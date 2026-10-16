#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPG TERMINAL - Save tipo GitHub (Markdown em .txt)
Funciona Windows (cmd/PowerShell) e Linux (bash/zsh)
Uso: python rpg_big.py  (ou python3 rpg_big.py)
"""
import os, sys, time, re

SAVE_FILE = "save_rpg.txt"

# ---------- Cross-platform ----------
def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausa(msg="Pressione ENTER..."):
    input(msg)

def digitar(texto, delay=0.025):
    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ---------- Estado ----------
class Jogador:
    def __init__(self, nome="Aventurer"):
        self.nome = nome
        self.vida = 100
        self.vida_max = 100
        self.atq = 15
        self.def_ = 5
        self.ouro = 0
        self.inven = {}
        # Mapa: salas visitadas (dict sala -> bool)
        self.salvas = {"Porto": False, "Floresta": False, "Castelo": False, "Caverna": False}
        self.sala_atual = "Porto"

    def adicionar_item(self, item, qty=1):
        self.inven[item] = self.inven.get(item, 0) + qty

# ---------- Save estilo GitHub ----------
def salvar(jogador):
    """Escreve save_rpg.txt com markdown (estilo GitHub)"""
    linhas = []
    linhas.append("# RPG Save - Jogador: {}".format(jogador.nome))
    linhas.append("")
    linhas.append("## 📊 Stats")
    linhas.append("")
    linhas.append("| Atributo | Valor |")
    linhas.append("|----------|-------|")
    linhas.append("| Vida     | {} / {} |".format(jogador.vida, jogador.vida_max))
    linhas.append("| Ataque   | {} |".format(jogador.atq))
    linhas.append("| Defesa   | {} |".format(jogador.def_))
    linhas.append("| Ouro     | {} 🪙 |".format(jogador.ouro))
    linhas.append("")
    linhas.append("## 🎒 Inventário")
    linhas.append("")
    if jogador.inven:
        for item, qt in sorted(jogador.inven.items()):
            linhas.append("- [x] {} (x{})".format(item, qt))
    else:
        linhas.append("_Vazio..._")
    linhas.append("")
    linhas.append("## 🗺️ Progresso / Mapa")
    linhas.append("")
    for sala, visitada in sorted(jogador.salvas.items()):
        status = "[x]" if visitada else "[ ]"
        linhas.append("- {} **{}**{}".format(status, sala, " 👑" if sala == "Castelo" else ""))
    linhas.append("")
    linhas.append("## 📍 Sala Atual")
    linhas.append(jogador.sala_atual)
    linhas.append("")
    linhas.append("---")
    linhas.append("*Arquivo gerado pelo RPG Terminal. Pode editar no VS Code / Notepad.*")
    
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    digitar("[💾 SAVE] Arquivo '{}' atualizado (formato GitHub/Markdown).".format(SAVE_FILE))

# ---------- Carregar ----------
def carregar(jogador):
    if not os.path.exists(SAVE_FILE):
        digitar("Não há save encontrado.")
        return False
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            texto = f.read()
        # Extrai nome
        m = re.search(r"# RPG Save - Jogador: (.+)", texto)
        if m:
            jogador.nome = m.group(1).strip()
        # Vida
        m = re.search(r"\| Vida \s*\| ([0-9]+) / ([0-9]+) \|", texto)
        if m:
            jogador.vida = int(m.group(1))
            jogador.vida_max = int(m.group(2))
        # Ataque
        m = re.search(r"\| Ataque \s*\| ([0-9]+) \|", texto)
        if m:
            jogador.atq = int(m.group(1))
        # Defesa
        m = re.search(r"\| Defesa \s*\| ([0-9]+) \|", texto)
        if m:
            jogador.def_ = int(m.group(1))
        # Ouro
        m = re.search(r"\| Ouro \s*\| ([0-9]+)", texto)
        if m:
            jogador.ouro = int(m.group(1))
        # Inventário
        for item_match in re.finditer(r"- \[x\] (.+?) \(x([0-9]+)\)", texto):
            item = item_match.group(1).strip()
            qt = int(item_match.group(2))
            jogador.inven[item] = qt
        # Progresso
        for sala_match in re.finditer(r"- \[([x ])\] \*\*(.+?)\*\*", texto):
            c = sala_match.group(1)
            sala = sala_match.group(2).strip()
            # Remove emoji do castelo se houver (simples)
            sala = sala.replace(" 👑", "").strip()
            if sala in jogador.salvas:
                jogador.salvas[sala] = (c == "x")
        # Sala atual
        m = re.search(r"## 📍 Sala Atual\n(.+?)\n", texto)
        if m:
            sala = m.group(1).strip()
            if sala in jogador.salvas:
                jogador.sala_atual = sala
        digitar("[📂 LOAD] Save '{}' carregado!".format(SAVE_FILE))
        return True
    except Exception as e:
        digitar("Erro ao carregar save: {}".format(e))
        return False

# ---------- Combate ----------
def combate(jogador, inimigo_nome, inimigo_vida, inimigo_atq):
    print(f"\n⚔️  COMBATE: {inimigo_nome}")
    vida_inimigo = inimigo_vida
    while vida_inimigo > 0 and jogador.vida > 0:
        print(f"Você: {jogador.vida} HP | Inimigo: {vida_inimigo} HP")
        print("Ações: [A]tacar  [D]efender  [C]urar (poção)  [I]nventário")
        acao = input("Escolha: ").strip().upper()
        if acao == "A":
            dano = max(1, jogador.atq - 2)
            vida_inimigo -= dano
            print(f"Você golpeia o {inimigo_nome} causando {dano} de dano!")
            # Revidada
            dano_rec = max(0, inimigo_atq - jogador.def_)
            jogador.vida -= dano_rec
            print(f"{inimigo_nome} revida com {dano_rec} de dano!")
        elif acao == "D":
            jogador.def_ += 5
            print("Você assume postura defensiva (+5 defesa nesta rodada)!")
            dano_rec = max(0, inimigo_atq - (jogador.def_ + 5))
            jogador.vida -= dano_rec
            print(f"{inimigo_nome} bate causando {dano_rec} de dano (bloqueado)!")
        elif acao == "C":
            if jogador.inven.get("Poção de Vida", 0) > 0:
                curar = 20
                jogador.vida = min(jogador.vida_max, jogador.vida + curar)
                jogador.inven["Poção de Vida"] -= 1
                if jogador.inven["Poção de Vida"] == 0:
                    del jogador.inven["Poção de Vida"]
                print(f"Você bebe uma poção e recupera {curar} HP!")
            else:
                print("Não tem poções!")
        elif acao == "I":
            mostrar_inventario(jogador)
            continue
        else:
            print("Ação inválida.")
        # Envolve turno se ainda há vida
        if vida_inimigo <= 0:
            break
    if jogador.vida <= 0:
        print("Você caiu... GAME OVER.")
        pausa()
        return False
    else:
        print(f"Você venceu! {inimigo_nome} derrotado.")
        jogador.ouro += 10
        return True

# ---------- Inventário ----------
def mostrar_inventario(jogador):
    limpar()
    digitar("=== INVENTÁRIO ===")
    if not jogador.inven:
        print("Vazio.")
    else:
        for item, qt in sorted(jogador.inven.items()):
            print("- {} x{}".format(item, qt))
    digitar(f"Ouro: {jogador.ouro} | Vida: {jogador.vida}/{jogador.vida_max}")
    pausa()

# ---------- Menu / Cenas ----------
def cena_porto(jogador):
    limpar()
    digitar("=== PORTO ===")
    digitar("Cidade de pescadores. O ar é salgado. Há uma taverna e uma estrada.")
    print("[1] Falar com o pescador (recebe poção)\n[2] Ir para a Floresta Sombria\n[3] Ir para o Castelo (exige chave)\n[4] Salvar / Voltar ao menu")
    escolha = input("Escolha: ").strip()
    if escolha == "1":
        jogador.adicionar_item("Poção de Vida", 1)
        digitar("O pescador te dá uma Poção de Vida!")
        pausa()
    elif escolha == "2":
        jogar.cenario_floresta(jogador)
    elif escolha == "3":
        if jogador.inven.get("Chave do Castelo", 0) > 0:
            jogar.cenario_castelo(jogador)
        else:
            digitar("A porta está trancada. Precisa da Chave do Castelo.")
            pausa()
    elif escolha == "4":
        salvar(jogador)
        pausa()

def cena_floresta(jogador):
    jogador.salvas["Floresta"] = True
    limpar()
    digitar("=== FLORESTA SOMBRIA ===")
    digitar("Árvores altas bloqueiam o sol. Você ouve uivos.")
    print("[1] Explorar (encontrar item)\n[2] Combater Goblin\n[3] Voltar ao Porto")
    escolha = input("Escolha: ").strip()
    if escolha == "1":
        item = "Espada de Ferro" if not jogador.inven.get("Espada de Ferro") else "Poção de Vida"
        jogador.adicionar_item(item, 1)
        jogador.atq += 5 if item == "Espada de Ferro" else 0
        digitar(f"Você encontrou: {item}!")
        if item == "Espada de Ferro":
            digitar("Ataque aumentado!")
        pausa()
    elif escolha == "2":
        ok = combate(jogador, "Goblin", 30, 8)
        if ok:
            jogador.adicionar_item("Chave do Castelo", 1)
            digitar("O Goblin dropou uma Chave do Castelo!")
            pausa()
    elif escolha == "3":
        pass
    # Atualiza sala atual
    jogador.sala_atual = "Porto"

def cena_castelo(jogador):
    jogador.salvas["Castelo"] = True
    limpar()
    digitar("=== CASTELO DO REI ===")
    digitar("Salas de pedra. No trono, uma armadura brilhante.")
    print("[1] Pegar Armadura de Ouro (+def)\n[2] Combater o Guardião\n[3] Voltar")
    escolha = input("Escolha: ").strip()
    if escolha == "1":
        jogador.def_ += 10
        digitar("Você veste a Armadura de Ouro! Defesa +10.")
        pausa()
    elif escolha == "2":
        ok = combate(jogador, "Guardião do Rei", 60, 12)
        if ok:
            digitar("O rei agradece! Você ganha 50 ouro.")
            jogador.ouro += 50
            joga.cenario_caverna(jogador)  # Desbloqueia caverna
            pausa()
    elif escolha == "3":
        pass
    jogador.sala_atual = "Porto"

def cena_caverna(jogador):
    jogador.salvas["Caverna"] = True
    limpar()
    digitar("=== CAVERNA DO DRAGÃO ===")
    digitar("Calor intenso. Um dragão dorme sobre ouro.")
    ok = combate(jogador, "Dragão Antigo", 150, 20)
    if ok:
        digitar("VOCÊ DERROTou O DRAGÃO! O reino está salvo!")
        jogador.ouro += 200
        digitar("Vitória Legendaría!")
        # Final: salva
        salvar(jogador)
        pausa()

# ---------- Main ----------
class GameLoop:
    def __init__(self):
        pass

    def cenario_floresta(self, j):
        cena_floresta(j)

    def cenario_castelo(self, j):
        cena_castelo(j)

    def cenario_caverna(self, j):
        cena_caverna(j)

game = GameLoop()
jogar = game  # alias para usar jogar.cenario_... dentro das funções (hack simples)

def menu_principal():
    # Inicializa jogador
    nome_input = input("Seu nome de aventureiro: ").strip() or "Aventurer"
    j = Jogador(nome_input)
    # Tenta carregar
    if os.path.exists(SAVE_FILE):
        resp = input("Save encontrado. Carregar? (S/N): ").strip().upper()
        if resp == "S":
            carregar(j)
    
    while True:
        limpar()
        digitar("=== MENU RPG ===")
        digitar(f"Jogador: {j.nome} | Sala: {j.sala_atual} | Vida: {j.vida}/{j.vida_max}")
        print("[1] Explorar Porto / Mundo\n[2] Inventário\n[3] Salvar Jogo\n[4] Carregar Save\n[5] Sair")
        op = input("Opção: ").strip()
        if op == "1":
            # Se ainda não visitou floresta, começa pelo porto; senão permite ir diretamente?
            # Simples: sempre volta ao porto para escolha
            j.sala_atual = "Porto"
            cena_porto(j)
        elif op == "2":
            mostrar_inventario(j)
        elif op == "3":
            salvar(j)
            pausa()
        elif op == "4":
            carregar(j)
            pausa()
        elif op == "5":
            digitar("Até a próxima aventura!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\nJogo encerrado pelo usuário.")
