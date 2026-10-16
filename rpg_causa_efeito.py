#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPG CAUSA & CONSEQUÊNCIA
- Classes de personagem (Guerreiro, Mago, Arqueiro)
- Missões com impacto posterior
- Consequências: ações passadas bloqueiam/liberam caminhos futuros
- Save estilo GitHub (.txt Markdown) + salvamento automático
- Inventário visual (tabela no terminal)
- Funciona Windows/Linux sem dependências
"""
import os, sys, time, re, random

SAVE_MANUAL = "save_rpg.txt"
SAVE_AUTO = "save_auto_rpg.txt"

# ---------- Cross-platform ----------
def limpar():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except:
        pass

def pausa(msg="Pressione ENTER..."):
    input(msg)

def digitar(texto, delay=0.015):
    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ---------- Jogador ----------
class Jogador:
    def __init__(self, nome="Aventurer", classe="Guerreiro"):
        self.nome = nome
        self.classe = classe
        self.flags = {
            "pescador_falado": False,
            "goblin_derrotado": False,
            "crista_pegada": False,
            "portao_aberto": False,
            "manuscrito_lido": False,
            "dragao_derrotado": False,
        }
        self.missao_ativa = None  # ex: "O Mar Escuro"
        self.missao_concluida = False
        self.inven = {}
        self.ouro = 0
        # Stats base por classe
        if classe == "Guerreiro":
            self.vida = 120; self.vida_max = 120; self.atq = 20; self.def_ = 10
        elif classe == "Mago":
            self.vida = 80; self.vida_max = 80; self.atq = 25; self.def_ = 2
        else:  # Arqueiro
            self.vida = 100; self.vida_max = 100; self.atq = 18; self.def_ = 6
        self.sala_atual = "Porto"
        # Inventário inicial por classe
        if classe == "Guerreiro":
            self.adicionar_item("Poção de Vida", 1)
        elif classe == "Mago":
            self.adicionar_item("Poção de Vida", 2)
        else:
            self.adicionar_item("Poção de Vida", 1)
            self.ouro += 10

    def adicionar_item(self, item, qt=1):
        self.inven[item] = self.inven.get(item, 0) + qt

    def usar_poção(self):
        if self.inven.get("Poção de Vida", 0) > 0:
            self.inven["Poção de Vida"] -= 1
            if self.inven["Poção de Vida"] == 0:
                del self.inven["Poção de Vida"]
            self.vida = min(self.vida_max, self.vida + 25)
            return True
        return False

# ---------- Inventário Visual (tabela estilo GitHub) ----------
def mostrar_inventario(jogador):
    limpar()
    digitar("=== 🎒 INVENTÁRIO ===")
    digitar(f"Classe: {jogador.classe} | Nome: {jogador.nome}")
    digitar(f"Ouro: {jogador.ouro} 🪙  |  Vida: {jogador.vida}/{jogador.vida_max}")
    digitar(f"Missão: {jogador.missao_ativa or 'Nenhuma'}")
    print()
    # Tabela markdown simples no terminal
    print("| Item               | Qtd |")
    print("|--------------------|-----|")
    if jogador.inven:
        for item, qt in sorted(jogador.inven.items()):
            print(f"| {item:<18} | {qt} |")
    else:
        print("| _Vazio_            | - |")
    print()
    # Flags visíveis (causa/consequência)
    digitar("=== 🏁 FLAGS (Causa/Efeito) ===")
    for k, v in sorted(jogador.flags.items()):
        status = "✅" if v else "❌"
        nome = k.replace("_", " ").title()
        print(f"{status} {nome}")
    pausa()

# ---------- Sistema de Missão ----------
def atualizar_missao(jogador, evento):
    # Eventos de consequência
    if evento == "pescador_ok":
        jogador.flags["pescador_falado"] = True
        jogador.missao_ativa = "O Mar Escuro"
        jogador.adicionar_item("Manuscrito Antigo", 1)
        digitar("[📜 MISSÃO ATIVADA] 'O Mar Escuro'. Leia o manuscrito quando quiser.")
    elif evento == "goblin_ok":
        jogador.flags["goblin_derrotado"] = True
        jogador.flags["crista_pegada"] = True
        jogador.adicionar_item("Crista Azul", 1)
    elif evento == "manuscrito_lido":
        jogador.flags["manuscrito_lido"] = True
        jogador.atq += 5
        digitar("[📖 CONSEQUÊNCIA] Você entende a língua do Guardião. Ataque +5.")
    elif evento == "dragao_ok":
        jogador.flags["dragao_derrotado"] = True
        jogador.missao_concluida = True
        jogador.ouro += 200
        digitar("[👑 MISSÃO CONCLUÍDA] O reino está salvo!")

# ---------- Combate ----------
def combate(jogador, nome, vida_inimigo, atq_inimigo):
    v_inim = vida_inimigo
    turnos = 0
    while v_inim > 0 and jogador.vida > 0:
        turnos += 1
        limpar()
        digitar(f"⚔️  COMBATE: {nome}")
        digitar(f"Você: {jogador.vida} HP | Inimigo: {v_inim} HP")
        digitar(f"Turno: {turnos} | Classe: {jogador.classe}")
        print("[A]tacar  [D]efender  [C]urar (poção)  [I]nventário  [F]ugir")
        acao = input("Ação: ").strip().upper()
        if acao == "A":
            dano = max(3, jogador.atq - 2)
            v_inim -= dano
            # Revidada
            rec = max(0, atq_inimigo - jogador.def_)
            if turnos == 1:
                # Primeira revidada do Goblin pode ser mais forte se não leu manuscrito
                pass
            jogador.vida -= rec
            digitar(f"Você causa {dano} de dano! Inimigo revida {rec}.")
        elif acao == "D":
            jogador.def_ += 8
            rec = max(0, atq_inimigo - (jogador.def_))
            jogador.vida -= rec
            digitar(f"Defesa reforçada! Sofre {rec} de dano.")
        elif acao == "C":
            if jogador.usar_poção():
                digitar("Você bebe uma poção (+25 HP)!")
            else:
                digitar("Sem poções!")
        elif acao == "I":
            mostrar_inventario(jogador)
            continue
        elif acao == "F":
            digitar("Você foge! Mas pode perder oportunidades.")
            # Se fugir do Goblin, não ganha Crista (consequência)
            if nome == "Goblin":
                digitar("[⚠️ CONSEQUÊNCIA] O Goblin fugiu com a Crista. Você não poderá abrir o portão do Castelo sem ela.")
            return False  # falhou/combatido incompleto
        else:
            digitar("Ação inválida.")
        pausa()
    if jogador.vida <= 0:
        digitar("Você caiu... GAME OVER.")
        pausa()
        return False
    else:
        digitar(f"Vitória! Você derrotou {nome}.")
        return True

# ---------- Salvar / Carregar (Markdown GitHub) ----------
def salvar_completo(jogador, arquivo=SAVE_MANUAL, auto=False):
    titulo = f"# RPG Save - Jogador: {jogador.nome}"
    if auto:
        titulo += " (AUTO)"
    linhas = [titulo, ""]
    linhas.append("## 📊 Stats")
    linhas.append("")
    linhas.append("| Atributo | Valor |")
    linhas.append("|----------|-------|")
    linhas.append(f"| Nome     | {jogador.nome} |")
    linhas.append(f"| Classe   | {jogador.classe} |")
    linhas.append(f"| Vida     | {jogador.vida} / {jogador.vida_max} |")
    linhas.append(f"| Ataque   | {jogador.atq} |")
    linhas.append(f"| Defesa   | {jogador.def_} |")
    linhas.append(f"| Ouro     | {jogador.ouro} 🪙 |")
    linhas.append("")
    linhas.append("## 🏁 Missão")
    linhas.append(f"- Ativa: `{jogador.missao_ativa or 'Nenhuma'}`")
    linhas.append(f"- Concluída: {'✅' if jogador.missao_concluida else '❌'}")
    linhas.append("")
    linhas.append("## 🎒 Inventário")
    if jogador.inven:
        for item, qt in sorted(jogador.inven.items()):
            linhas.append(f"- [x] {item} (x{qt})")
    else:
        linhas.append("_Vazio..._")
    linhas.append("")
    linhas.append("## 🏁 Flags (Causa & Consequência)")
    for k, v in sorted(jogador.flags.items()):
        linhas.append(f"- [{'x' if v else ' '}] `{k}`")
    linhas.append("")
    linhas.append("## 🗺️ Progresso / Sala Atual")
    linhas.append(jogador.sala_atual)
    linhas.append("")
    linhas.append("---")
    linhas.append("*Arquivo gerado pelo RPG Causa & Consequência. Pode editar no VS Code / Notepad.*")
    
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    digitar(f"[💾 SAVE] '{arquivo}' atualizado (estilo GitHub/Markdown).")

def carregar_completo(jogador, arquivo=SAVE_MANUAL):
    if not os.path.exists(arquivo):
        return False
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            texto = f.read()
        # Nome
        m = re.search(r"# RPG Save - Jogador: (.+?)(?: \(AUTO\))?", texto)
        if m:
            jogador.nome = m.group(1).strip()
        # Classe
        m = re.search(r"\| Classe\s*\| (.+?) \|", texto)
        if m:
            jogador.classe = m.group(1).strip()
        # Stats básicos
        m = re.search(r"\| Vida\s*\| ([0-9]+) / ([0-9]+) \|", texto)
        if m:
            jogador.vida = int(m.group(1)); jogador.vida_max = int(m.group(2))
        m = re.search(r"\| Ataque\s*\| ([0-9]+) \|", texto)
        if m: jogador.atq = int(m.group(1))
        m = re.search(r"\| Defesa\s*\| ([0-9]+) \|", texto)
        if m: jogador.def_ = int(m.group(1))
        m = re.search(r"\| Ouro\s*\| ([0-9]+)", texto)
        if m: jogador.ouro = int(m.group(1))
        # Inventário
        jogador.inven = {}
        for item_match in re.finditer(r"- \[x\] (.+?) \(x([0-9]+)\)", texto):
            jogador.inven[item_match.group(1).strip()] = int(item_match.group(2))
        # Missão
        m = re.search(r"- Ativa: `(.+?)`", texto)
        if m: jogador.missao_ativa = m.group(1).strip() if m.group(1).strip() != "Nenhuma" else None
        m = re.search(r"- Concluída: (✅|❌)", texto)
        if m: jogador.missao_concluida = (m.group(1) == "✅")
        # Flags
        for flag_match in re.finditer(r"- \[([x ])\] `(.+?)`", texto):
            k = flag_match.group(2).strip()
            v = (flag_match.group(1) == "x")
            if k in jogador.flags:
                jogador.flags[k] = v
        # Sala atual
        m = re.search(r"## 🗺️ Progresso / Sala Atual\n(.+?)\n", texto)
        if m: jogador.sala_atual = m.group(1).strip()
        digitar(f"[📂 LOAD] '{arquivo}' carregado!")
        return True
    except Exception as e:
        digitar(f"Erro no load: {e}")
        return False

# ---------- Cenas (Causa & Consequência) ----------

def cena_porto(jogador):
    limpar()
    digitar("=== PORTO ===")
    digitar("Cidade de pescadores. O ar é salgado.")
    if jogador.flags["pescador_falado"]:
        digitar("Você já falou com o pescador. Ele te aponta para o caminho do mar.")
        opcoes = ["1) Seguir missão (O Mar Escuro)", "2) Explorar Floresta", "3) Salvar / Menu", "4) Inventário"]
    else:
        digitar("Há um pescador sentado perto do cais.")
        opcoes = ["1) Falar com o pescador", "2) Ignorar e ir para Floresta", "3) Salvar / Menu", "4) Inventário"]
    
    for o in opcoes:
        print(o)
    escolha = input("Escolha: ").strip()
    
    if escolha == "1" and not jogador.flags["pescador_falado"]:
        digitar("O pescador diz: 'O mar está escuro. Há uma maldição. Encontre o manuscrito no cais.'")
        atualizar_missao(jogador, "pescador_ok")
        jogador.adicionar_item("Chave do Castelo", 1)  # Consequência: sem falar, não tem chave
        pausa()
        # Se já falou, opção 1 é seguir missão (vai para floresta direto com missão ativa)
    elif escolha == "1" and jogador.flags["pescador_falado"]:
        digitar("Você segue a missão: 'O Mar Escuro'. Vá à Floresta Sombria.")
        jogador.sala_atual = "Floresta"
        cena_floresta(jogador)
        return
    elif escolha == "2" and not jogador.flags["pescador_falado"]:
        digitar("Você ignora o pescador e segue em frente...")
        jogador.sala_atual = "Floresta"
        cena_floresta(jogador)
        return
    elif escolha == "2" and jogador.flags["pescador_falado"]:
        jogador.sala_atual = "Floresta"
        cena_floresta(jogador)
        return
    elif escolha == "3":
        salvar_completo(jogador)
        # Auto save
        salvar_completo(jogador, SAVE_AUTO, auto=True)
        pausa()
    elif escolha == "4":
        mostrar_inventario(jogador)

    # Se terminou a cena sem ir para floresta, volta ao porto (fica no porto)
    jogador.sala_atual = "Porto"

def cena_floresta(jogador):
    jogador.flags["goblin_derrotado"] = False  # permite tentar de novo, mas se já fez, não ganha novamente
    # Se já derrotou e pegou Crista, não precisa repetir
    # Se já tem Crista, pula combate (consequência: já resolveu)
    if jogador.flags["crista_pegada"]:
        limpar()
        digitar("=== FLORESTA SOMBRIA ===")
        digitar("Você já encontrou a Crista Azul aqui anteriormente.")
        digitar("O caminho está limpo agora.")
        print("[1] Voltar ao Porto\n[2] Ir ao Castelo (se tiver chave)")
        es = input("Escolha: ").strip()
        if es == "2":
            if jogador.inven.get("Chave do Castelo", 0) > 0:
                jogador.sala_atual = "Castelo"
                cena_castelo(jogador)
            else:
                digitar("Precisa da Chave do Castelo. Ela está no Goblin (já derrotado? verifique).")
                pausa()
        jogador.sala_atual = "Porto"
        return
    
    # Se ainda não resolveu Goblin
    limpar()
    digitar("=== FLORESTA SOMBRIA ===")
    if jogador.missao_ativa == "O Mar Escuro":
        digitar("[📜 MISSÃO ATIVA] 'O Mar Escuro'. Você sente uma presença sombria.")
    else:
        digitar("Árvores altas bloqueiam o sol. Você ouve uivos.")
    
    # Se não tem missão, ainda pode luta (não ganha Crista se não tiver missão? Podemos deixar sempre ganhar, mas se fugiu é consequência)
    # Vamos deixar: se derrotar, ganha Crista se tiver missão; se não tiver missão, ganha apenas item básico.
    # Mas para consequência forte: se fugir do Goblin, nunca ganha Crista (flag fica false permanentemente)
    print("[1] Combater Goblin\n[2] Tentar fugir (consequência!)\n[3] Voltar")
    es = input("Escolha: ").strip()
    
    if es == "1":
        ok = combate(jogador, "Goblin Sombrio", 40, 10)
        if ok:
            jogador.flags["goblin_derrotado"] = True
            jogador.flags["crista_pegada"] = True
            jogador.adicionar_item("Crista Azul", 1)
            # Se missão ativa, atualiza (já está ativa, ganhe progresso)
            digitar("[💎 CONSEQUÊNCIA] Você encontrou a Crista Azul! Com ela, poderá abrir o portão do Castelo.")
            # Se não tinha missão ainda, não ativa; apenas item.
            pausa()
    elif es == "2":
        digitar("Você foge... Mas o Goblin leva a Crista.")
        digitar("[⚠️ CONSEQUÊNCIA PERMANENTE] Sem a Crista Azul, você NÃO poderá abrir o portão do Castelo (mesmo com a chave).")
        # Não muda flags de goblin_derrotado (permanece false), não ganha Crista
        pausa()
    elif es == "3":
        pass
    
    jogador.sala_atual = "Porto"

def cena_castelo(jogador):
    # Consequência: precisa da Chave do Castelo e da Crista Azul (se missao ativa ou se quer entrar completamente)
    # Se não tem Crista e missao ativa, o portão está trancado
    limpar()
    digitar("=== CASTELO DO REI ===")
    digitar("Portas de pedra. Há um portão de ferro.")
    
    # Verifica condições
    tem_chave = jogador.inven.get("Chave do Castelo", 0) > 0
    tem_crista = jogador.flags["crista_pegada"]
    
    if tem_chave and tem_crista:
        digitar("Você tem a Chave e a Crista Azul. O portão se abre!")
    elif tem_chave and not tem_crista:
        digitar("[❌ BLOQUEADO] Você tem a chave, mas falta a Crista Azul. O portão não se abre (consequência de não derrotar o Goblin).")
    elif not tem_chave and tem_crista:
        digitar("Você tem a Crista, mas não a Chave do Castelo.")
    else:
        digitar("Você não tem nem Chave nem Crista.")
    
    # Se conseguiu entrar (tem chave + crista)
    if tem_chave and tem_crista:
        print("[1] Entrar no Salão do Rei (batalha)\n[2] Ler Manuscrito (se tiver)\n[3] Voltar")
        es = input("Escolha: ").strip()
        if es == "1":
            ok = combate(jogador, "Guardião Real", 60, 12)
            if ok:
                jogador.flags["portao_aberto"] = True
                jogador.adicionar_item("Armadura de Ouro", 1)
                jogador.def_ += 10
                digitar("[👑 CONSEQUÊNCIA] O Rei te dá uma Armadura de Ouro e abre a caverna.")
                # Se ainda não tem missão do dragão, pode ativar agora (se pescador falado)
                if jogador.flags["pescador_falado"] and not jogador.flags["dragao_derrotado"]:
                    jogador.missao_ativa = "O Mar Escuro"
                    digitar("O Rei menciona o Dragão: 'Vá à Caverna, se você for digno.'")
                pausa()
        elif es == "2" and jogador.inven.get("Manuscrito Antigo", 0) > 0:
            jogador.flags["manuscrito_lido"] = True
            jogador.atq += 5
            # Pode usar informação para subornar Guardião sem combate? Vamos permitir como alternativa no combate, mas aqui já entrou.
            digitar("Você lê o manuscrito. Entende a língua antiga.")
            pausa()
        elif es == "3":
            pass
    else:
        # Não entra
        print("[1] Voltar ao Porto")
        es = input("Escolha: ").strip()
    
    jogador.sala_atual = "Porto"

def cena_caverna(jogador):
    # Consequência: só pode entrar se portao_aberto == True (ou se missao ativa e guardião derrotado)
    # Se tentou entrar sem portao_aberto, dragão é invencível (consequência)
    limpar()
    digitar("=== CAVERNA DO DRAGÃO ===")
    
    # Verifica acesso
    if not jogador.flags["portao_aberto"]:
        # Se ainda não resolveu o Castelo, não entra (ou entra mas é impossível)
        if jogador.missao_ativa == "O Mar Escuro":
            digitar("A neblina bloqueia a entrada. Sem passar pelo Castelo, você não pode acessar a Caverna.")
            digitar("[⚠️ CONSEQUÊNCIA] A missão 'O Mar Escuro' exige que você complete o Castelo primeiro.")
        else:
            digitar("A caverna está bloqueada por uma barreira mágica. Volte quando o reino estiver preparado.")
        pausa()
        jogador.sala_atual = "Porto"
        return
    
    # Se entrou legalmente
    if jogador.flags["dragao_derrotado"]:
        digitar("A caverna está vazia. O Dragão foi derrotado anteriormente.")
        pausa()
        jogador.sala_atual = "Porto"
        return
    
    digitar("Calor intenso. Um dragão dorme sobre ouro infinito.")
    if jogador.missao_ativa == "O Mar Escuro":
        digitar("[📜 MISSÃO] 'O Mar Escuro' — Derrote o Dragão.")
    
    print("[1] Combater Dragão\n[2] Voltar")
    es = input("Escolha: ").strip()
    if es == "1":
        # Se leu manuscrito, pode usar frase secreta para reduzir dano? Vamos fazer: se manuscrito_lido, combate é mais fácil (atq +5 já aplicado, mas vamos dar bônus de defesa +10 no combate)
        if jogador.flags["manuscrito_lido"]:
            digitar("[📖 CONSEQUÊNCIA] Você usa a frase do Manuscrito! O Dragão hesita.")
            jogador.def_ += 5  # bônus temporário
        ok = combate(jogador, "Dragão Antigo", 120, 20)
        if ok:
            atualizar_missao(jogador, "dragao_ok")
            jogador.adicionar_item("Ouro do Dragão", 1)
            digitar("Você é a lenda do reino!")
            pausa()
    elif es == "2":
        pass
    jogador.sala_atual = "Porto"

# ---------- Menu Principal ----------
def criar_personagem():
    digitar("=== CRIAR PERSONAGEM ===")
    nome = input("Seu nome: ").strip() or "Aventurer"
    print("Classes:")
    print("[G] Guerreiro (vida alta, defesa forte)")
    print("[M] Mago (ataque alto, vida baixa)")
    print("[A] Arqueiro (equilibrado, ouro inicial +10)")
    c = input("Classe: ").strip().upper()
    if c == "M":
        classe = "Mago"
    elif c == "A":
        classe = "Arqueiro"
    else:
        classe = "Guerreiro"
    digitar(f"Classe escolhida: {classe}")
    return Jogador(nome, classe)

def menu_principal():
    # Pergunta se quer carregar
    j = None
    if os.path.exists(SAVE_MANUAL) or os.path.exists(SAVE_AUTO):
        resp = input("Há saves encontrados. Deseja carregar manual (M) ou automático (A) ou criar novo (N)? ").strip().upper()
        if resp == "M" and os.path.exists(SAVE_MANUAL):
            j = Jogador("Temp")
            carregar_completo(j, SAVE_MANUAL)
        elif resp == "A" and os.path.exists(SAVE_AUTO):
            j = Jogador("Temp")
            carregar_completo(j, SAVE_AUTO)
    if j is None:
        j = criar_personagem()
    
    while True:
        limpar()
        digitar("=== RPG CAUSA & CONSEQUÊNCIA ===")
        digitar(f"Jogador: {j.nome} | Classe: {j.classe}")
        digitar(f"Sala: {j.sala_atual} | Vida: {j.vida}/{j.vida_max} | Ouro: {j.ouro}")
        digitar(f"Missão: {j.missao_ativa or 'Nenhuma'} | Concluída: {'✅' if j.missao_concluida else '❌'}")
        print()
        print("[1] Explorar Mundo (Porto / Salas)")
        print("[2] Inventário (visual + flags)")
        print("[3] Salvar Manual")
        print("[4] Salvar Automático")
        print("[5] Carregar Save")
        print("[6] Sair")
        op = input("Opção: ").strip()
        if op == "1":
            j.sala_atual = "Porto"
            cena_porto(j)
        elif op == "2":
            mostrar_inventario(j)
        elif op == "3":
            salvar_completo(j, SAVE_MANUAL)
            pausa()
        elif op == "4":
            salvar_completo(j, SAVE_AUTO, auto=True)
            pausa()
        elif op == "5":
            resp = input("Manual (M) ou Auto (A) ou Voltar (V)? ").strip().upper()
            if resp == "M":
                temp = Jogador("Temp")
                if carregar_completo(temp, SAVE_MANUAL):
                    j = temp
            elif resp == "A":
                temp = Jogador("Temp")
                if carregar_completo(temp, SAVE_AUTO):
                    j = temp
            pausa()
        elif op == "6":
            # Auto-save ao sair
            salvar_completo(j, SAVE_AUTO, auto=True)
            digitar("Salvo automático criado. Até a próxima!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\nJogo encerrado.")
