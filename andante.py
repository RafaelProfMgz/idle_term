#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPG IDLE + ANDARES + MAGIA + MAPEAMENTO ASCII + AUTO PLAY
- Andares (1-5) com chefes e requisitos
- Auto Play: joga sozinho enquanto você não está (farm, XP, itens, eventos aleatórios)
- Magia D&D-like simples (Mana = Int*10, feitiços: Bola de Fogo, Cura, Escudo, Impulso)
- Mapa ASCII maior (torre vertical de andares)
- Save .txt estilo GitHub (editável)
"""
import os, sys, time, re, random

# ---------- Interface Visual (ASCII + zsh + Cores) ----------
# Import auxiliar de cores (pode ser usado diretamente)
BR = "\033[1m"; RD = "\033[31m"; GN = "\033[32m"; YW = "\033[33m"
BL = "\033[34m"; MG = "\033[35m"; CY = "\033[36m"; WT = "\033[37m"
RESET = "\033[0m"; DIM = "\033[2m"; BOLD = "\033[1m"

def logo_ascii():
    return (f"{YW}{BOLD}"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║  ✦  ANDANTE RPG   —   A V E N T U R A  ✦  ║\n"
        "╚══════════════════════════════════════════════════════════════╝"
        f"{RESET}")

def borda_titulo(titulo, cor=YW):
    largura = len(titulo) + 4
    return (f"{cor}{BOLD}╔{'═'*(largura-2)}╗\n"
            f"║  {titulo}  ║\n"
            f"╚{'═'*(largura-2)}╝{RESET}")

def linha_sep(cor=CY):
    return f"{cor}─" * 58 + f"{RESET}"

def destaque(texto, cor=YW):
    return f"{cor}{BOLD}{texto}{RESET}"

def stick_luta(jogador_nome="You", inimigo="Goblin"):
    # Palito compacto — apenas 2 linhas
    return (f"{YW} O  ⚔  O  {RESET}\n"
            f"{YW} \\  ✦  /  {RESET}")

def animar_batalha(jogador, inimigo_nome="Goblin", delay=0.8):
    # Slider lateral lento — desliza de lado sem limpar a tela
    simbolo = f"{YW}⚔{RESET}"
    # Faz 12 passos limitados para não travar
    for pos in range(0, 60, 5):
        sys.stdout.write(f"\r{' '*pos}{simbolo}  {dim_texto('Combate — '+inimigo_nome)}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"\r{' '*55}✓  {dim_texto('Luta completa!')}")
    sys.stdout.flush()
    time.sleep(delay)
    sys.stdout.write("\n")

def dim_texto(t):
    return f"{DIM}{t}{RESET}"

def renderizar_personagem(jogador):
    # Renderiza o personagem em ASCII conforme classe + equipamento
    # Cabeça
    cabeca = "O"
    if jogador.inven.get("Crista Azul", 0) > 0:
        cabeca = f"{CY}◈{RESET}"  # coroa azul
    elif jogador.inven.get("Crista do Goblin", 0) > 0:
        cabeca = f"{YW}✦{RESET}"  # coroa dourada
    # Corpo
    corpo = f"{YW}|{RESET}"
    if jogador.inven.get("Armadura de Ouro", 0) > 0:
        corpo = f"{YW}█{RESET}"  # armadura
    # Braços
    braco_esq = f"{YW}\\{RESET}"
    braco_dir = f"{YW}/{RESET}"
    # Equipamentos nas mãos
    espada = ""
    arco = ""
    cajado = ""
    if jogador.inven.get("Espada de Ferro", 0) > 0 or jogador.inven.get("Crista Azul", 0) > 0:
        espada = f"{YW}⚔{RESET}"
    if jogador.inven.get("Manuscrito Antigo", 0) > 0:
        cajado = f"{CY}§{RESET}"
    if jogador.inven.get("Ouro do Dragão", 0) > 0:
        arco = f"{GN}~{RESET}"
    # Classe visual
    if jogador.classe == "Guerreiro":
        braco_esq = f"{YW}\\{RESET}"; braco_dir = f"{YW}/{RESET}"; espada = f"{YW}⚔{RESET}"
    elif jogador.classe == "Mago":
        braco_esq = f"{CY}\\{RESET}"; braco_dir = f"{CY}/{RESET}"; cajado = f"{CY}§{RESET}"
    elif jogador.classe == "Arqueiro":
        braco_esq = f"{GN}\\{RESET}"; braco_dir = f"{GN}/{RESET}"; arco = f"{GN}~{RESET}"
    # Montar figura — máximo 2 linhas
    linha_braco = f"{braco_esq}  {espada}{arco}{cajado}  {braco_dir}" if (espada or arco or cajado) else f"{braco_esq}  {braco_dir}"
    return (f"{YW}{BOLD}  {cabeca}  {corpo} {linha_braco}{RESET}\n")

def info_box(titulo, linhas_dict, cor=BL):
    # linhas_dict = {label: value}
    print(f"{cor}{BOLD}┌─ {titulo} {'─'*(50-len(titulo))}┐{RESET}")
    for k, v in linhas_dict.items():
        print(f"{cor}│ {k:<20} {v:>20} │{RESET}")
    print(f"{cor}{BOLD}└{'─'*58}┘{RESET}")

SAVE_MANUAL = "save_idle.txt"
SAVE_AUTO = "save_auto_idle.txt"

# ---------- AI / Auto Play ----------
EVENTOS_AUTO = [
    ("Batalha", 0.4, "Goblin"),
    ("Item", 0.2, "Poção de Vida"),
    ("Ouro", 0.2, "10"),
    ("Diálogo", 0.1, "Pescador"),
    ("Trabalho", 0.1, "Force"),
]

def limpar():
    try: os.system('cls' if os.name == 'nt' else 'clear')
    except: pass

def pausa(msg="Pressione ENTER..."):
    input(msg)

def digitar(texto, delay=0.012):
    for ch in texto:
        sys.stdout.write(ch); sys.stdout.flush()
        time.sleep(delay)
    print()

def auto_play(jogador, passos=25, ate_chefe=False, infinito=False):
    """Simula o jogador no andar atual, ganhando XP, itens, eventos aleatórios."""
    modo = "INFINITO (pare quando quiser)" if infinito else ("ATÉ CHEFE" if ate_chefe else f"{passos} passos")
    digitar(f"[🤖 AUTO PLAY] Iniciando sessão no Andar {jogador.andar} — Modo: {modo}")
    res = {"batalhas":0,"itens":0,"ouro_ganho":0,"xp_ganho":0,"eventos":0,"morte":False,"chefe_tentado":False,"parou_chefe":False}
    i = 0
    while True:
        if jogador.vida <= 0:
            res["morte"] = True
            break
        # Escolhe evento
        eventos = EVENTOS_AUTO
        pesos = [e[1] for e in eventos]
        escolha = random.choices(eventos, weights=pesos, k=1)[0]
        tipo, _, obj = escolha
        # Executa evento simuladamente
        if tipo == "Batalha":
            animar_batalha(jogador, obj, delay=1.2)
            dano = random.randint(0, 8)
            jogador.vida -= dano
            jogador.ganhar_xp(random.randint(10, 25))
            jogador.ouro += random.randint(5, 15)
            res["batalhas"] += 1
            res["xp_ganho"] += 10
        elif tipo == "Item":
            item = random.choice(["Poção de Vida","Crista Azul","Manuscrito Antigo","Chave do Castelo"])
            jogador.adicionar_item(item, 1)
            res["itens"] += 1
        elif tipo == "Ouro":
            qt = int(obj)
            jogador.ouro += qt
            res["ouro_ganho"] += qt
        elif tipo == "Diálogo":
            res["eventos"] += 1
            if obj == "Pescador" and not jogador.flags.get("pescador_falado"):
                jogador.flags["pescador_falado"] = True
                jogador.missao_ativa = "O Mar Escuro"
        elif tipo == "Trabalho":
            jogador.ganhar_xp(random.randint(5, 15))
            res["xp_ganho"] += 5
        jogador.vida = min(jogador.vida_max, jogador.vida + 2)
        # Verifica até chefe
        if ate_chefe:
            info = ANDARES.get(jogador.andar,{})
            req_nivel = info.get("req_nivel",99)
            req_flag = info.get("req_flag")
            if jogador.nivel >= req_nivel and (not req_flag or jogador.flags.get(req_flag)):
                res["parou_chefe"] = True
                digitar(f"[🎯 AUTO ATÉ CHEFE] Requisitos atingidos! Pode enfrentar {info['chefe']} no Andar {jogador.andar}.")
                break
        i += 1
        # Se infinito, roda sem perguntar; apenas atualiza status a cada 10 passos
        if infinito and i % 10 == 0:
            digitar(f"[🤖 AUTO IDLE] Passo {i} | XP {jogador.xp} | Vida {jogador.vida} | Andar {jogador.andar} | Batalhas {res['batalhas']}")
        # Se passos definido e atingido, para
        if not infinito and passos is not None and i >= passos:
            break
    digitar(f"[🤖 AUTO PLAY] Sessão encerrada (andar {jogador.andar}, passos: {i}).")
    digitar(f"Batalhas: {res['batalhas']} | Itens: {res['itens']} | Ouro +{res['ouro_ganho']} | XP +{res['xp_ganho']} | Eventos: {res['eventos']}")
    if res["morte"]:
        digitar("Você caiu durante a sessão! Mas revivemos automaticamente (vida restaurada para 50%).")
        jogador.vida = max(10, jogador.vida_max // 2)
    # Atualiza nível se subiu
    return res

# ---------- Magia D&D simples ----------
FEITICOS = {
    "Bola de Fogo": {"custo_mana":8,"dano":15,"desc":"Dano mágico básico."},
    "Cura": {"custo_mana":5,"cura":20,"desc":"Recupera vida."},
    "Escudo Arcano": {"custo_mana":10,"def_bonus":10,"duracao":3,"desc":"Defesa +10 por 3 turnos."},
    "Impulso": {"custo_mana":6,"atq_bonus":8,"duracao":3,"desc":"Ataque +8 por 3 turnos."},
    "Restauração": {"custo_mana":12,"cura":40,"mana_regen":5,"desc":"Cura forte e regenera mana."},
}

class Jogador:
    def __init__(self, nome="Aventurier", classe="Guerreiro", andar=1, idade=18):
        self.nome = nome
        self.classe = classe
        self.idade = idade
        self.andar = andar
        self.atributos = {"forca":10,"destreza":10,"inteligencia":10,"vitalidade":10,"carisma":10}
        self.pontos_atributo = 0
        self.nivel = 1
        self.xp = 0; self.xp_max = 100
        self.inven = {}
        self.ouro = 0
        self.flags = {
            "pescador_falado":False,"goblin_derrotado":False,"crista_pegada":False,
            "portao_aberto":False,"manuscrito_lido":False,"dragao_derrotado":False,
            "dialogo_positivo_3":False,
        }
        self.missao_ativa = None
        self.missao_concluida = False
        self.sala_atual = "Porto"
        # Magia
        self.mana_max = 20 + self.atributos["inteligencia"]*10 + self.nivel*5
        self.mana = self.mana_max
        self.feiticos_aprendidos = ["Bola de Fogo","Cura"]
        self.escudo_ativo = 0
        self.impulso_ativo = 0
        # Conquistas / Títulos simplificados
        self.conquistas = {"Primeiro Sangue":False,"Matador do Chefe":False,"Explorador":False}
        self.titulo_ativo = "Aventurier"
        if classe == "Guerreiro":
            self.vida = 120; self.vida_max = 120; self.atq = 20; self.def_ = 10
            self.feiticos_aprendidos = ["Bola de Fogo","Escudo Arcano"]
        elif classe == "Mago":
            self.vida = 80; self.vida_max = 80; self.atq = 15; self.def_ = 2
            self.mana_max += 30
            self.mana = self.mana_max
            self.feiticos_aprendidos = ["Bola de Fogo","Cura","Restauração"]
        else:  # Arqueiro
            self.vida = 100; self.vida_max = 100; self.atq = 18; self.def_ = 6
            self.ouro += 10
            self.feiticos_aprendidos = ["Bola de Fogo","Impulso"]
        self.adicionar_item("Poção de Vida", 2 if classe=="Mago" else 1)
        self.dialogo_positivo = 0
        self.passivas = []
        self._desbloquear_passivas()
        self._recalcular()

    def _recalcular(self):
        a = self.atributos
        self.vida_max = 50 + a["vitalidade"]*10 + self.nivel*10 + self.andar*5
        self.atq = 5 + a["forca"]*2 + a["inteligencia"]*0.5 + self.nivel*2 + self.andar*2
        self.def_ = 3 + a["destreza"]*1.5 + self.nivel + self.andar
        self.mana_max = 20 + a["inteligencia"]*10 + self.nivel*5 + self.andar*3
        if self.vida > self.vida_max: self.vida = self.vida_max
        if self.mana > self.mana_max: self.mana = self.mana_max

    def _desbloquear_passivas(self):
        novas = []
        if self.nivel >= 5 and "Ataque Duplo" not in self.passivas:
            novas.append("Ataque Duplo")
        if self.nivel >= 3 and self.atributos["destreza"] >= 15 and "Esquiva Rápida" not in self.passivas:
            novas.append("Esquiva Rápida")
        if self.atributos["vitalidade"] >= 15 and "Regeneração" not in self.passivas:
            novas.append("Regeneração")
        if self.nivel >= 8 and "Mestre do Andar" not in self.passivas:
            novas.append("Mestre do Andar")
        if self.nivel >= 10 and "Teleporte Andar" not in self.passivas:
            novas.append("Teleporte Andar")
        if self.atributos["carisma"] >= 15 and "Visão Noturna" not in self.passivas:
            novas.append("Visão Noturna")
        if self.atributos["inteligencia"] >= 15 and "Invocação Rápida" not in self.passivas:
            novas.append("Invocação Rápida")
        if self.atributos["forca"] >= 15 and "Fortalecimento" not in self.passivas:
            novas.append("Fortalecimento")
        if novas:
            self.passivas.extend(novas)
            digitar(f"[🌟 PASSIVAS DESBLOQUEADAS] {', '.join(novas)}")

    def aplicar_passivas(self):
        # Bônus aplicado antes do combate
        if "Ataque Duplo" in self.passivas:
            self.atq += 3  # bônus permanente
        if "Esquiva Rápida" in self.passivas:
            self.def_ += 2
        if "Regeneração" in self.passivas:
            self.vida = min(self.vida_max, self.vida + 5)
        if "Teleporte Andar" in self.passivas:
            # Pode tentar subir andar se requisitos atendidos (simples: bônus no combate contra chefe)
            pass
        if "Visão Noturna" in self.passivas:
            self.atq += 1  # bônus de precisão
        if "Invocação Rápida" in self.passivas:
            self.mana = min(self.mana_max, self.mana + 3)  # regenera mana rapidamente
        if "Fortalecimento" in self.passivas:
            self.atq += 5

    def adicionar_item(self, item, qt=1):
        self.inven[item] = self.inven.get(item,0)+qt

    def usar_poção(self):
        if self.inven.get("Poção de Vida",0)>0:
            self.inven["Poção de Vida"]-=1
            if self.inven["Poção de Vida"]==0: del self.inven["Poção de Vida"]
            self.vida = min(self.vida_max, self.vida + 25 + self.atributos["vitalidade"]*2)
            return True
        return False

    def ganhar_xp(self, qt):
        self.xp += qt
        if self.xp >= self.xp_max:
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.xp = 0
        self.xp_max = 100 * self.nivel
        self.pontos_atributo += 2
        self._recalcular()
        self._desbloquear_passivas()
        digitar(f"[📈 LEVEL UP!] Andar {self.andar} — Nível {self.nivel}! Pontos +2")

    def usar_magia(self, nome):
        if nome not in self.feiticos_aprendidos:
            digitar("Você não aprendeu esse feitiço.")
            return False
        info = FEITICOS.get(nome)
        if not info:
            digitar("Feitiço desconhecido.")
            return False
        if self.mana < info["custo_mana"]:
            digitar("Mana insuficiente! ({} / {})".format(self.mana, info["custo_mana"]))
            return False
        self.mana -= info["custo_mana"]
        digitar(f"[✨ MAGIA] {nome} lançado! Mana restante: {self.mana}")
        # Aplica efeitos
        if nome == "Bola de Fogo":
            dt = info["dano"] + self.atributos["inteligencia"]*2
            digitar(f"Dano de fogo: {dt}")
        elif nome == "Cura":
            cur = info["cura"] + self.atributos["vitalidade"]*3
            self.vida = min(self.vida_max, self.vida + cur)
            digitar(f"Curado +{cur} HP!")
        elif nome == "Escudo Arcano":
            self.escudo_ativo = info.get("duracao",3)
            self.def_ += info.get("def_bonus",10)
            digitar(f"Defesa aumentada por {self.escudo_ativo} turnos.")
        elif nome == "Impulso":
            self.impulso_ativo = info.get("duracao",3)
            self.atq += info.get("atq_bonus",8)
            digitar(f"Ataque aumentado por {self.impulso_ativo} turnos.")
        elif nome == "Restauração":
            cur = info["cura"] + self.atributos["vitalidade"]*4
            self.vida = min(self.vida_max, self.vida + cur)
            self.mana = min(self.mana_max, self.mana + info.get("mana_regen",5))
            digitar(f"Restauração completa! Vida +{cur}, Mana +{info.get('mana_regen',5)}")
        # Regeneração de mana por turno (simples)
        return True

    def distribuir_pontos(self):
        if self.pontos_atributo <= 0:
            digitar("Sem pontos."); return
        while self.pontos_atributo > 0:
            print(f"F={self.atributos['forca']} D={self.atributos['destreza']} I={self.atributos['inteligencia']} V={self.atributos['vitalidade']} C={self.atributos['carisma']}")
            a = input("+1 (F/D/I/V/C) ou 0: ").strip().upper()
            if a == "0": break
            if a == "F": self.atributos["forca"] += 1
            elif a == "D": self.atributos["destreza"] += 1
            elif a == "I": self.atributos["inteligencia"] += 1
            elif a == "V": self.atributos["vitalidade"] += 1
            elif a == "C": self.atributos["carisma"] += 1
            else: continue
            self.pontos_atributo -= 1
        self._recalcular()

# ---------- Andares ----------
ANDARES = {
    1: {"nome":"Porto & Floresta","chefe":"Goblin Sombrio","req_nivel":1,"req_flag":"pescador_falado","salas":["Porto","Floresta"],"recompensa":"Crista do Goblin"},
    2: {"nome":"Castelo do Rei","chefe":"Guardião Real","req_nivel":3,"req_flag":"crista_pegada","salas":["Porto","Castelo"],"recompensa":"Coroa do Guardião"},
    3: {"nome":"Caverna do Dragão","chefe":"Dragão Antigo","req_nivel":5,"req_flag":"portao_aberto","salas":["Porto","Caverna"],"recompensa":"Escama do Dragão"},
    4: {"nome":"Templo Antigo","chefe":"Cumulador","req_nivel":7,"req_flag":"manuscrito_lido","salas":["Porto","Templo"],"recompensa":"Relíquia Antiga"},
    5: {"nome":"Abismo","chefe":"Rei das Sombras","req_nivel":10,"req_flag":"dragao_derrotado","salas":["Porto","Abismo"],"recompensa":"Cristal da Sombra"},
}

def desenhar_torre(jogador):
    # Mapa vertical de andares
    digitar("=== 🏛️ TORRE / ANDARES ===")
    for i in range(5, 0, -1):
        info = ANDARES[i]
        status = "✅ ABERTO" if jogador.andar >= i else "🔒 BLOQUEADO"
        # Se está no andar atual, destaca
        arrow = " <-- VOCÊ" if jogador.andar == i else ""
        # Chefe derrotado?
        chefe_ok = (i==1 and jogador.flags.get("goblin_derrotado")) or (i==2 and jogador.flags.get("portao_aberto")) or (i==3 and jogador.flags.get("dragao_derrotado")) or (i>=4 and False)
        chefe_s = "👑 DERROTADO" if chefe_ok else "👑 PENDENTE"
        print(f"Andar {i} [{status}] — {info['nome']} | Chefe: {info['chefe']} [{chefe_s}]{arrow}")
    print()
    print("Salas disponíveis neste andar:", ", ".join(ANDARES[jogador.andar]["salas"]))

# ---------- Combate ----------
def combate(jogador, nome, vida_inimigo, atq_inimigo):
    v_inim = vida_inimigo
    turnos = 0
    while v_inim > 0 and jogador.vida > 0:
        jogador.aplicar_passivas()
        turnos += 1
        limpar()
        digitar(f"⚔️  COMBATE: {nome} (Andar {jogador.andar})")
        digitar(f"Você: {jogador.vida} HP | Inimigo: {v_inim} HP | Mana: {jogador.mana}/{jogador.mana_max} | XP: {jogador.xp}")
        # Bônus escudo/impulso
        bonus_def = 0
        bonus_atq = 0
        if jogador.escudo_ativo > 0:
            bonus_def = 10; jogador.escudo_ativo -= 1; digitar("[🛡️ Escudo Arcano ativo!]")
        if jogador.impulso_ativo > 0:
            bonus_atq = 8; jogador.impulso_ativo -= 1; digitar("[⚡ Impulso ativo!]")
        print("[A]tacar [D]efender [C]urar [M]agia [S]tatus [I]nventário [F]ugir")
        acao = input("Ação: ").strip().upper()
        if acao == "S":
            digitar(f"Nível: {jogador.nivel} | Atributos: F={jogador.atributos['forca']} D={jogador.atributos['destreza']} I={jogador.atributos['inteligencia']} V={jogador.atributos['vitalidade']} C={jogador.atributos['carisma']}")
            digitar(f"Mana: {jogador.mana} | Feitiços: {', '.join(jogador.feiticos_aprendidos)}")
            pausa(); continue
        elif acao == "M":
            print("Feitiços:")
            for f in jogador.feiticos_aprendidos:
                info = FEITICOS.get(f,{}); print(f"  - {f} (mana {info.get('custo_mana','?')})")
            nome_f = input("Feitiço: ").strip()
            if jogador.usar_magia(nome_f):
                pass  # já aplicou efeitos
        elif acao == "A":
            dano = max(3, jogador.atq + bonus_atq - 2 + random.randint(-2,2))
            v_inim -= dano
            rec = max(0, atq_inimigo - (jogador.def_ + bonus_def))
            jogador.vida -= rec
            digitar(f"Você causa {dano}! Inimigo revida {rec}.")
            if v_inim <= 0:
                jogador.ganhar_xp(20 + jogador.nivel*3)
                jogador.ouro += 10 + jogador.andar*5
                # Se derrotou chefe do andar
                chefe_nome = ANDARES[jogador.andar]["chefe"]
                if nome == chefe_nome and jogador.andar < 5:
                    recompensa = ANDARES[jogador.andar].get("recompensa","Troféu")
                    jogador.adicionar_item(recompensa, 1)
                    jogador.andar += 1
                    digitar(f"[👑 CHEFE DERROTADO!] Recompensa: {recompensa} | Andar avançado para {jogador.andar}!")
                else:
                    digitar("Vitória!")
                jogador.conquistas["Primeiro Sangue"] = True
                pausa(); return True
        elif acao == "D":
            jogador.def_ += 8 + bonus_def
            rec = max(0, atq_inimigo - jogador.def_)
            jogador.vida -= rec
            digitar(f"Defesa reforçada! Sofre {rec}.")
        elif acao == "C":
            if jogador.usar_poção(): digitar("Poção usada!")
            else: digitar("Sem poções!")
        elif acao == "I":
            # Inventário rápido
            print("Inventário:", " | ".join([f"{k}x{v}" for k,v in jogador.inven.items()]) if jogador.inven else "Vazio")
            continue
        elif acao == "F":
            digitar("Você foge!")
            return False
        else:
            digitar("Ação inválida.")
        pausa()
    if jogador.vida <= 0:
        digitar("GAME OVER.")
        jogador.vida = max(10, jogador.vida_max//2)
        return False
    return True

# ---------- Cenas atualizadas ----------
def cena_porto(jogador):
    limpar()
    digitar(f"=== PORTO (Andar {jogador.andar}) ===")
    digitar("Cidade de pescadores. Há uma taverna e uma estrada.")
    print("[1] Falar / Diálogo Pescador")
    print("[2] Ir para Floresta (combate)")
    print("[3] Fazer Auto Play (idle farm)")
    print("[4] Usar Magia")
    print("[5] Inventário / Mapa / Status")
    print("[6] Salvar")
    print("[7] Voltar ao Menu")
    es = input("Escolha: ").strip()
    if es == "1":
        digitar('Pescador: "Se você me ajudar, te darei o caminho."')
        if not jogador.flags.get("pescador_falado"):
            jogador.flags["pescador_falado"] = True
            jogador.adicionar_item("Chave do Castelo", 1)
            jogador.adicionar_item("Manuscrito Antigo", 1)
            jogador.missao_ativa = "O Mar Escuro"
            jogador.ganhar_xp(10)
            digitar("[📜 MISSÃO ATIVADA] 'O Mar Escuro'")
        else:
            digitar("Ele te lembra da missão.")
        pausa()
    elif es == "2":
        jogador.sala_atual = "Floresta"
        ok = combate(jogador, "Goblin Sombrio", 30, 8)
        if ok:
            jogador.flags["goblin_derrotado"] = True
            jogador.flags["crista_pegada"] = True
            jogador.adicionar_item("Crista Azul", 1)
            digitar("Crista obtida! Pode ir ao Castelo (Andar 2) se tiver nível 3+")
            pausa()
    elif es == "3":
        # Auto Play
        res = auto_play(jogador, passos=20)
        # Se atingiu requisitos, pode tentar subir de andar
        info = ANDARES[jogador.andar]
        if jogador.nivel >= info["req_nivel"] and (not info.get("req_flag") or jogador.flags.get(info["req_flag"])):
            digitar(f"[✅ REQUISITO ATINGIDO] Andar {jogador.andar}: Nível {jogador.nivel}, flag OK.")
            digitar("Você pode enfrentar o chefe agora pelo menu de combate.")
    elif es == "4":
        # Menu magia
        print("Feitiços aprendidos:", ", ".join(jogador.feiticos_aprendidos))
        nome = input("Feitiço (ou 0 para sair): ").strip()
        if nome != "0":
            jogador.usar_magia(nome)
        pausa()
    elif es == "5":
        # Menu completo rápido
        digitar(f"Andar: {jogador.andar} | Nível: {jogador.nivel} | XP: {jogador.xp}/{jogador.xp_max}")
        digitar(f"Vida: {jogador.vida}/{jogador.vida_max} | Mana: {jogador.mana}/{jogador.mana_max}")
        digitar(f"Atributos: F={jogador.atributos['forca']} D={jogador.atributos['destreza']} I={jogador.atributos['inteligencia']} V={jogador.atributos['vitalidade']} C={jogador.atributos['carisma']}")
        desenhar_torre(jogador)
        pausa()
    elif es == "6":
        salvar_man = True
        with open(SAVE_MANUAL,"w",encoding="utf-8") as f:
            f.write(f"# Save Idle\nAndar: {jogador.andar}\nNível: {jogador.nivel}\nXP: {jogador.xp}\nVida: {jogador.vida}/\nOuro: {jogador.ouro}\n")
        digitar("[💾 SAVE] Manual salvo.")
        pausa()
    jogador.sala_atual = "Porto"

def cena_chefe(jogador):
    info = ANDARES[jogador.andar]
    digitar(f"=== CHEFE DO ANDAR {jogador.andar} ===")
    digitar(f"Chefe: {info['chefe']} | Requisitos: Nível {info['req_nivel']} | Flag: {info.get('req_flag','Nenhum')}")
    if jogador.nivel < info["req_nivel"]:
        digitar("Você ainda não tem nível suficiente.")
        pausa(); return
    if info.get("req_flag") and not jogador.flags.get(info["req_flag"]):
        digitar("Você ainda não completou o requisito (flag bloqueada).")
        pausa(); return
    print("[1] Combater Chefe\n[2] Voltar")
    es = input("Escolha: ").strip()
    if es == "1":
        # Dificuldade aumenta com andar
        vida = 40 + jogador.andar*30
        atq = 10 + jogador.andar*5
        ok = combate(jogador, info["chefe"], vida, atq)
        if ok:
            jogador.andar += 1
            digitar(f"[👑 CHEFE DERROTADO!] Andar avançado para {jogador.andar}!")
            jogador.ganhar_xp(50)
    jogador.sala_atual = "Porto"

# ---------- Salvar / Carregar ----------
def auto_salvar(jogador):
    try:
        with open(SAVE_AUTO,"w",encoding="utf-8") as f:
            f.write(f"# Auto Save RPG Idle\nNome:{jogador.nome}\nClasse:{jogador.classe}\nIdade:{jogador.idade}\nAndar:{jogador.andar}\nNivel:{jogador.nivel}\nXP:{jogador.xp}\nVida:{jogador.vida}\nOuro:{jogador.ouro}\nMana:{jogador.mana}\nPassivas:{','.join(jogador.passivas)}\n")
    except Exception:
        pass

def salvar_man(jogador):
    with open(SAVE_MANUAL,"w",encoding="utf-8") as f:
        f.write(f"# RPG Idle Save\nNome:{jogador.nome}\nClasse:{jogador.classe}\nIdade:{jogador.idade}\nAndar:{jogador.andar}\nNivel:{jogador.nivel}\nXP:{jogador.xp}\nVida:{jogador.vida}\nOuro:{jogador.ouro}\nMana:{jogador.mana}\nAtributos:F={jogador.atributos['forca']} D={jogador.atributos['destreza']} I={jogador.atributos['inteligencia']} V={jogador.atributos['vitalidade']} C={jogador.atributos['carisma']}\n")
    digitar("[💾 SAVE MANUAL] 'save_idle.txt'")

def carregar_man(jogador):
    if not os.path.exists(SAVE_MANUAL): return False
    with open(SAVE_MANUAL,"r") as f:
        for linha in f:
            if linha.startswith("Andar:"): jogador.andar = int(linha.split(":")[1].strip())
            elif linha.startswith("Nivel:"): jogador.nivel = int(linha.split(":")[1].strip())
            elif linha.startswith("XP:"): jogador.xp = int(linha.split(":")[1].strip())
            elif linha.startswith("Vida:"): jogador.vida = int(linha.split(":")[1].strip())
            elif linha.startswith("Idade:"): jogador.idade = int(linha.split(":")[1].strip())
    jogador._recalcular()
    digitar("[📂 LOAD] Carregado.")
    return True

# ---------- Menu ----------
def menu():
    # Criação/edição inicial
    nome = input("Nome do personagem: ").strip() or "Aventurier"
    print("Classes: [G] Guerreiro | [M] Mago | [A] Arqueiro")
    classe_input = input("Classe (G/M/A): ").strip().upper()
    classe = "Mago" if classe_input == "M" else "Arqueiro" if classe_input == "A" else "Guerreiro"
    idade_str = input("Idade (número): ").strip()
    idade = int(idade_str) if idade_str.isdigit() else 18
    j = Jogador(nome, classe, 1)
    j.idade = idade
    # Carrega auto-save automaticamente (não perde progresso)
    if os.path.exists(SAVE_AUTO):
        try:
            temp = Jogador("Temp", "Guerreiro", 1)
            carregar_man(temp)  # tenta carregar do manual se existe; se não, usa padrão
            # Se temos save auto, carregamos direto (simples: lemos arquivo e aplicamos)
            with open(SAVE_AUTO,"r") as f:
                for linha in f:
                    if linha.startswith("Nome:"): j.nome = linha.split(":")[1].strip()
                    elif linha.startswith("Classe:"): j.classe = linha.split(":")[1].strip()
                    elif linha.startswith("Idade:"): j.idade = int(linha.split(":")[1].strip())
                    elif linha.startswith("Andar:"): j.andar = int(linha.split(":")[1].strip())
                    elif linha.startswith("Nivel:"): j.nivel = int(linha.split(":")[1].strip())
                    elif linha.startswith("XP:"): j.xp = int(linha.split(":")[1].strip())
                    elif linha.startswith("Vida:"): j.vida = int(linha.split(":")[1].strip())
                    elif linha.startswith("Ouro:"): j.ouro = int(linha.split(":")[1].strip())
                    elif linha.startswith("Mana:"): j.mana = int(linha.split(":")[1].strip())
            j._recalcular()
            digitar("[📂 AUTO LOAD] Progresso restaurado automaticamente.")
        except Exception:
            pass
    # Pergunta manual só se quiser carregar outro save específico
    if os.path.exists(SAVE_MANUAL):
        resp = input("Save manual encontrado. Carregar? (S/N) — S = usar manual, N = usar auto: ").strip().upper()
        if resp == "S":
            carregar_man(j)
            alterar = input("Alterar nome/classe/idade do save? (S/N): ").strip().upper()
            if alterar == "S":
                novo_nome = input("Novo nome (Enter = manter): ").strip() or j.nome
                novo_classe = input("Nova classe G/M/A (Enter = manter): ").strip().upper()
                novo_idade = input("Nova idade (Enter = manter): ").strip()
                j.nome = novo_nome
                j.classe = "Mago" if novo_classe=="M" else "Arqueiro" if novo_classe=="A" else j.classe
                j.idade = int(novo_idade) if novo_idade.isdigit() else j.idade
    while True:
        auto_salvar(j)
        limpar()
        print(logo_ascii())
        print(renderizar_personagem(j))
        print(borda_titulo("  MENU PRINCIPAL  ", YW))
        # Status visual em caixa
        print(f"{BL}{BOLD}┌─ PERSONAGEM ───────────────────────────────────────────┐{RESET}")
        print(f"{BL}│ {BOLD}Nome:{RESET} {destaque(j.nome, YW)}{' '*30}│{RESET}")
        print(f"{BL}│ {BOLD}Idade:{RESET} {destaque(str(j.idade), GN)}  {BOLD}Classe:{RESET} {destaque(j.classe, CY)}  {BOLD}Andar:{RESET} {destaque(str(j.andar), MG)}  │{RESET}")
        print(f"{BL}│ {BOLD}Nível:{RESET} {destaque(str(j.nivel), YW)}  {BOLD}XP:{RESET} {destaque(str(j.xp)+'/'+str(j.xp_max), GN)}  {BOLD}Ouro:{RESET} {destaque(str(j.ouro), YW)}  │{RESET}")
        print(f"{BL}│ {BOLD}Vida:{RESET} {destaque(str(j.vida)+'/'+str(j.vida_max), GN)}  {BOLD}Mana:{RESET} {destaque(str(j.mana)+'/'+str(j.mana_max), MG)}  │{RESET}")
        print(f"{BL}│ {BOLD}Passivas:{RESET} {destaque(', '.join(j.passivas) if j.passivas else 'Nenhuma', CY)}{' '*10}│{RESET}")
        print(f"{BL}{BOLD}└{'─'*58}┘{RESET}")
        print()
        print(f"{GN}➜{RESET}  [1] {destaque('Explorar / Andar / Feira', YW)}")
        print(f"{GN}➜{RESET}  [2] {destaque('Enfrentar Chefe do Andar', YW)}")
        print(f"{GN}➜{RESET}  [3] {destaque('Auto Play (Idle Farm) — Infinito', YW)}")
        print(f"{GN}➜{RESET}  [4] {destaque('Magia / Feitiços', YW)}")
        print(f"{GN}➜{RESET}  [5] {destaque('Distribuir Pontos', YW)}")
        print(f"{GN}➜{RESET}  [6] {destaque('Inventário / Mapa / Status', YW)}")
        print(f"{GN}➜{RESET}  [7] {destaque('Salvar', YW)}")
        print(f"{GN}➜{RESET}  [8] {destaque('Carregar', YW)}")
        print(f"{GN}➜{RESET}  [9] {destaque('Sair', YW)}")
        print()
        op = input("Opção: ").strip()
        if op == "1": cena_porto(j)
        elif op == "2": cena_chefe(j)
        elif op == "3":
            modo = input("Auto Normal (N) / Auto até Chefe (C) / Infinito (I)? ").strip().upper()
            ate_chefe = (modo == "C")
            infinito = (modo == "I")
            passos = None if infinito else 20
            res = auto_play(j, passos=passos, ate_chefe=ate_chefe, infinito=infinito)
            if res.get("parou_chefe"):
                digitar("Você pode ir direto ao chefe (opção 2)!")
            pausa()
        elif op == "4":
            print("Feitiços:", ", ".join(j.feiticos_aprendidos))
            nome = input("Feitiço (ou 0): ").strip()
            if nome != "0": j.usar_magia(nome)
            pausa()
        elif op == "5": j.distribuir_pontos(); pausa()
        elif op == "6":
            digitar("=== INVENTÁRIO / STATUS ===")
            print("Inventário:", j.inven)
            desenhar_torre(j)
            pausa()
        elif op == "7": salvar_man(j); pausa()
        elif op == "8":
            if carregar_man(j): pausa()
        elif op == "9":
            salvar_man(j)
            digitar("Salvo. Até a próxima!")
            break
        else:
            print("Inválido.")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nSaindo...")
