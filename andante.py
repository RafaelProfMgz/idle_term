#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPG IDLE + ANDARES + MAGIA + MAPEAMENTO ASCII + AUTO PLAY
- Andares (1-5) com chefes e requisitos
- Modo Idle: joga sozinho sem parar (farm, chefes, andares, voltas na torre) + progresso offline
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

# Saves ficam ao lado do andante.py, de onde quer que o jogo seja aberto
PASTA_JOGO = os.path.dirname(os.path.abspath(__file__))
SAVE_MANUAL = os.path.join(PASTA_JOGO, "save_idle.txt")
SAVE_AUTO = os.path.join(PASTA_JOGO, "save_auto_idle.txt")

# ---------- Eventos do modo idle ----------
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

# ---------- Modo Idle (Auto Play contínuo) ----------
class LeitorTecla:
    """Lê uma tecla sem travar o loop. Windows: msvcrt | Linux: termios + select.
    Se não houver terminal (ex.: input por pipe), só Ctrl+C interrompe."""
    def __enter__(self):
        self.antigo = None
        if os.name != 'nt' and sys.stdin.isatty():
            import termios, tty
            self.antigo = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, *exc):
        if self.antigo is not None:
            import termios
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.antigo)

    def ler(self):
        """Devolve todas as teclas já apertadas (string, pode ser vazia)."""
        teclas = ""
        try:
            if os.name == 'nt':
                import msvcrt
                while msvcrt.kbhit():
                    teclas += msvcrt.getwch()
            elif sys.stdin.isatty():
                import select
                fd = sys.stdin.fileno()
                # os.read direto no descritor: sys.stdin.read() guardaria teclas num buffer que o select não vê
                while select.select([fd], [], [], 0)[0]:
                    lido = os.read(fd, 64)
                    if not lido:
                        break
                    teclas += lido.decode("utf-8", "ignore")
        except Exception:
            pass
        return teclas

VELOCIDADES = [2.0, 1.0, 0.5, 0.25, 0.1]   # segundos por tick
AUTO_SALVAR_A_CADA = 10                    # ticks
# Ritmo (a 1s/tick): nível 3 ~15s, nível 5 ~2,5min; voltas na torre ~27min, 43min, 1,2h, 1,8h, 2,5h...
RITMO_XP = 0.6                             # multiplicador do XP ganho no idle
NIVEIS_POR_VOLTA = 4                       # quantos níveis a mais cada volta na torre exige
OFFLINE_MAX_MIN = 12 * 60                  # progresso offline limitado a 12h
OFFLINE_EFICIENCIA = 0.5                   # offline rende 50% do que renderia com o jogo aberto

def barra(atual, maximo, largura=20, cor=GN):
    cheio = int(largura * max(0, min(1, atual / maximo))) if maximo else 0
    return f"{cor}{'█'*cheio}{DIM}{'░'*(largura-cheio)}{RESET}"

def nivel_requerido(jogador):
    """Nível mínimo do chefe atual; cada volta na torre pede +NIVEIS_POR_VOLTA."""
    return ANDARES[jogador.andar]["req_nivel"] + NIVEIS_POR_VOLTA * (jogador.ciclo - 1)

def requisitos_ok(jogador):
    flag = ANDARES[jogador.andar].get("req_flag")
    return jogador.nivel >= nivel_requerido(jogador) and (not flag or jogador.flags.get(flag))

def luta_auto(jogador, vida_inimigo, atq_inimigo):
    """Resolve uma luta inteira sem input. Retorna (venceu, dano_recebido)."""
    vida_ini = jogador.vida
    v = vida_inimigo
    while v > 0 and jogador.vida > 0:
        if "Bola de Fogo" in jogador.feiticos_aprendidos and jogador.mana >= FEITICOS["Bola de Fogo"]["custo_mana"] and v > jogador.atq:
            jogador.mana -= FEITICOS["Bola de Fogo"]["custo_mana"]
            v -= FEITICOS["Bola de Fogo"]["dano"] + jogador.atributos["inteligencia"] * 2
        else:
            v -= max(3, jogador.atq + random.randint(-3, 3))
        if v > 0:
            jogador.vida -= max(1, int(atq_inimigo - jogador.def_ / 2) + random.randint(-2, 2))
        if jogador.vida < jogador.vida_max * 0.3 and jogador.inven.get("Poção de Vida", 0) > 0:
            jogador.usar_poção()
    return jogador.vida > 0, max(0, vida_ini - jogador.vida)

def _auto_distribuir(jogador):
    if jogador.pontos_atributo <= 0:
        return None
    foco = {"Guerreiro": ["forca", "vitalidade"], "Mago": ["inteligencia", "vitalidade"],
            "Arqueiro": ["destreza", "forca"]}.get(jogador.classe, ["forca", "vitalidade"])
    gastos = jogador.pontos_atributo
    for k in range(gastos):
        jogador.atributos[foco[k % 2]] += 1
    jogador.pontos_atributo = 0
    jogador._recalcular()
    jogador._desbloquear_passivas(silencioso=True)
    return f"+{gastos} pontos em {' / '.join(foco)}"

def tick_idle(jogador, res, log):
    """Um passo do jogo idle. Escreve o que aconteceu em `log`."""
    def anota(txt):
        log.append(txt); del log[:-8]
    escala = jogador.escala()
    info = ANDARES[jogador.andar]
    # Regeneração passiva
    jogador.vida = min(jogador.vida_max, jogador.vida + max(2, jogador.vida_max // 40))
    jogador.mana = min(jogador.mana_max, jogador.mana + 1 + jogador.atributos["inteligencia"] // 5)
    jogador.aplicar_flags_de_progresso()
    msg = _auto_distribuir(jogador)
    if msg: anota(f"📈 {msg}")
    for linha in checar_conquistas(jogador):
        anota(linha)
    # Chefe: luta sozinho assim que os requisitos batem e a vida está boa (Teleporte Andar: basta 50%)
    limite = 0.5 if "Teleporte Andar" in jogador.passivas else 0.8
    if requisitos_ok(jogador) and jogador.vida >= jogador.vida_max * limite:
        vida_c, atq_c = stats_chefe(jogador)
        res["chefes_tentados"] += 1
        venceu, dano = luta_auto(jogador, vida_c, atq_c)
        if venceu:
            res["chefes"] += 1
            anota(f"👑 {info['chefe']} derrotado! (-{dano} HP)")
            for linha in vencer_chefe(jogador):
                anota(linha)
        else:
            jogador.vida = max(1, jogador.vida_max // 3)
            anota(f"💀 {info['chefe']} venceu. Você recua para treinar.")
        return
    # Evento de história que destrava o andar
    flag = info.get("req_flag")
    if flag and not jogador.flags.get(flag) and flag in HISTORIA and random.random() < 0.25:
        jogador.flags[flag] = True
        if flag == "pescador_falado":
            jogador.dialogo_bom()
        for linha in HISTORIA[flag]["texto"]:
            anota(linha)
        for item in HISTORIA[flag].get("itens", []):
            jogador.adicionar_item(item, 1)
        res["eventos"] += 1
        return
    tipo = random.choices([e[0] for e in EVENTOS_AUTO], weights=[e[1] for e in EVENTOS_AUTO], k=1)[0]
    if tipo == "Batalha":
        monstro = random.choice(MONSTROS[jogador.andar])
        venceu, dano = luta_auto(jogador, int((15 + jogador.andar * 12) * escala), int((5 + jogador.andar * 4) * escala))
        res["batalhas"] += 1
        if venceu:
            xp = max(1, int(random.randint(10, 25) * jogador.andar * escala * RITMO_XP))
            ouro = int(random.randint(5, 15) * jogador.andar * escala)
            jogador.ouro += ouro; res["ouro_ganho"] += ouro; res["xp_ganho"] += xp
            subiu = jogador.ganhar_xp(xp, silencioso=True)
            anota(f"⚔️  {monstro} vencido: +{xp} XP, +{ouro} ouro" + (f" (-{dano} HP)" if dano else ""))
            if subiu: anota(f"🌟 LEVEL UP! Nível {jogador.nivel}")
        else:
            res["mortes"] += 1
            jogador.vida = max(1, jogador.vida_max // 2)
            anota(f"💀 {monstro} te derrubou. Você acorda no Porto.")
    elif tipo == "Item":
        item = random.choices(["Poção de Vida", "Crista Azul", "Manuscrito Antigo"], weights=[6, 2, 1], k=1)[0]
        jogador.adicionar_item(item, 1); res["itens"] += 1
        anota(f"🎒 Encontrou: {item}")
    elif tipo == "Ouro":
        qt = int(random.randint(5, 15) * jogador.andar * escala)
        jogador.ouro += qt; res["ouro_ganho"] += qt
        anota(f"💰 +{qt} ouro largado no caminho")
    elif tipo == "Diálogo":
        res["eventos"] += 1
        anota(random.choice(FALAS_IDLE.get(jogador.andar, FALAS_IDLE[1])))
    elif tipo == "Trabalho":
        xp = max(1, int(random.randint(5, 15) * jogador.andar * RITMO_XP))
        jogador.ganhar_xp(xp, silencioso=True); res["xp_ganho"] += xp
        anota(f"🔨 Trabalhou no porto: +{xp} XP")

def desenhar_idle(jogador, res, log, velocidade):
    info = ANDARES[jogador.andar]
    vida_c, _ = stats_chefe(jogador)
    flag = info.get("req_flag")
    ok_nv = "✔" if jogador.nivel >= nivel_requerido(jogador) else "✘"
    ok_fl = "✔" if (not flag or jogador.flags.get(flag)) else "✘"
    linhas = [
        f"{YW}{BOLD}═══ ANDANTE · MODO IDLE ═══{RESET}  Volta {jogador.ciclo} · Andar {jogador.andar}/5 {CY}{info['nome']}{RESET}",
        f"{BOLD}{jogador.nome}{RESET} ({jogador.classe})  Nível {jogador.nivel}  Ouro {YW}{jogador.ouro}{RESET}",
        f"Vida {barra(jogador.vida, jogador.vida_max, cor=GN)} {int(jogador.vida)}/{int(jogador.vida_max)}",
        f"Mana {barra(jogador.mana, jogador.mana_max, cor=MG)} {int(jogador.mana)}/{int(jogador.mana_max)}",
        f"XP   {barra(jogador.xp, jogador.xp_max, cor=YW)} {jogador.xp}/{jogador.xp_max}",
        f"Chefe: {info['chefe']} ({vida_c} HP) — Nível {nivel_requerido(jogador)} {ok_nv}  {flag or '-'} {ok_fl}",
        f"Título: {jogador.titulo_ativo} · Conquistas {sum(jogador.conquistas.values())}/{len(CONQUISTAS_DEF)} · Passivas: {', '.join(jogador.passivas) or 'nenhuma'}",
        f"Sessão: {res['batalhas']} batalhas · {res['chefes']} chefes · +{res['xp_ganho']} XP · +{res['ouro_ganho']} ouro",
        f"{CY}── Últimos eventos ──{RESET}",
    ] + [f"  {l}" for l in log] + [""] * (8 - len(log)) + [
        f"{DIM}[Q] voltar ao menu  [+] mais rápido  [-] mais lento  ({velocidade}s/tick · salva sozinho){RESET}",
    ]
    sys.stdout.write("\033[H\033[J" + "\n".join(linhas) + "\n")
    sys.stdout.flush()

def auto_play(jogador, passos=None, velocidade=1.0, desenhar=True):
    """Modo idle: joga sozinho para sempre, até você apertar Q (ou Ctrl+C).
    `passos` limita os ticks (usado em testes); `velocidade` = segundos por tick."""
    res = {"batalhas": 0, "chefes": 0, "chefes_tentados": 0, "itens": 0, "ouro_ganho": 0,
           "xp_ganho": 0, "eventos": 0, "mortes": 0, "ticks": 0}
    log = ["🤖 Modo idle iniciado. O andante segue sozinho."]
    sair = False
    try:
        with LeitorTecla() as teclado:
            while not sair and (passos is None or res["ticks"] < passos):
                res["ticks"] += 1
                tick_idle(jogador, res, log)
                if res["ticks"] % AUTO_SALVAR_A_CADA == 0:
                    auto_salvar(jogador)
                if desenhar:
                    desenhar_idle(jogador, res, log, velocidade)
                fim = time.time() + velocidade
                while not sair:
                    for t in teclado.ler():
                        if t.lower() == "q":
                            sair = True
                        elif t in ("+", "="):
                            velocidade = min((v for v in VELOCIDADES if v < velocidade), default=velocidade, key=lambda v: velocidade - v)
                        elif t in ("-", "_"):
                            velocidade = min((v for v in VELOCIDADES if v > velocidade), default=velocidade, key=lambda v: v - velocidade)
                    if time.time() >= fim:
                        break
                    time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    auto_salvar(jogador)
    return res

def progresso_offline(jogador, segundos):
    """Ganhos enquanto o jogo estava fechado (limitado a OFFLINE_MAX_MIN)."""
    minutos = min(int(segundos // 60), OFFLINE_MAX_MIN)
    if minutos < 1:
        return None
    # Média do idle aberto por minuto: ~480 XP e ~360 ouro por andar (60 ticks)
    xp = int(minutos * 480 * jogador.andar * jogador.escala() * RITMO_XP * OFFLINE_EFICIENCIA)
    ouro = int(minutos * 360 * jogador.andar * jogador.escala() * OFFLINE_EFICIENCIA)
    nivel_antes = jogador.nivel
    jogador.ouro += ouro
    jogador.ganhar_xp(xp, silencioso=True)
    _auto_distribuir(jogador)
    jogador.vida = jogador.vida_max; jogador.mana = jogador.mana_max
    return minutos, xp, ouro, jogador.nivel - nivel_antes

# ---------- Magia D&D simples ----------
FEITICOS = {
    "Bola de Fogo": {"custo_mana":8,"dano":15,"desc":"Dano mágico básico."},
    "Cura": {"custo_mana":5,"cura":20,"desc":"Recupera vida."},
    "Escudo Arcano": {"custo_mana":10,"def_bonus":10,"duracao":3,"desc":"Defesa +10 por 3 turnos."},
    "Impulso": {"custo_mana":6,"atq_bonus":8,"duracao":3,"desc":"Ataque +8 por 3 turnos."},
    "Restauração": {"custo_mana":12,"cura":40,"mana_regen":5,"desc":"Cura forte e regenera mana."},
}

def xp_para_nivel(nivel):
    """XP necessário para sair deste nível. Curva polinomial típica de idle:
    níveis iniciais em segundos, depois cada vez mais longos (ver RITMO_XP)."""
    return int(35 * nivel ** 2.7)

FEITICOS_CLASSE = {
    "Guerreiro": ["Bola de Fogo","Escudo Arcano"],
    "Mago": ["Bola de Fogo","Cura","Restauração"],
    "Arqueiro": ["Bola de Fogo","Impulso"],
}

# Bônus de cada classe somados em _recalcular()
CLASSES = {
    "Guerreiro": {"vida":40,"atq":4,"def":4,"mana":-20,"ouro":0,"pocoes":1},
    "Mago":      {"vida":-20,"atq":-4,"def":-4,"mana":40,"ouro":0,"pocoes":2},
    "Arqueiro":  {"vida":10,"atq":2,"def":2,"mana":0,"ouro":10,"pocoes":1},
}

# Passivas com bônus fixo de status (as de efeito por turno ficam em aplicar_passivas)
PASSIVAS_BONUS = {
    "Ataque Duplo": {"atq":3},
    "Esquiva Rápida": {"def":2},
    "Visão Noturna": {"atq":1},
    "Fortalecimento": {"atq":5},
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
        self.xp = 0; self.xp_max = xp_para_nivel(1)
        self.inven = {}
        self.ouro = 0
        self.ciclo = 1  # "volta" na torre: depois do Andar 5 recomeça mais difícil
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
        # Conquistas / Títulos (CONQUISTAS_DEF / TITULOS_DEF)
        self.conquistas = {nome: False for nome in CONQUISTAS_DEF}
        self.titulo_ativo = "Aventurier"
        self.ultimo_dano = 0
        if self.classe not in CLASSES:
            self.classe = "Guerreiro"
        self.ouro += CLASSES[self.classe]["ouro"]
        self.feiticos_aprendidos = list(FEITICOS_CLASSE[self.classe])
        self.adicionar_item("Poção de Vida", CLASSES[self.classe]["pocoes"])
        self.dialogo_positivo = 0
        self.passivas = []
        self.vida = 0  # definidos de verdade logo abaixo, após _recalcular()
        self._desbloquear_passivas()
        self._recalcular()
        self.vida = self.vida_max; self.mana = self.mana_max

    def _recalcular(self):
        """Status = atributos + nível/andar + bônus da classe + passivas + título.
        Nada aqui acumula: pode ser chamado quantas vezes quiser."""
        a = self.atributos
        c = CLASSES.get(self.classe, CLASSES["Guerreiro"])
        self.vida_max = 50 + a["vitalidade"]*10 + self.nivel*10 + self.andar*5 + c["vida"]
        self.atq = 5 + a["forca"]*2 + a["inteligencia"]*0.5 + self.nivel*2 + self.andar*2 + c["atq"]
        self.def_ = 3 + a["destreza"]*1.5 + self.nivel + self.andar + c["def"]
        self.mana_max = 20 + a["inteligencia"]*10 + self.nivel*5 + self.andar*3 + c["mana"]
        for p in self.passivas:
            self.atq += PASSIVAS_BONUS.get(p, {}).get("atq", 0)
            self.def_ += PASSIVAS_BONUS.get(p, {}).get("def", 0)
        titulo = TITULOS_DEF.get(self.titulo_ativo, {})
        self.atq += titulo.get("bonus_atq", 0)
        self.def_ += titulo.get("bonus_def", 0)
        if self.vida > self.vida_max: self.vida = self.vida_max
        if self.mana > self.mana_max: self.mana = self.mana_max

    def escala(self):
        """Multiplicador de dificuldade/recompensa por volta na torre."""
        return 1 + 0.5 * (self.ciclo - 1)

    def aplicar_flags_de_progresso(self):
        """Quem já passou de um andar venceu os chefes anteriores (vale para saves antigos)."""
        for n in range(1, self.andar):
            for f in CHEFE_FLAGS.get(n, []):
                self.flags[f] = True

    def dialogo_bom(self):
        """Conta uma conversa positiva; a 3ª ativa a flag dialogo_positivo_3."""
        self.dialogo_positivo += 1
        if self.dialogo_positivo >= 3:
            self.flags["dialogo_positivo_3"] = True

    def _desbloquear_passivas(self, silencioso=False):
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
            self._recalcular()
            if not silencioso:
                digitar(f"[🌟 PASSIVAS DESBLOQUEADAS] {', '.join(novas)}")

    def aplicar_passivas(self):
        """Efeitos por turno de combate. Bônus fixos de ATQ/DEF ficam em PASSIVAS_BONUS."""
        if "Regeneração" in self.passivas:
            self.vida = min(self.vida_max, self.vida + 5)
        if "Invocação Rápida" in self.passivas:
            self.mana = min(self.mana_max, self.mana + 3)

    def adicionar_item(self, item, qt=1):
        self.inven[item] = self.inven.get(item,0)+qt

    def usar_poção(self):
        if self.inven.get("Poção de Vida",0)>0:
            self.inven["Poção de Vida"]-=1
            if self.inven["Poção de Vida"]==0: del self.inven["Poção de Vida"]
            self.vida = min(self.vida_max, self.vida + 25 + self.atributos["vitalidade"]*2)
            return True
        return False

    def ganhar_xp(self, qt, silencioso=False):
        """Soma XP e sobe quantos níveis couberem. Retorna True se subiu."""
        if "Mestre do Andar" in self.passivas:
            qt = int(qt * 1.25)
        self.xp += qt
        subiu = False
        while self.xp >= self.xp_max:
            self.xp -= self.xp_max
            self.subir_nivel(silencioso)
            subiu = True
        return subiu

    def subir_nivel(self, silencioso=False):
        self.nivel += 1
        self.xp_max = xp_para_nivel(self.nivel)
        self.pontos_atributo += 2
        self._recalcular()
        self.vida = self.vida_max; self.mana = self.mana_max  # level up restaura
        self._desbloquear_passivas(silencioso)
        if not silencioso:
            digitar(f"[📈 LEVEL UP!] Andar {self.andar} — Nível {self.nivel}! Pontos +2")

    def usar_magia(self, nome):
        """Lança o feitiço. Bola de Fogo guarda o dano em self.ultimo_dano (o combate aplica)."""
        self.ultimo_dano = 0
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
            self.ultimo_dano = info["dano"] + self.atributos["inteligencia"]*2
            digitar(f"Dano de fogo: {self.ultimo_dano}")
        elif nome == "Cura":
            cur = info["cura"] + self.atributos["vitalidade"]*3
            self.vida = min(self.vida_max, self.vida + cur)
            digitar(f"Curado +{cur} HP!")
        elif nome == "Escudo Arcano":
            self.escudo_ativo = info.get("duracao",3)  # bônus aplicado turno a turno em combate()
            digitar(f"Defesa +{info.get('def_bonus',10)} por {self.escudo_ativo} turnos de combate.")
        elif nome == "Impulso":
            self.impulso_ativo = info.get("duracao",3)
            digitar(f"Ataque +{info.get('atq_bonus',8)} por {self.impulso_ativo} turnos de combate.")
        elif nome == "Restauração":
            cur = info["cura"] + self.atributos["vitalidade"]*4
            self.vida = min(self.vida_max, self.vida + cur)
            self.mana = min(self.mana_max, self.mana + info.get("mana_regen",5))
            digitar(f"Restauração completa! Vida +{cur}, Mana +{info.get('mana_regen',5)}")
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
        self._desbloquear_passivas()

# ---------- Conquistas / Títulos ----------
CONQUISTAS_DEF = {
    "Primeiro Sangue": {"desc":"Derrotou o Goblin Sombrio","ouro":10,"xp":20,"flags":["goblin_derrotado"]},
    "Pescador Amigo": {"desc":"Aceitou ajudar o Pescador","ouro":15,"xp":30,"flags":["pescador_falado"]},
    "Crista Azul": {"desc":"Obteve a crista que abre o Castelo","ouro":20,"xp":25,"flags":["crista_pegada"]},
    "Portão Aberto": {"desc":"Passou pelo portão do Castelo","ouro":20,"xp":30,"flags":["portao_aberto"]},
    "Leitor de Manuscritos": {"desc":"Leu o Manuscrito Antigo","ouro":10,"xp":15,"flags":["manuscrito_lido"]},
    "Matador de Dragão": {"desc":"Derrotou o Dragão Antigo","ouro":100,"xp":100,"flags":["dragao_derrotado"]},
    "Dono do Porto": {"desc":"Completou a torre","ouro":50,"xp":50,"volta":2},
    "Diplomata": {"desc":"Teve 3 conversas positivas","ouro":25,"xp":25,"flags":["dialogo_positivo_3"]},
}

# Títulos: liberados por conquista + nível; o melhor liberado fica ativo e dá bônus
TITULOS_DEF = {
    "Aventurier": {"req_nivel":1,"conquista":None,"status":"Explorador dos mares.","bonus_atq":0,"bonus_def":0},
    "Caçador de Sombras": {"req_nivel":5,"conquista":"Crista Azul","status":"Possui a Crista Azul.","bonus_atq":3,"bonus_def":2},
    "Guardião do Rei": {"req_nivel":8,"conquista":"Portão Aberto","status":"Passou pelo portão do Castelo.","bonus_atq":5,"bonus_def":5},
    "Matador de Dragões": {"req_nivel":10,"conquista":"Matador de Dragão","status":"O Dragão caiu.","bonus_atq":8,"bonus_def":8},
    "Lenda do Porto": {"req_nivel":15,"conquista":"Dono do Porto","status":"Completou a torre.","bonus_atq":10,"bonus_def":10},
}

def checar_conquistas(jogador):
    """Libera conquistas novas (dá ouro/XP) e escolhe o melhor título. Retorna as linhas a mostrar."""
    linhas = []
    for nome, c in CONQUISTAS_DEF.items():
        if jogador.conquistas.get(nome):
            continue
        ok = all(jogador.flags.get(f) for f in c.get("flags", [])) and jogador.ciclo >= c.get("volta", 1)
        if ok:
            jogador.conquistas[nome] = True
            jogador.ouro += c["ouro"]
            jogador.ganhar_xp(c["xp"], silencioso=True)
            linhas.append(f"🏆 Conquista: {nome} (+{c['ouro']} ouro, +{c['xp']} XP)")
    liberados = [t for t, d in TITULOS_DEF.items()
                 if jogador.nivel >= d["req_nivel"] and (d["conquista"] is None or jogador.conquistas.get(d["conquista"]))]
    melhor = max(liberados, key=lambda t: TITULOS_DEF[t]["bonus_atq"] + TITULOS_DEF[t]["bonus_def"])
    if melhor != jogador.titulo_ativo:
        jogador.titulo_ativo = melhor
        jogador._recalcular()
        linhas.append(f"🎖️  Novo título: {melhor} — {TITULOS_DEF[melhor]['status']}")
    return linhas

# ---------- Andares ----------
ANDARES = {
    1: {"nome":"Porto & Floresta","chefe":"Goblin Sombrio","req_nivel":1,"req_flag":"pescador_falado","salas":["Porto","Floresta"],"recompensa":"Crista do Goblin"},
    2: {"nome":"Castelo do Rei","chefe":"Guardião Real","req_nivel":3,"req_flag":"crista_pegada","salas":["Porto","Castelo"],"recompensa":"Coroa do Guardião"},
    3: {"nome":"Caverna do Dragão","chefe":"Dragão Antigo","req_nivel":5,"req_flag":"portao_aberto","salas":["Porto","Caverna"],"recompensa":"Escama do Dragão"},
    4: {"nome":"Templo Antigo","chefe":"Cumulador","req_nivel":7,"req_flag":"manuscrito_lido","salas":["Porto","Templo"],"recompensa":"Relíquia Antiga"},
    5: {"nome":"Abismo","chefe":"Rei das Sombras","req_nivel":10,"req_flag":"dragao_derrotado","salas":["Porto","Abismo"],"recompensa":"Cristal da Sombra"},
}

# Flags que viram True ao vencer o chefe de cada andar (destravam o próximo)
CHEFE_FLAGS = {
    1: ["goblin_derrotado", "crista_pegada"],
    2: ["portao_aberto"],
    3: ["dragao_derrotado"],
    4: [],
    5: [],
}

# Eventos de história que destravam andares no modo idle (flag -> texto/itens)
HISTORIA = {
    "pescador_falado": {
        "texto": ['🎣 Pescador: "Se você me ajudar, te darei o caminho."',
                  "📜 Missão 'O Mar Escuro' ativada. Ele te entrega uma chave e um manuscrito."],
        "itens": ["Chave do Castelo", "Manuscrito Antigo"],
    },
    "manuscrito_lido": {
        "texto": ["📖 À luz das velas do Templo, a tinta do manuscrito volta a aparecer.",
                  "📖 É um mapa. Uma escada desce para onde o Cumulador espera."],
    },
}

MONSTROS = {
    1: ["Goblin da Floresta", "Lobo Magro", "Caranguejo Gigante"],
    2: ["Soldado Fantasma", "Rato do Castelo", "Armadura Vazia"],
    3: ["Morcego de Brasa", "Kobold Mineiro", "Filhote de Dragão"],
    4: ["Sacerdote Oco", "Estátua Viva", "Acólito Cego"],
    5: ["Sombra Errante", "Eco do Abismo", "Olho Sem Fundo"],
}

FALAS_IDLE = {
    1: ["🐈 Um gato rouba um peixe da sua bolsa. Você deixa.",
        "🔔 O sino do porto toca três vezes. Ninguém sabe por quê."],
    2: ["🏰 Um estandarte rasgado bate no vento. O brasão do Rei está apagado.",
        "🗝️ A chave do castelo esquenta no seu bolso."],
    3: ["🔥 O chão da caverna está morno. Algo grande respira lá embaixo.",
        "💎 Escamas antigas brilham entre as pedras."],
    4: ["🕯️ As velas do Templo acendem sozinhas quando você passa.",
        "🙏 Alguém deixou uma oferenda fresca no altar vazio."],
    5: ["🌑 No Abismo não há eco. Seus passos somem antes de chegar ao chão.",
        "👁️ Você tem a impressão de que a escuridão também está subindo."],
}

def stats_chefe(jogador):
    """(vida, ataque) do chefe do andar atual, escalando com a volta na torre."""
    e = jogador.escala()
    return int((40 + jogador.andar * 30) * e), int((10 + jogador.andar * 5) * e)

def vencer_chefe(jogador):
    """Recompensa, flags e avanço de andar. Retorna as linhas a mostrar.
    Depois do Andar 5 começa uma nova volta na torre (mais difícil e mais rica)."""
    n = jogador.andar
    info = ANDARES[n]
    linhas = []
    jogador.adicionar_item(info.get("recompensa", "Troféu"), 1)
    for f in CHEFE_FLAGS.get(n, []):
        jogador.flags[f] = True
    jogador.ganhar_xp(int(50 * n * jogador.escala()), silencioso=True)
    linhas.append(f"🎁 Recompensa: {info.get('recompensa', 'Troféu')}")
    if n < 5:
        jogador.andar += 1
        linhas.append(f"🏛️  Você sobe para o Andar {jogador.andar}: {ANDARES[jogador.andar]['nome']}")
    else:
        jogador.ciclo += 1
        jogador.andar = 1
        for f in jogador.flags:
            jogador.flags[f] = False
        linhas.append(f"🌀 O Rei das Sombras cai. A torre gira. Volta {jogador.ciclo} começa no Porto.")
    jogador._recalcular()
    return linhas

def desenhar_torre(jogador):
    # Mapa vertical de andares
    digitar("=== 🏛️ TORRE / ANDARES ===")
    for i in range(5, 0, -1):
        info = ANDARES[i]
        status = "✅ ABERTO" if jogador.andar >= i else "🔒 BLOQUEADO"
        # Se está no andar atual, destaca
        arrow = " <-- VOCÊ" if jogador.andar == i else ""
        # Chefe derrotado?
        chefe_ok = jogador.andar > i
        chefe_s = "👑 DERROTADO" if chefe_ok else "👑 PENDENTE"
        print(f"Andar {i} [{status}] — {info['nome']} | Chefe: {info['chefe']} [{chefe_s}]{arrow}")
    print()
    print("Salas disponíveis neste andar:", ", ".join(ANDARES[jogador.andar]["salas"]))

# ---------- Combate ----------
def combate(jogador, nome, vida_inimigo, atq_inimigo):
    """Combate por turnos. Bônus de Escudo/Impulso/Defender valem só no turno — nada fica permanente."""
    v_inim = vida_inimigo
    turnos = 0
    while v_inim > 0 and jogador.vida > 0:
        jogador.aplicar_passivas()
        jogador.mana = min(jogador.mana_max, jogador.mana + 1 + jogador.atributos["inteligencia"] // 5)
        turnos += 1
        limpar()
        digitar(f"⚔️  COMBATE: {nome} (Andar {jogador.andar})")
        digitar(f"Você: {jogador.vida} HP | Inimigo: {v_inim} HP | Mana: {jogador.mana}/{jogador.mana_max} | XP: {jogador.xp}")
        bonus_def = 0
        bonus_atq = 0
        if jogador.escudo_ativo > 0:
            bonus_def = FEITICOS["Escudo Arcano"]["def_bonus"]; digitar("[🛡️ Escudo Arcano ativo!]")
        if jogador.impulso_ativo > 0:
            bonus_atq = FEITICOS["Impulso"]["atq_bonus"]; digitar("[⚡ Impulso ativo!]")
        print("[A]tacar [D]efender [C]urar [M]agia [S]tatus [I]nventário [F]ugir")
        acao = input("Ação: ").strip().upper()
        if acao == "S":
            digitar(f"Nível: {jogador.nivel} | Atributos: F={jogador.atributos['forca']} D={jogador.atributos['destreza']} I={jogador.atributos['inteligencia']} V={jogador.atributos['vitalidade']} C={jogador.atributos['carisma']}")
            digitar(f"Mana: {jogador.mana} | Feitiços: {', '.join(jogador.feiticos_aprendidos)} | Título: {jogador.titulo_ativo}")
            pausa(); continue
        if acao == "I":
            print("Inventário:", " | ".join([f"{k}x{v}" for k,v in jogador.inven.items()]) if jogador.inven else "Vazio")
            continue
        if acao == "F":
            digitar("Você foge!")
            jogador.escudo_ativo = jogador.impulso_ativo = 0
            return False
        rec = 0
        if acao == "M":
            print("Feitiços:")
            for f in jogador.feiticos_aprendidos:
                info = FEITICOS.get(f,{}); print(f"  - {f} (mana {info.get('custo_mana','?')})")
            nome_f = input("Feitiço: ").strip()
            if jogador.usar_magia(nome_f) and jogador.ultimo_dano:
                v_inim -= jogador.ultimo_dano
            rec = max(0, atq_inimigo - (jogador.def_ + bonus_def))
        elif acao == "A":
            dano = max(3, jogador.atq + bonus_atq - 2 + random.randint(-2,2))
            v_inim -= dano
            rec = max(0, atq_inimigo - (jogador.def_ + bonus_def))
            digitar(f"Você causa {dano}!")
        elif acao == "D":
            rec = max(0, atq_inimigo - (jogador.def_ + bonus_def + 8))
            digitar("Defesa reforçada neste turno!")
        elif acao == "C":
            if jogador.usar_poção(): digitar("Poção usada!")
            else: digitar("Sem poções!")
            rec = max(0, atq_inimigo - (jogador.def_ + bonus_def))
        else:
            digitar("Ação inválida."); pausa(); continue
        if jogador.escudo_ativo > 0: jogador.escudo_ativo -= 1
        if jogador.impulso_ativo > 0: jogador.impulso_ativo -= 1
        if v_inim <= 0:
            jogador.ganhar_xp(20 + jogador.nivel*3)
            jogador.ouro += 10 + jogador.andar*5
            if nome == ANDARES[jogador.andar]["chefe"]:
                digitar("[👑 CHEFE DERROTADO!]")
                for linha in vencer_chefe(jogador):
                    digitar(linha)
            else:
                digitar("Vitória!")
            jogador.escudo_ativo = jogador.impulso_ativo = 0
            pausa(); return True
        if rec:
            jogador.vida -= rec
            digitar(f"{nome} revida: -{rec} HP.")
        pausa()
    jogador.escudo_ativo = jogador.impulso_ativo = 0
    if jogador.vida <= 0:
        digitar("GAME OVER.")
        jogador.vida = max(10, jogador.vida_max//2)
        return False
    return True

# ---------- Cenas ----------
# Cada andar tem sua cena de exploração: NPC/ação de história + sala de combate
CENAS = {
    1: {"titulo":"PORTO","desc":"Cidade de pescadores. Uma taverna, redes secando e uma estrada para a Floresta.",
        "npc":"Falar com o Pescador","sala":"Floresta"},
    2: {"titulo":"CASTELO DO REI","desc":"Muralhas rachadas. Um guardião de armadura enferrujada vigia a ponte.",
        "npc":"Falar com o Guardião","sala":"Pátio"},
    3: {"titulo":"CAVERNA DO DRAGÃO","desc":"O ar é quente e cheira a enxofre. Ossos cobrem o chão.",
        "npc":"Examinar as escamas","sala":"Túneis"},
    4: {"titulo":"TEMPLO ANTIGO","desc":"Colunas sem teto. Velas acesas que ninguém acendeu.",
        "npc":"Ler o Manuscrito no altar","sala":"Claustro"},
    5: {"titulo":"ABISMO","desc":"Não há chão à vista. Só a escada, e o que sobe por ela.",
        "npc":"Escutar a escuridão","sala":"Borda"},
}

def dialogo_pescador(jogador):
    if jogador.flags.get("pescador_falado"):
        digitar('Pescador: "O mar continua escuro. Suba, andante. É lá que está a resposta."')
        return
    digitar('Pescador: "Se você me ajudar, te darei o caminho."')
    print("[1] Aceitar ajudar\n[2] Perguntar sobre a torre\n[3] Ir embora")
    es = input("Escolha: ").strip()
    if es == "1":
        jogador.flags["pescador_falado"] = True
        jogador.dialogo_bom()
        for item in HISTORIA["pescador_falado"]["itens"]:
            jogador.adicionar_item(item, 1)
        jogador.missao_ativa = "O Mar Escuro"
        jogador.ganhar_xp(10)
        digitar("[📜 MISSÃO ATIVADA] 'O Mar Escuro' — ele te entrega uma chave e um manuscrito.")
    elif es == "2":
        digitar('Pescador: "Dizem que quem sobe a torre desce ao fundo do mar. Eu só sei que ninguém voltou."')
        jogador.dialogo_bom()

def dialogo_guardiao(jogador):
    if jogador.flags.get("portao_aberto"):
        digitar('Guardião: "Você de novo. Passe, antes que eu mude de ideia."')
        return
    digitar('Guardião: "Ninguém passa sem ordem do Rei. E o Rei não dá ordens há anos."')
    print("[1] Mostrar o Manuscrito Antigo\n[2] Desafiar o Guardião\n[3] Ir embora")
    es = input("Escolha: ").strip()
    if es == "1":
        if jogador.inven.get("Manuscrito Antigo", 0) <= 0:
            digitar("Você não tem nada que ele queira ver.")
        elif not requisitos_ok(jogador):
            digitar(f'Guardião: "Essa letra... é do Rei. Mas você não sobreviveria lá dentro. Volte no nível {nivel_requerido(jogador)}."')
        else:
            digitar("Ele lê em silêncio. A mão que segura a lança treme.")
            digitar('Guardião: "Essa letra... é do Rei. Vá."')
            jogador.dialogo_bom()
            for linha in vencer_chefe(jogador):
                digitar(linha)
    elif es == "2":
        cena_chefe(jogador)

def ler_manuscrito(jogador):
    if jogador.flags.get("manuscrito_lido"):
        digitar("O mapa continua ali: a escada desce para onde o Cumulador espera.")
        return
    if jogador.inven.get("Manuscrito Antigo", 0) <= 0:
        digitar("Sobre o altar há uma página arrancada. Falta o resto — um manuscrito antigo.")
        digitar("(Dica: o Pescador do Porto tem um; às vezes ele aparece no modo idle.)")
        return
    jogador.flags["manuscrito_lido"] = True
    for linha in HISTORIA["manuscrito_lido"]["texto"]:
        digitar(linha)

def cena_explorar(jogador):
    cena = CENAS[jogador.andar]
    limpar()
    digitar(f"=== {cena['titulo']} (Andar {jogador.andar}, Volta {jogador.ciclo}) ===")
    digitar(cena["desc"])
    print(f"[1] {cena['npc']}")
    print(f"[2] Ir para {cena['sala']} (combate)")
    print("[3] Modo Idle (joga sozinho)")
    print("[4] Usar Magia")
    print("[5] Inventário / Mapa / Status")
    print("[6] Salvar")
    print("[7] Voltar ao Menu")
    es = input("Escolha: ").strip()
    if es == "1":
        if jogador.andar == 1: dialogo_pescador(jogador)
        elif jogador.andar == 2: dialogo_guardiao(jogador)
        elif jogador.andar == 4: ler_manuscrito(jogador)
        else: digitar(random.choice(FALAS_IDLE[jogador.andar]))
        pausa()
    elif es == "2":
        jogador.sala_atual = cena["sala"]
        monstro = random.choice(MONSTROS[jogador.andar])
        e = jogador.escala()
        ok = combate(jogador, monstro, int((15 + jogador.andar * 12) * e), int((5 + jogador.andar * 4) * e))
        if ok and jogador.andar == 1 and random.random() < 0.5:
            jogador.adicionar_item("Crista Azul", 1)
            digitar("Uma crista azul cai do monstro. O chefe do andar ainda espera (menu 2).")
            pausa()
    elif es == "3":
        auto_play(jogador)
    elif es == "4":
        print("Feitiços aprendidos:", ", ".join(jogador.feiticos_aprendidos))
        nome = input("Feitiço (ou 0 para sair): ").strip()
        if nome != "0":
            jogador.usar_magia(nome)
        pausa()
    elif es == "5":
        mostrar_status(jogador)
        pausa()
    elif es == "6":
        salvar_man(jogador)
        pausa()
    jogador.sala_atual = cena["titulo"].title()

def mostrar_status(jogador):
    digitar(f"Volta: {jogador.ciclo} | Andar: {jogador.andar} | Nível: {jogador.nivel} | XP: {jogador.xp}/{jogador.xp_max}")
    digitar(f"Vida: {jogador.vida}/{jogador.vida_max} | Mana: {jogador.mana}/{jogador.mana_max} | ATQ {jogador.atq:.0f} | DEF {jogador.def_:.0f}")
    digitar(f"Atributos: F={jogador.atributos['forca']} D={jogador.atributos['destreza']} I={jogador.atributos['inteligencia']} V={jogador.atributos['vitalidade']} C={jogador.atributos['carisma']}")
    t = TITULOS_DEF[jogador.titulo_ativo]
    digitar(f"Título: {jogador.titulo_ativo} (+{t['bonus_atq']} ATQ / +{t['bonus_def']} DEF) | Passivas: {', '.join(jogador.passivas) or 'nenhuma'}")
    feitas = [c for c, v in jogador.conquistas.items() if v]
    digitar(f"Conquistas ({len(feitas)}/{len(CONQUISTAS_DEF)}): {', '.join(feitas) or 'nenhuma'}")
    print("Inventário:", " | ".join(f"{k} x{v}" for k, v in jogador.inven.items()) or "vazio")
    desenhar_torre(jogador)

def cena_chefe(jogador):
    info = ANDARES[jogador.andar]
    digitar(f"=== CHEFE DO ANDAR {jogador.andar} ===")
    digitar(f"Chefe: {info['chefe']} | Requisitos: Nível {nivel_requerido(jogador)} | Flag: {info.get('req_flag','Nenhum')}")
    if jogador.nivel < nivel_requerido(jogador):
        digitar("Você ainda não tem nível suficiente.")
        pausa(); return
    if info.get("req_flag") and not jogador.flags.get(info["req_flag"]):
        digitar("Você ainda não completou o requisito (flag bloqueada).")
        pausa(); return
    print("[1] Combater Chefe\n[2] Voltar")
    es = input("Escolha: ").strip()
    if es == "1":
        # Dificuldade aumenta com andar e com a volta na torre (recompensa/avanço ficam em combate())
        vida, atq = stats_chefe(jogador)
        combate(jogador, info["chefe"], vida, atq)
    jogador.sala_atual = "Porto"

# ---------- Salvar / Carregar ----------
# Formato .txt estilo GitHub: "Chave: valor" + listas "- [x] flag" e "- item: qt".
# Pode ser editado à mão; linhas que faltam mantêm o valor padrão.
def texto_save(jogador, titulo):
    a = jogador.atributos
    linhas = [
        f"# {titulo}",
        f"Nome: {jogador.nome}",
        f"Classe: {jogador.classe}",
        f"Idade: {jogador.idade}",
        f"Volta: {jogador.ciclo}",
        f"Andar: {jogador.andar}",
        f"Nivel: {jogador.nivel}",
        f"XP: {jogador.xp}",
        f"Vida: {int(jogador.vida)}",
        f"Mana: {int(jogador.mana)}",
        f"Ouro: {jogador.ouro}",
        f"Pontos: {jogador.pontos_atributo}",
        f"Atributos: F={a['forca']} D={a['destreza']} I={a['inteligencia']} V={a['vitalidade']} C={a['carisma']}",
        f"Passivas: {', '.join(jogador.passivas)}",
        f"Conquistas: {', '.join(c for c, v in jogador.conquistas.items() if v)}",
        f"Titulo: {jogador.titulo_ativo}",
        f"Conversas: {jogador.dialogo_positivo}",
        f"UltimoAcesso: {int(time.time())}",
        "",
        "## Flags",
    ] + [f"- [{'x' if v else ' '}] {k}" for k, v in jogador.flags.items()] + [
        "",
        "## Inventário",
    ] + [f"- {item}: {qt}" for item, qt in jogador.inven.items()]
    return "\n".join(linhas) + "\n"

def gravar_save(jogador, caminho, titulo):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto_save(jogador, titulo))

def ler_save(jogador, caminho):
    """Aplica o save no jogador. Retorna o timestamp UltimoAcesso (ou None)."""
    atalhos = {"F": "forca", "D": "destreza", "I": "inteligencia", "V": "vitalidade", "C": "carisma"}
    inteiro = lambda s: int(float(s.split("/")[0].strip()))
    ultimo = None
    inven = {}
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            m = re.match(r"- \[( |x|X)\] (\w+)$", linha)
            if m:
                jogador.flags[m.group(2)] = m.group(1).lower() == "x"
                continue
            m = re.match(r"- (.+):\s*(\d+)$", linha)
            if m:
                inven[m.group(1).strip()] = int(m.group(2))
                continue
            if ":" not in linha or linha.startswith("#"):
                continue
            chave, valor = [p.strip() for p in linha.split(":", 1)]
            try:
                if chave == "Nome" and valor: jogador.nome = valor
                elif chave == "Classe" and valor in FEITICOS_CLASSE:
                    jogador.classe = valor
                    jogador.feiticos_aprendidos = list(FEITICOS_CLASSE[valor])
                elif chave == "Idade": jogador.idade = inteiro(valor)
                elif chave == "Volta": jogador.ciclo = max(1, inteiro(valor))
                elif chave == "Andar": jogador.andar = min(5, max(1, inteiro(valor)))
                elif chave in ("Nivel", "Nível"): jogador.nivel = max(1, inteiro(valor))
                elif chave == "XP": jogador.xp = inteiro(valor)
                elif chave == "Vida": jogador.vida = inteiro(valor)
                elif chave == "Mana": jogador.mana = inteiro(valor)
                elif chave == "Ouro": jogador.ouro = inteiro(valor)
                elif chave == "Pontos": jogador.pontos_atributo = inteiro(valor)
                elif chave == "Atributos":
                    for par in valor.split():
                        k, _, v = par.partition("=")
                        if k in atalhos and v.isdigit():
                            jogador.atributos[atalhos[k]] = int(v)
                elif chave == "Passivas":
                    jogador.passivas = [p.strip() for p in valor.split(",") if p.strip()]
                elif chave == "Conquistas":
                    for c in valor.split(","):
                        if c.strip() in jogador.conquistas:
                            jogador.conquistas[c.strip()] = True
                elif chave in ("Titulo", "Título") and valor in TITULOS_DEF: jogador.titulo_ativo = valor
                elif chave == "Conversas": jogador.dialogo_positivo = inteiro(valor)
                elif chave == "UltimoAcesso": ultimo = inteiro(valor)
            except ValueError:
                pass  # valor estragado na edição manual: mantém o padrão
    if inven:
        jogador.inven = inven
    jogador.xp_max = xp_para_nivel(jogador.nivel)
    jogador._recalcular()
    jogador._desbloquear_passivas(silencioso=True)
    jogador.aplicar_flags_de_progresso()
    return ultimo

def auto_salvar(jogador):
    try:
        gravar_save(jogador, SAVE_AUTO, "Auto Save — Andante")
    except Exception:
        pass

def salvar_man(jogador):
    gravar_save(jogador, SAVE_MANUAL, "Save Manual — Andante")
    digitar(f"[💾 SAVE MANUAL] '{os.path.basename(SAVE_MANUAL)}'")

def carregar_man(jogador):
    if not os.path.exists(SAVE_MANUAL): return False
    ler_save(jogador, SAVE_MANUAL)
    digitar("[📂 LOAD] Carregado.")
    return True

def mostrar_offline(jogador, ultimo):
    if not ultimo:
        return
    r = progresso_offline(jogador, time.time() - ultimo)
    if r:
        minutos, xp, ouro, niveis = r
        digitar(f"[⏳ ENQUANTO VOCÊ ESTAVA FORA] {minutos // 60}h{minutos % 60:02d}min de jornada:")
        digitar(f"   +{xp} XP · +{ouro} ouro" + (f" · +{niveis} nível(is)" if niveis else ""))

# ---------- Menu ----------
def criar_personagem():
    nome = input("Nome do personagem: ").strip() or "Aventurier"
    print("Classes: [G] Guerreiro | [M] Mago | [A] Arqueiro")
    classe_input = input("Classe (G/M/A): ").strip().upper()
    classe = "Mago" if classe_input == "M" else "Arqueiro" if classe_input == "A" else "Guerreiro"
    idade_str = input("Idade (número): ").strip()
    j = Jogador(nome, classe, 1)
    j.idade = int(idade_str) if idade_str.isdigit() else 18
    return j

def menu():
    print(logo_ascii())
    j = None
    # Jogo idle: se já existe progresso, continua direto
    if os.path.exists(SAVE_AUTO):
        try:
            j = Jogador("Temp", "Guerreiro", 1)
            ultimo = ler_save(j, SAVE_AUTO)
            resp = input(f"Continuar com {j.nome} ({j.classe}, Andar {j.andar}, Nível {j.nivel})? [S/n] (N = novo personagem, substitui o auto save): ").strip().upper()
            if resp == "N":
                j = None
            else:
                mostrar_offline(j, ultimo)
                pausa()
        except Exception as e:
            digitar(f"[⚠️ AUTO SAVE ILEGÍVEL] {e} — criando personagem novo.")
            j = None
    if j is None:
        j = criar_personagem()
    while True:
        novidades = checar_conquistas(j)
        auto_salvar(j)
        if novidades:
            for linha in novidades:
                digitar(linha)
            pausa()
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
        print(f"{GN}➜{RESET}  [1] {destaque('Explorar o andar atual', YW)}")
        print(f"{GN}➜{RESET}  [2] {destaque('Enfrentar Chefe do Andar', YW)}")
        print(f"{GN}➜{RESET}  [3] {destaque('Modo Idle — joga sozinho (Q para voltar)', YW)}")
        print(f"{GN}➜{RESET}  [4] {destaque('Magia / Feitiços', YW)}")
        print(f"{GN}➜{RESET}  [5] {destaque('Distribuir Pontos', YW)}")
        print(f"{GN}➜{RESET}  [6] {destaque('Inventário / Mapa / Status', YW)}")
        print(f"{GN}➜{RESET}  [7] {destaque('Salvar', YW)}")
        print(f"{GN}➜{RESET}  [8] {destaque('Carregar', YW)}")
        print(f"{GN}➜{RESET}  [9] {destaque('Sair', YW)}")
        print()
        op = input("Opção: ").strip()
        if op == "1": cena_explorar(j)
        elif op == "2": cena_chefe(j)
        elif op == "3":
            res = auto_play(j)
            limpar()
            digitar(f"[🤖 IDLE PAUSADO] {res['ticks']} passos · {res['batalhas']} batalhas · {res['chefes']} chefes · +{res['xp_ganho']} XP · +{res['ouro_ganho']} ouro")
            pausa()
        elif op == "4":
            print("Feitiços:", ", ".join(j.feiticos_aprendidos))
            nome = input("Feitiço (ou 0): ").strip()
            if nome != "0": j.usar_magia(nome)
            pausa()
        elif op == "5": j.distribuir_pontos(); pausa()
        elif op == "6":
            digitar("=== INVENTÁRIO / STATUS ===")
            mostrar_status(j)
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
    if os.name == 'nt':
        os.system("")  # habilita cores ANSI e redesenho de tela no console do Windows
    try:
        sys.stdout.reconfigure(errors="replace")  # emoji em console sem UTF-8 vira "?" em vez de erro
    except Exception:
        pass
    try:
        menu()
    except KeyboardInterrupt:
        print("\nSaindo...")
