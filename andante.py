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
import os, sys, time, re, random, unicodedata

# ---------- Interface Visual (ASCII + zsh + Cores) ----------
# Import auxiliar de cores (pode ser usado diretamente)
BR = "\033[1m"; RD = "\033[31m"; GN = "\033[32m"; YW = "\033[33m"
BL = "\033[34m"; MG = "\033[35m"; CY = "\033[36m"; WT = "\033[37m"
RESET = "\033[0m"; DIM = "\033[2m"; BOLD = "\033[1m"

def logo_ascii():
    return (f"{YW}{BOLD}"
            "  ▄▀█ █▄ █ █▀▄ ▄▀█ █▄ █ ▀█▀ █▀▀\n"
            "  █▀█ █ ▀█ █▄▀ █▀█ █ ▀█  █  ██▄"
            f"{RESET}\n{DIM}  a torre que se sobe sozinho · idle de terminal{RESET}")

def altura_tela():
    """Linhas do terminal (mínimo 20)."""
    try:
        import shutil
        return max(20, shutil.get_terminal_size((80, 24)).lines)
    except Exception:
        return 24

def largura_tela():
    """Largura útil do terminal (até 90 colunas)."""
    try:
        import shutil
        return max(40, min(90, shutil.get_terminal_size((80, 24)).columns - 2))
    except Exception:
        return 78

def _larguras(texto):
    """(caractere, colunas que ocupa) — emoji contam 2; seletores de variação, 0."""
    for i, ch in enumerate(texto):
        if ch in "‍︎️" or unicodedata.combining(ch):
            yield ch, 0
        elif unicodedata.east_asian_width(ch) in ("W", "F") or texto[i + 1:i + 2] == "️":
            yield ch, 2
        else:
            yield ch, 1

def largura_visivel(texto):
    return sum(w for _, w in _larguras(visivel(texto)))

def cortar(texto, largura=None):
    """Corta uma linha (com cores) para caber no terminal — nada de quebra que bagunça a tela."""
    largura = largura or largura_tela()
    if largura_visivel(texto) <= largura:
        return texto
    saida, usado, i = [], 0, 0
    while i < len(texto):
        m = re.match(r"\033\[[0-9;]*m", texto[i:])
        if m:
            saida.append(m.group()); i += len(m.group()); continue
        ch, w = next(_larguras(texto[i:i + 2]))
        if usado + w > largura - 1:
            break
        saida.append(ch); usado += w; i += 1
    return "".join(saida) + "…" + RESET

def quebrar(texto, recuo=" ", largura=None):
    """Quebra um texto sem cores em linhas que cabem no terminal."""
    import textwrap
    largura = (largura or largura_tela()) - len(recuo)
    return textwrap.wrap(texto, max(20, largura + len(recuo)), initial_indent=recuo,
                         subsequent_indent=" " * len(recuo)) or [recuo]

def secao(titulo="", cor=CY, grossa=False):
    """Linha divisória com título: ── Título ─────── (sem borda direita: emoji não desalinha)."""
    traco = "━" if grossa else "─"
    if not titulo:
        return f"{cor}{traco * largura_tela()}{RESET}"
    return f"{cor}{traco * 2} {BOLD}{titulo}{RESET}{cor} {traco * max(2, largura_tela() - len(titulo) - 4)}{RESET}"

def fmt_num(n):
    """Números curtos de jogo idle: 950, 12,3K, 4,5M, 1,2B."""
    n = int(n)
    for limite, divisor, sufixo in ((999_950_000_000, 10**12, "T"), (999_950_000, 10**9, "B"), (999_950, 10**6, "M"), (10**4, 10**3, "K")):
        if abs(n) >= limite:
            return f"{n / divisor:.1f}{sufixo}".replace(".", ",")
    return str(n)

def visivel(texto):
    """Texto sem códigos de cor (para medir largura)."""
    return re.sub(r"\033\[[0-9;]*m", "", texto)

def colunas(itens, largura_col=None):
    """Junta textos (podem ter cor, sem emoji) em duas colunas alinhadas."""
    largura_col = largura_col or largura_tela() // 2
    linhas = []
    for i in range(0, len(itens), 2):
        par = itens[i:i + 2]
        linhas.append("".join(p + " " * max(1, largura_col - len(visivel(p))) for p in par).rstrip())
    return linhas

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
# (tipo, peso, objeto) — ouro diminuiu para o log não virar só "ganhou ouro"
EVENTOS_AUTO = [
    ("Batalha", 0.45, "Monstro do andar"),
    ("Item", 0.12, "Poção de Vida"),
    ("Ouro", 0.12, "Moedas"),
    ("Diálogo", 0.12, "Fala do andar"),
    ("Trabalho", 0.13, "Trabalho do andar"),
    ("Encontro", 0.06, "Encontro raro"),
]

def limpar():
    try: os.system('cls' if os.name == 'nt' else 'clear')
    except: pass

# Menus respondem a UMA tecla, sem ENTER (ESC = voltar, setas = W/A/S/D).
# Sem terminal (testes, pipe) cai no input() normal. Os scripts de teste desligam com TECLA_UNICA = False.
TECLA_UNICA = True
_SETAS = {"\x1b[A": "W", "\x1b[B": "S", "\x1b[C": "D", "\x1b[D": "A", "\x1bOA": "W", "\x1bOB": "S", "\x1bOC": "D", "\x1bOD": "A"}

def ler_tecla(prompt=" Escolha: "):
    """Lê uma tecla e devolve em MAIÚSCULA ("" = ENTER, "0" = ESC)."""
    if not TECLA_UNICA or not sys.stdin.isatty():
        return input(prompt).strip().upper()
    sys.stdout.write(prompt); sys.stdout.flush()
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch = {"H": "W", "P": "S", "M": "D", "K": "A"}.get(msvcrt.getwch(), "")
    else:
        import termios, tty
        fd = sys.stdin.fileno()
        antigo = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = os.read(fd, 8).decode("utf-8", "ignore")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, antigo)
        ch = _SETAS.get(ch, "0" if ch == "\x1b" else ch[:1] if not ch.startswith("\x1b") else "")
    if ch == "\x03":
        raise KeyboardInterrupt
    if ch in ("\r", "\n"):
        ch = ""
    print(ch if ch.strip() else "")
    return ch.upper()

def pausa(msg=""):
    ler_tecla(f" {DIM}▸ qualquer tecla para continuar{RESET} ")

def paginar(titulo, linhas, cor=YW, no_fim=False, rodape=""):
    """Mostra uma lista longa em páginas do tamanho do terminal. ←/→ (ou A/D, ENTER) navegam, 0/ESC sai."""
    por_pag = max(5, altura_tela() - 5)
    paginas = max(1, -(-len(linhas) // por_pag))
    p = paginas - 1 if no_fim else 0
    while True:
        limpar()
        marca = f" · {p + 1}/{paginas}" if paginas > 1 else ""
        print(secao(f"{titulo}{marca}", cor, grossa=True))
        for l in linhas[p * por_pag:(p + 1) * por_pag]:
            print(cortar(l))
        print(secao())
        nav = f"[←/→] páginas   " if paginas > 1 else ""
        k = ler_tecla(f" {DIM}{nav}[0] voltar{rodape}{RESET} ")
        if k in ("0", "Q") or (k == "" and p == paginas - 1) or (paginas == 1 and k not in ("A", "D")):
            return
        if k in ("D", "", "S") and p < paginas - 1:
            p += 1
        elif k in ("A", "W") and p > 0:
            p -= 1

def menu_opcoes(itens, colunas_n=None):
    """Opções lado a lado em N colunas (rótulos curtos, sem emoji): 4 num terminal de 80, 3 se for estreito."""
    colunas_n = colunas_n or (4 if largura_tela() >= 76 else 3)
    largura = largura_tela() // colunas_n
    linhas = []
    for i in range(0, len(itens), colunas_n):
        grupo = itens[i:i + colunas_n]
        linhas.append("  " + "".join(p + " " * max(1, largura - len(visivel(p))) for p in grupo).rstrip())
    return linhas

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
RITMO_XP = 0.35                            # multiplicador do XP ganho no idle
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
    return nivel_efetivo(jogador) >= nivel_requerido(jogador) and (not flag or jogador.flags.get(flag))

def luta_auto(jogador, vida_inimigo, atq_inimigo, nome=None, chefe=False, elemento=None, regras=()):
    """Resolve uma luta inteira sem input. Retorna (venceu, dano_recebido).
    Usa crítico, efeitos de equipamento, bestiário e (quando liberados) habilidades ativas e grupo.
    `regras` são restrições de torres/dungeons: "sem_pocao", "so_magia", "sem_grupo"."""
    j = jogador
    b = j.bonus
    vida_ini = j.vida
    v = vida_inimigo * (1 - min(50, b.get("chefe_vida", 0)) / 100 if chefe else 1)
    crit, crit_mult = chance_critico(j)
    mult = (1 + b.get("dano", 0) / 100) * (1 + bonus_bestiario(j, nome) / 100)
    regen = b.get("regen", 0) / 100
    luta = nova_luta(j, regras)
    turno = 0
    while v > 0 and j.vida > 0 and turno < 200:
        turno += 1
        dano = acao_luta(j, luta, v, elemento)
        if dano is None:   # ação básica: Bola de Fogo ou ataque
            fogo = j.dano_fogo()
            if ("Bola de Fogo" in j.feiticos_aprendidos and j.mana >= FEITICOS["Bola de Fogo"]["custo_mana"]
                    and (fogo > j.atq or "so_magia" in regras) and v > j.atq):
                j.mana -= FEITICOS["Bola de Fogo"]["custo_mana"]
                dano = fogo * mult_elemento("Fogo", elemento)
            elif "so_magia" in regras:
                dano = j.atq * 0.25
            else:
                dano = max(3, j.atq + random.randint(-3, 3))
        if random.random() < crit + luta["crit_extra"][0]:
            dano *= crit_mult
        if random.random() < b.get("tiro_duplo", 0) / 100:
            dano *= 2
        dano = int(dano * mult * luta["mult_dano"])
        v -= dano
        if dano > j.stats.get("maior_dano", 0):
            j.stats["maior_dano"] = dano
        v -= ataque_grupo(j, luta, elemento)
        if v > 0:
            recebido = max(1, int(atq_inimigo * luta["mult_inimigo"] - j.def_ / 2) + random.randint(-2, 2))
            recebido = defesa_luta(j, luta, recebido)
            j.vida -= recebido
            v -= recebido * luta["reflexo"]
        if regen and j.vida > 0:
            j.vida = min(j.vida_max, j.vida + int(j.vida_max * regen))
        fim_turno_luta(j, luta)
        if j.vida < j.vida_max * 0.3 and j.inven.get("Poção de Vida", 0) > 0 and "sem_pocao" not in regras:
            j.usar_poção()
    return j.vida > 0 and v <= 0, max(0, vida_ini - j.vida)

def mult_elemento(elem_ataque, elem_inimigo):
    """Fraqueza ×1,5 · resistência ×0,6 (tabela ELEMENTOS_INIMIGO)."""
    if not elem_inimigo or not elem_ataque:
        return 1.0
    fraco, forte = ELEMENTOS_INIMIGO.get(elem_inimigo, (None, None))
    return 1.5 if elem_ataque == fraco else 0.6 if elem_ataque == forte else 1.0

# elemento do inimigo -> (fraqueza, resistência)
ELEMENTOS_INIMIGO = {
    "Água": ("Terra", "Fogo"), "Fogo": ("Água", "Fogo"), "Terra": ("Fogo", "Água"),
    "Luz": ("Sombra", "Luz"), "Sombra": ("Luz", "Sombra"),
}
ELEMENTO_ANDAR = {1: "Água", 2: "Terra", 3: "Fogo", 4: "Luz", 5: "Sombra"}



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

FLAG_TEXTO = {
    "pescador_falado": "falar com o Pescador",
    "crista_pegada": "pegar a crista do Goblin",
    "portao_aberto": "abrir o portão do Castelo",
    "manuscrito_lido": "ler o Manuscrito no Templo",
    "dragao_derrotado": "derrotar o Dragão",
}
ESPERA_APOS_DERROTA = 30    # ticks de treino antes de tentar o chefe de novo

def novo_res():
    return {"batalhas": 0, "chefes": 0, "chefes_tentados": 0, "itens": 0, "ouro_ganho": 0,
            "xp_ganho": 0, "eventos": 0, "mortes": 0, "ticks": 0, "compras": 0,
            "destaque": "", "inicio": time.time()}

def tick_idle(jogador, res, log):
    """Um passo do jogo idle (Botas Ligeiras e equipamento dão chance de uma ação extra)."""
    jogador.stats["ticks"] = jogador.stats.get("ticks", 0) + 1
    jogador.stats["ticks_volta"] = jogador.stats.get("ticks_volta", 0) + 1
    _tick_idle(jogador, res, log)
    extra = min(0.6, FORJA["botas"]["por_nivel"] * jogador.forja.get("botas", 0) + jogador.bonus.get("acao_extra", 0) / 100)
    if extra and random.random() < extra:
        _tick_idle(jogador, res, log, extra=True)
    drenar_avisos(jogador, res, log)

def drenar_avisos(jogador, res, log):
    """Passa os avisos (desbloqueios, contratos, itens raros...) para o log do idle."""
    for texto, grande in jogador.avisos:
        log.append(texto); del log[:-30]
        if grande:
            res["destaque"] = texto
    jogador.avisos.clear()

def _tick_idle(jogador, res, log, extra=False):
    def anota(txt, grande=False):
        log.append(txt); del log[:-30]
        if grande:
            res["destaque"] = txt
    escala = jogador.escala()
    info = ANDARES[jogador.andar]
    if not extra:
        # Regeneração, progresso, pontos, conquistas, loja
        jogador.vida = min(jogador.vida_max, jogador.vida + max(2, jogador.vida_max // 40))
        jogador.mana = min(jogador.mana_max, jogador.mana + 1 + jogador.atributos["inteligencia"] // 5)
        jogador.espera_chefe = max(0, getattr(jogador, "espera_chefe", 0) - 1)
        jogador.aplicar_flags_de_progresso()
        atualizar_desbloqueios(jogador)
        renovar_contratos(jogador)
        manutencao_idle(jogador, anota)
        msg = _auto_distribuir(jogador)
        if msg: anota(f"📈 {msg}")
        for linha in checar_conquistas(jogador):
            anota(linha, grande=True)
        if jogador.auto_compra and desbloqueado(jogador, "forja"):
            comprado = auto_comprar(jogador)
            if comprado:
                res["compras"] += 1
                anota(f"🔨 Forja: {FORJA[comprado]['nome']} nível {jogador.forja[comprado]}")
    # Chefe: luta sozinho quando os requisitos batem, a vida está boa e não acabou de perder
    limite = 0.5 if "Teleporte Andar" in jogador.passivas else 0.8
    if requisitos_ok(jogador) and jogador.vida >= jogador.vida_max * limite and not jogador.espera_chefe:
        vida_c, atq_c = stats_chefe(jogador)
        res["chefes_tentados"] += 1
        andar = jogador.andar
        venceu, dano = luta_auto(jogador, vida_c, atq_c, nome=info["chefe"], chefe=True, elemento=ELEMENTO_ANDAR.get(andar))
        if venceu:
            res["chefes"] += 1
            anota(f"👑 {info['chefe']} derrotado! (-{fmt_num(dano)} HP)", grande=True)
            marcar_abates(jogador)
            linha_loot = loot_vitoria(jogador, chefe=True, andar=andar)
            for linha in vencer_chefe(jogador):
                anota(linha)
            if linha_loot:
                anota(linha_loot)
            if jogador.andar == 1:
                res["destaque"] = f"🌀 Volta {jogador.ciclo} começou! A torre está mais forte — e paga mais."
        else:
            jogador.vida = max(1, jogador.vida_max // 3)
            jogador.espera_chefe = ESPERA_APOS_DERROTA
            anota(f"💀 {info['chefe']} venceu. Treine e fortaleça-se na Forja.", grande=True)
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
            guardar_item(jogador, item)
        res["eventos"] += 1
        return
    tipo = random.choices([e[0] for e in EVENTOS_AUTO], weights=[e[1] for e in EVENTOS_AUTO], k=1)[0]
    if tipo == "Batalha":
        monstro = random.choice(MONSTROS[jogador.andar])
        venceu, dano = luta_auto(jogador, *stats_monstro(jogador), nome=monstro, elemento=ELEMENTO_ANDAR.get(jogador.andar))
        res["batalhas"] += 1
        if venceu:
            registrar_abate(jogador, monstro)
            xp_base = random.randint(10, 25) * jogador.andar * escala * RITMO_XP
            nivel_antes, xp_antes = jogador.nivel, jogador.xp
            subiu = jogador.ganhar_xp(xp_base, silencioso=True)
            ouro = jogador.ganhar_ouro(random.randint(5, 15) * jogador.andar * escala)
            res["ouro_ganho"] += ouro; res["xp_ganho"] += int(xp_base * jogador.mult_xp())
            anota(f"⚔️  {monstro} vencido: +{fmt_num(xp_base * jogador.mult_xp())} XP, +{fmt_num(ouro)} ouro"
                  + (f" (-{fmt_num(dano)} HP)" if dano else ""))
            if subiu:
                anota(f"🌟 LEVEL UP! Nível {jogador.nivel}", grande=True)
            linha_loot = loot_vitoria(jogador)
            if linha_loot:
                anota(linha_loot)
        else:
            res["mortes"] += 1
            jogador.vida = max(1, jogador.vida_max // 2)
            anota(f"💀 {monstro} te derrubou. Você acorda no Porto.")
    elif tipo == "Item":
        item = random.choices(["Poção de Vida", "Crista Azul", "Manuscrito Antigo"], weights=[6, 2, 1], k=1)[0]
        res["itens"] += 1
        vendido = guardar_item(jogador, item)
        res["ouro_ganho"] += vendido
        anota(f"🎒 Encontrou: {item}" + (f" (bolsa cheia: vendido por {fmt_num(vendido)} ouro)" if vendido else ""))
    elif tipo == "Ouro":
        qt = jogador.ganhar_ouro(random.randint(5, 15) * jogador.andar * escala)
        res["ouro_ganho"] += qt
        anota(f"💰 +{fmt_num(qt)} ouro largado no caminho")
    elif tipo == "Diálogo":
        res["eventos"] += 1
        if jogador.grupo and random.random() < 0.4:
            anota(random.choice(COMPANHEIROS[random.choice(jogador.grupo)]["falas"]))
        else:
            anota(random.choice(FALAS_IDLE.get(jogador.andar, FALAS_IDLE[1])))
    elif tipo == "Trabalho":
        xp_base = random.randint(5, 15) * jogador.andar * RITMO_XP
        if jogador.ganhar_xp(xp_base, silencioso=True):
            anota(f"🌟 LEVEL UP! Nível {jogador.nivel}", grande=True)
        res["xp_ganho"] += int(xp_base * jogador.mult_xp())
        anota(f"{TRABALHOS[jogador.andar]}: +{fmt_num(xp_base * jogador.mult_xp())} XP")
    elif tipo == "Encontro":
        e = random.choice(ENCONTROS)
        res["eventos"] += 1
        partes = []
        if e.get("ouro"):
            qt = jogador.ganhar_ouro(e["ouro"] * jogador.andar * escala); res["ouro_ganho"] += qt
            partes.append(f"+{fmt_num(qt)} ouro")
        if e.get("xp"):
            xp_base = e["xp"] * jogador.andar * escala * RITMO_XP
            jogador.ganhar_xp(xp_base, silencioso=True); res["xp_ganho"] += int(xp_base * jogador.mult_xp())
            partes.append(f"+{fmt_num(xp_base * jogador.mult_xp())} XP")
        if e.get("cura"):
            jogador.vida = min(jogador.vida_max, jogador.vida + int(jogador.vida_max * e["cura"]))
            partes.append("vida recuperada")
        anota(f"{e['texto']} ({', '.join(partes)})")

def _linha_torre(jogador):
    partes = []
    for i in range(1, 6):
        if jogador.andar > i: partes.append(f"{GN}{i} ✔{RESET}")
        elif jogador.andar == i: partes.append(f"{YW}{BOLD}{i} ▶{RESET}")
        else: partes.append(f"{DIM}{i} ·{RESET}")
    return f"{DIM} ─ {RESET}".join(partes)

def _rumo_ao_chefe(jogador):
    """Fração do caminho até poder enfrentar o chefe (nível + flag)."""
    req = nivel_requerido(jogador)
    if nivel_efetivo(jogador) >= req:
        frac_nivel = 1.0
    else:
        base = req - NIVEIS_POR_VOLTA if jogador.ciclo > 1 else 1
        feito = (nivel_efetivo(jogador) - base) + jogador.xp / max(1, jogador.xp_max)
        frac_nivel = max(0.0, min(1.0, feito / max(1, req - base)))
    flag = ANDARES[jogador.andar].get("req_flag")
    flag_ok = not flag or jogador.flags.get(flag)
    return frac_nivel * (1.0 if flag_ok else 0.9)

def _cor_poder(p):
    cor = GN if p >= 1.2 else YW if p >= 1.0 else RD
    return f"{cor}{BOLD}{p:.1f}×{RESET}".replace(".", ",")

def _resumo_forja(jogador):
    curtos = {"arma": "Lâmina", "armadura": "Armadura", "coracao": "Amuleto", "sorte": "Sorte", "estudo": "Diário", "botas": "Botas"}
    return " · ".join(f"{curtos[k]} {jogador.forja.get(k, 0)}" for k in FORJA)



def linhas_progresso_idle(j):
    """Forja, equipamento, contratos e grupo — uma linha cada, na ordem de importância."""
    linhas = []
    abertos = [c for c in j.contratos if not c["feito"]]
    if abertos:
        c = max(abertos, key=lambda c: c["prog"] / c["qt"])
        linhas.append(f" Contrato {barra(c['prog'], c['qt'], 8, CY)} {fmt_num(c['prog'])}/{fmt_num(c['qt'])} {c['texto']}")
    for extra in LINHAS_IDLE_EXTRA:
        linhas += extra(j)
    if j.equip:
        melhor = max(j.equip.values(), key=lambda it: it["rank"])
        linhas.append(f" Equip {len(j.equip)}/{len(SLOTS)} · melhor {fmt_item(melhor)}")
    if desbloqueado(j, "forja"):
        linhas.append(f" Forja {_resumo_forja(j)}" + ("" if j.auto_compra else f" {DIM}(auto-compra desligada){RESET}"))
    return [secao("Progresso")] + linhas if linhas else []

def desenhar_idle(jogador, res, log, velocidade):
    """Painel do idle: cabe na altura do terminal e nenhuma linha passa da largura (senão a tela rola e pisca)."""
    j = jogador
    info = ANDARES[j.andar]
    vida_c, atq_c = stats_chefe(j)
    flag = info.get("req_flag")
    req = nivel_requerido(j)
    ok = lambda b: f"{GN}✔{RESET}" if b else f"{RD}✘{RESET}"
    minutos = max(1 / 60, (time.time() - res.get("inicio", time.time())) / 60)
    taxa = f" {DIM}+{fmt_num(res['ouro_ganho'] / minutos)}/min{RESET}" if minutos >= 0.25 else ""
    cond = f"Nv {req} {ok(nivel_efetivo(j) >= req)}"
    if flag and not j.flags.get(flag):
        cond += f" · falta {FLAG_TEXTO.get(flag, flag)}"
    espera = f" {DIM}(treinando {j.espera_chefe}){RESET}" if getattr(j, "espera_chefe", 0) else ""
    rumo = _rumo_ao_chefe(j)
    topo = [
        secao(f"ANDANTE · IDLE · Volta {j.ciclo}", YW, grossa=True),
        f" {BOLD}{j.nome}{RESET} · {j.classe}{linha_classe_extra(j)} · Nv {BOLD}{j.nivel}{RESET} · {CY}{j.titulo_ativo}{RESET}",
        f" Vida {barra(j.vida, j.vida_max, 14, GN)} {fmt_num(j.vida)}/{fmt_num(j.vida_max)}"
        f"  Mana {barra(j.mana, j.mana_max, 8, MG)} {fmt_num(j.mana)}",
        f" XP   {barra(j.xp, j.xp_max, 14, YW)} {fmt_num(j.xp)}/{fmt_num(j.xp_max)}  Ouro {YW}{BOLD}{fmt_num(j.ouro)}{RESET}{taxa}",
        secao(f"Andar {j.andar}: {info['nome']}"),
        f" {_linha_torre(j)}   {MG}✦ {j.fragmentos}{RESET}  {CY}◎ {j.conchas}{RESET}",
        f" {BOLD}{info['chefe']}{RESET} · {cond} · Poder {_cor_poder(poder_contra(j, vida_c, atq_c))}{espera}",
        f" Rumo ao chefe {barra(rumo, 1, 20, CY)} {int(rumo * 100)}%",
    ]
    meio = linhas_progresso_idle(j)
    escolha = linhas_escolha(j)
    eventos = [secao("Eventos"),
               f" {YW}{BOLD}★ {res['destaque']}{RESET}" if res.get("destaque") else f" {DIM}★ os grandes momentos aparecem aqui{RESET}"]
    rodape = [secao(), f" {DIM}[Q] menu   [+/-] velocidade {str(velocidade).replace('.', ',')}s   "
                       f"[A] auto-compra {'ligada' if j.auto_compra else 'desligada'}{RESET}"]
    altura = altura_tela() - 1
    fixo = len(topo) + len(escolha) + len(eventos) + len(rodape)
    while meio and fixo + len(meio) + 2 > altura:   # tela baixa: some primeiro o que é menos importante
        meio.pop()
    if len(meio) == 1:
        meio = []
    n_log = max(1, altura - fixo - len(meio))
    corpo = [f"   {l}" for l in log[-n_log:]] + [""] * (n_log - len(log[-n_log:]))
    linhas = topo + meio + escolha + eventos + corpo + rodape
    sys.stdout.write("\033[H" + "\n".join(cortar(l) + "\033[K" for l in linhas[:altura]) + "\033[J")
    sys.stdout.flush()

def auto_play(jogador, passos=None, velocidade=1.0, desenhar=True):
    """Modo idle: joga sozinho para sempre, até você apertar Q (ou Ctrl+C).
    `passos` limita os ticks (usado em testes); `velocidade` = segundos por tick."""
    res = novo_res()
    log = ["🤖 Modo idle iniciado. O andante segue sozinho."]
    sair = False
    jogador.idle_interativo = desenhar
    if desenhar:
        sys.stdout.write("\033[2J\033[?25l")   # limpa uma vez e esconde o cursor (sem piscar)
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
                    redesenhar = False
                    for t in teclado.ler():
                        if t.lower() == "q":
                            sair = True
                        elif t in "123" and jogador.escolha_pendente:
                            resolver_escolha(jogador, int(t) - 1); drenar_avisos(jogador, res, log); redesenhar = True
                        elif t.lower() == "a":
                            jogador.auto_compra = not jogador.auto_compra; redesenhar = True
                        elif t in ("+", "="):
                            velocidade = min((v for v in VELOCIDADES if v < velocidade), default=velocidade, key=lambda v: velocidade - v); redesenhar = True
                        elif t in ("-", "_"):
                            velocidade = min((v for v in VELOCIDADES if v > velocidade), default=velocidade, key=lambda v: v - velocidade); redesenhar = True
                    if redesenhar and desenhar and not sair:
                        desenhar_idle(jogador, res, log, velocidade)
                    if time.time() >= fim:
                        break
                    time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    jogador.idle_interativo = False
    if desenhar:
        sys.stdout.write("\033[?25h\n"); sys.stdout.flush()
    auto_salvar(jogador)
    return res

def eficiencia_offline(jogador):
    return min(1.0, OFFLINE_EFICIENCIA + ALTAR["eco"]["por_nivel"] * jogador.altar.get("eco", 0))

def limite_offline_min(jogador):
    return OFFLINE_MAX_MIN + 60 * jogador.altar.get("eco", 0)

def progresso_offline(jogador, segundos):
    """Ganhos enquanto o jogo estava fechado. Retorna um dict com o resumo (ou None)."""
    minutos = min(int(segundos // 60), limite_offline_min(jogador))
    if minutos < 1:
        return None
    ef = eficiencia_offline(jogador)
    # Média do idle aberto por minuto: ~480 XP e ~360 ouro por andar (60 passos)
    xp_base = minutos * 480 * jogador.andar * jogador.escala() * RITMO_XP * ef
    ouro_base = minutos * 360 * jogador.andar * jogador.escala() * ef
    nivel_antes = jogador.nivel
    ouro = jogador.ganhar_ouro(ouro_base)
    jogador.ganhar_xp(xp_base, silencioso=True)
    _auto_distribuir(jogador)
    compras = 0
    while jogador.auto_compra and desbloqueado(jogador, "forja") and compras < 500 and auto_comprar(jogador):
        compras += 1
    baus = min(12, minutos // 60)   # um Baú de Bronze por hora fora
    for _ in range(baus):
        guardar_bau(jogador, "Baú de Bronze")
    extras = [linha for f in OFFLINE_EXTRA for linha in f(jogador, minutos)]
    atualizar_desbloqueios(jogador)
    jogador.vida = jogador.vida_max; jogador.mana = jogador.mana_max
    return {"minutos": minutos, "xp": int(xp_base * jogador.mult_xp()), "ouro": ouro,
            "niveis": jogador.nivel - nivel_antes, "compras": compras, "eficiencia": ef,
            "limitado": segundos // 60 > minutos, "baus": baus, "extras": extras}



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
    return int(35 * nivel ** 2.7 * (1.5 if nivel > NIVEL_MORTAL else 1))

FEITICOS_CLASSE = {
    "Guerreiro": ["Bola de Fogo","Escudo Arcano"],
    "Mago": ["Bola de Fogo","Cura","Restauração"],
    "Arqueiro": ["Bola de Fogo","Impulso"],
}

# Bônus de cada classe somados em _recalcular()
CLASSES = {
    "Guerreiro": {"vida":40,"atq":4,"def":4,"mana":-20,"ouro":0,"pocoes":1},
    "Mago":      {"vida":-10,"atq":-4,"def":0,"mana":40,"ouro":0,"pocoes":2},
    "Arqueiro":  {"vida":10,"atq":2,"def":2,"mana":0,"ouro":10,"pocoes":1},
}

# Passivas com bônus fixo de status (as de efeito por turno ficam em aplicar_passivas)
PASSIVAS_BONUS = {
    "Ataque Duplo": {"atq":3},
    "Esquiva Rápida": {"def":2},
    "Visão Noturna": {"atq":1},
    "Fortalecimento": {"atq":5},
}

# ---------- Forja (gasto de ouro) ----------
# custo = base * cresc^nivel; efeito = por_nivel * nivel (percentual, exceto botas)
FORJA = {
    "arma":     {"nome":"Lâmina Afiada",      "efeito":"ATQ",    "por_nivel":0.08, "base":40,  "cresc":1.32},
    "armadura": {"nome":"Armadura Reforçada", "efeito":"DEF",    "por_nivel":0.08, "base":40,  "cresc":1.32},
    "coracao":  {"nome":"Amuleto do Coração", "efeito":"Vida",   "por_nivel":0.10, "base":60,  "cresc":1.34},
    "sorte":    {"nome":"Moeda da Sorte",     "efeito":"ouro",   "por_nivel":0.10, "base":100, "cresc":1.39},
    "estudo":   {"nome":"Diário de Bordo",    "efeito":"XP",     "por_nivel":0.06, "base":150, "cresc":1.41},
    "botas":    {"nome":"Botas Ligeiras",     "efeito":"ação extra", "por_nivel":0.04, "base":300, "cresc":1.50, "max":15},
}

# ---------- Altar dos Fragmentos (prestígio: bônus permanentes) ----------
# custo em fragmentos = 2 + 2*nivel; sem auto-compra: é a decisão do jogador
ALTAR = {
    "ancestral": {"nome":"Força Ancestral",  "desc":"+10% ATQ e DEF",                    "por_nivel":0.10},
    "ganancia":  {"nome":"Ganância",         "desc":"+20% ouro",                         "por_nivel":0.20},
    "sabedoria": {"nome":"Sabedoria",        "desc":"+15% XP",                           "por_nivel":0.15},
    "eco":       {"nome":"Eco do Andante",   "desc":"+10% offline (máx 100%) e +1h de limite", "por_nivel":0.10, "max":5},
}
FRAGMENTOS_CHEFE = 1        # por chefe vencido
FRAGMENTOS_REI = 3          # pelo Rei das Sombras (fim da volta)

# ---------- Tralhas: o que passa do limite é vendido sozinho ----------
LIMITE_ITEM = {"Poção de Vida": 10, "Crista Azul": 1, "Manuscrito Antigo": 1, "Chave do Castelo": 1}
PRECO_ITEM = {"Poção de Vida": 8, "Crista Azul": 25, "Manuscrito Antigo": 30, "Chave do Castelo": 15}
PRECO_TROFEU = 60           # recompensa de chefe repetida (x andar)

def custo_forja(jogador, chave):
    f = FORJA[chave]
    return int(f["base"] * f["cresc"] ** jogador.forja.get(chave, 0))

def custo_altar(jogador, chave):
    return 2 + 2 * jogador.altar.get(chave, 0)

def forja_no_maximo(jogador, chave):
    return jogador.forja.get(chave, 0) >= FORJA[chave].get("max", 10**9)

def comprar_forja(jogador, chave):
    """Compra 1 nível na Forja. Retorna o custo pago ou 0 se não deu."""
    custo = custo_forja(jogador, chave)
    if forja_no_maximo(jogador, chave) or jogador.ouro < custo:
        return 0
    jogador.ouro -= custo
    jogador.forja[chave] = jogador.forja.get(chave, 0) + 1
    jogador._recalcular()
    return custo

def comprar_altar(jogador, chave):
    custo = custo_altar(jogador, chave)
    if jogador.altar.get(chave, 0) >= ALTAR[chave].get("max", 10**9) or jogador.fragmentos < custo:
        return 0
    jogador.fragmentos -= custo
    jogador.altar[chave] = jogador.altar.get(chave, 0) + 1
    jogador._recalcular()
    return custo

def auto_comprar(jogador):
    """Compra o upgrade mais barato da Forja que couber no bolso (usado pelo idle)."""
    opcoes = [(custo_forja(jogador, k), k) for k in FORJA if not forja_no_maximo(jogador, k)]
    if not opcoes:
        return None
    custo, chave = min(opcoes)
    if comprar_forja(jogador, chave):
        return chave
    return None

def guardar_item(jogador, item, qt=1):
    """Adiciona item; o que passar do limite vira ouro. Retorna o ouro ganho com a venda."""
    jogador.adicionar_item(item, qt)
    return vender_excesso(jogador, [item])

def vender_excesso(jogador, itens=None):
    trofeus = {info["recompensa"]: n for n, info in ANDARES.items()}
    ganho = 0
    for item in list(itens or jogador.inven.keys()):
        qt = jogador.inven.get(item, 0)
        if item in LIMITE_ITEM:
            limite, preco = LIMITE_ITEM[item], PRECO_ITEM[item] * jogador.andar
        elif item in trofeus:
            limite, preco = 1, PRECO_TROFEU * trofeus[item]
        else:
            continue
        if qt > limite:
            ganho += jogador.ganhar_ouro((qt - limite) * preco)
            jogador.inven[item] = limite
    return ganho

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
        # Economia: Forja (ouro), Altar (fragmentos de prestígio)
        self.forja = {k: 0 for k in FORJA}
        self.altar = {k: 0 for k in ALTAR}
        self.fragmentos = 0
        self.auto_compra = True
        self.espera_chefe = 0  # ticks de treino após perder para o chefe (não é salvo)
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
        self._estado_v3()
        self.vida = 0  # definidos de verdade logo abaixo, após _recalcular()
        self._desbloquear_passivas()
        self._recalcular()
        self.vida = self.vida_max; self.mana = self.mana_max

    def _estado_v3(self):
        """Estado dos sistemas v3 (docs/PLANEJAMENTO.md). Também zera tudo antes de carregar um save."""
        self.revelados = []      # sistemas já liberados (DESBLOQUEIOS); nunca voltam a fechar
        self.stats = {}          # contadores e recordes (evento())
        self.marcas = {}         # flags permanentes de missões/escolhas (não zeram na volta)
        self.avisos = []         # (texto, grande) esperando para aparecer no idle/menu
        self.diario = []         # Diário de Bordo
        self.bestiario = {}      # monstro -> abates
        self.equip = {}          # slot -> item (dict de gerar_item)
        self.po_forja = 0
        self.conchas = 0
        self.piedade_loot = 0
        self.contratos = []
        self.contratos_renovam = 0
        self.presente_ultimo = 0
        self.presente_seq = 0
        self.bonus = {}
        self.novidades = []      # últimas mensagens mostradas no menu (não vai para o save)
        # Fase 2: habilidades e níveis
        self.habilidades = {}    # nó -> pontos
        self.usos = {}           # ativa -> vezes usada (rank)
        self.rotacao = []
        self.auto_hab = True
        self.subclasse = ""
        self.reset_volta = 0
        self.pontos_hab_extra = 0
        self.maestria = {"atq": 0, "def": 0, "vida": 0}
        self.maestria_foco = "atq"
        # Fase 3: companheiros e missões
        self.companheiros = {}   # cid -> {xp, memorias, afinidade, batalhas}
        self.grupo = []
        self.auto_grupo = True
        self.piedade4 = 0
        self.piedade5 = 0
        self.missoes_ativas = {}   # id -> progresso
        self.missoes_feitas = {}   # id -> escolha (1, 2...) ou 0
        self.escolha_pendente = ""
        self.escolha_prazo = 0
        self.idle_interativo = False

    def _recalcular(self):
        """Status = atributos + nível/andar + bônus da classe + passivas + título.
        Nada aqui acumula: pode ser chamado quantas vezes quiser."""
        a = self.atributos
        c = CLASSES.get(self.classe, CLASSES["Guerreiro"])
        self.bonus = b = calcular_bonus(self)   # equipamento, conjuntos, habilidades, grupo, maestria
        self.vida_max = 50 + a["vitalidade"]*10 + self.nivel*10 + self.andar*5 + c["vida"] + b.get("vida", 0)
        self.atq = 5 + a["forca"]*2 + a["inteligencia"]*0.5 + self.nivel*2 + self.andar*2 + c["atq"] + b.get("atq", 0)
        self.def_ = 3 + a["destreza"]*1.5 + self.nivel + self.andar + c["def"] + b.get("def", 0)
        self.mana_max = 20 + a["inteligencia"]*10 + self.nivel*5 + self.andar*3 + c["mana"] + b.get("mana", 0)
        for p in self.passivas:
            self.atq += PASSIVAS_BONUS.get(p, {}).get("atq", 0)
            self.def_ += PASSIVAS_BONUS.get(p, {}).get("def", 0)
        titulo = TITULOS_DEF.get(self.titulo_ativo, {})
        self.atq += titulo.get("bonus_atq", 0)
        self.def_ += titulo.get("bonus_def", 0)
        # Forja e Altar multiplicam (percentuais)
        forja, altar = getattr(self, "forja", {}), getattr(self, "altar", {})
        ancestral = 1 + ALTAR["ancestral"]["por_nivel"] * altar.get("ancestral", 0)
        self.atq = int(self.atq * (1 + FORJA["arma"]["por_nivel"] * forja.get("arma", 0)) * ancestral)
        self.def_ = int(self.def_ * (1 + FORJA["armadura"]["por_nivel"] * forja.get("armadura", 0)) * ancestral)
        self.vida_max = int(self.vida_max * (1 + FORJA["coracao"]["por_nivel"] * forja.get("coracao", 0)))
        tudo = b.get("tudo", 0)
        self.atq = int(self.atq * (1 + (b.get("atq%", 0) + tudo) / 100))
        self.def_ = int(self.def_ * (1 + (b.get("def%", 0) + tudo) / 100))
        self.vida_max = int(self.vida_max * (1 + (b.get("vida%", 0) + tudo) / 100))
        if self.vida > self.vida_max: self.vida = self.vida_max
        if self.mana > self.mana_max: self.mana = self.mana_max

    def escala(self):
        """Multiplicador de dificuldade/recompensa por volta na torre."""
        return 1 + 0.5 * (self.ciclo - 1)

    def mult_dano(self):
        """Multiplicador da Forja (Lâmina) e do Altar (Força Ancestral) — vale para arma e magia."""
        return ((1 + FORJA["arma"]["por_nivel"] * self.forja.get("arma", 0))
                * (1 + ALTAR["ancestral"]["por_nivel"] * self.altar.get("ancestral", 0)))

    def dano_fogo(self):
        """Dano da Bola de Fogo: Inteligência + nível/andar (como o ataque), vezes Lâmina e Força Ancestral."""
        base = FEITICOS["Bola de Fogo"]["dano"] + self.atributos["inteligencia"] * 3 + self.nivel * 2 + self.andar * 2
        return int(base * self.mult_dano() * (1 + self.bonus.get("fogo_cadeia", 0) / 100))

    def dano_por_turno(self):
        """Dano médio por turno (ataque ou Bola de Fogo), já com crítico e bônus de dano."""
        base = self.atq
        if "Bola de Fogo" in self.feiticos_aprendidos and self.mana_max >= FEITICOS["Bola de Fogo"]["custo_mana"]:
            base = max(self.atq, self.dano_fogo())
        crit, crit_mult = chance_critico(self)
        base *= (1 + crit * (crit_mult - 1)) * (1 + self.bonus.get("dano", 0) / 100) * (1 + self.bonus.get("tiro_duplo", 0) / 100)
        if desbloqueado(self, "habilidades") and rotacao_valida(self):
            base *= 1.35                       # ativas: em média ~35% a mais por turno
        grupo = sum(PODER_FUNCAO[COMPANHEIROS[c]["funcao"]] for c in getattr(self, "grupo", []) if c in COMPANHEIROS)
        return base + self.atq * grupo * (1 + self.bonus.get("comando", 0) / 100)

    def mult_ouro(self):
        return ((1 + FORJA["sorte"]["por_nivel"] * self.forja.get("sorte", 0)) * (1 + ALTAR["ganancia"]["por_nivel"] * self.altar.get("ganancia", 0))
                * (1 + self.bonus.get("ouro%", 0) / 100))

    def mult_xp(self):
        m = (1 + FORJA["estudo"]["por_nivel"] * self.forja.get("estudo", 0)) * (1 + ALTAR["sabedoria"]["por_nivel"] * self.altar.get("sabedoria", 0))
        return m * (1.25 if "Mestre do Andar" in self.passivas else 1) * (1 + self.bonus.get("xp%", 0) / 100)

    def ganhar_ouro(self, qt):
        """Soma ouro já com bônus (Moeda da Sorte, Ganância, equipamento). Retorna o valor ganho."""
        qt = int(qt * self.mult_ouro())
        self.ouro += qt
        if qt > 0:
            evento(self, "ouro", qt)
        return qt

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
        """Soma XP (com bônus de Forja/Altar/Mestre do Andar) e sobe quantos níveis couberem.
        Retorna True se subiu."""
        qt = int(qt * self.mult_xp())
        self.xp += qt
        subiu = False
        while self.xp >= self.xp_max:
            if self.nivel >= nivel_teto(self):
                if self.nivel < NIVEL_MAX:      # teto mortal: espera o Despertar
                    self.xp = self.xp_max
                    break
                self.xp -= self.xp_max          # depois do 120: Maestria
                self.maestria[self.maestria_foco] = self.maestria.get(self.maestria_foco, 0) + 1
                self.xp_max = xp_maestria(self)
                self._recalcular()
                continue
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
        if self.nivel % 10 == 0:   # marco de nível
            guardar_bau(self, "Baú de Ouro")
            avisar(self, f"🎖️  Marco: nível {self.nivel}! Um Baú de Ouro te espera [B].", grande=True)
            anotar_diario(self, f"Chegou ao nível {self.nivel}.")
        if self.nivel >= NIVEL_MAX:
            self.xp_max = xp_maestria(self)
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
            self.ultimo_dano = self.dano_fogo()
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
            print(" Sem pontos para distribuir. Cada nível dá 2 (o idle distribui sozinho)."); pausa(); return
        while self.pontos_atributo > 0:
            a = self.atributos
            print(f" {YW}{self.pontos_atributo} ponto(s){RESET}  F={a['forca']} D={a['destreza']} I={a['inteligencia']} V={a['vitalidade']} C={a['carisma']}")
            a = ler_tecla(f" +1 em [F]orça [D]estreza [I]nteligência [V]italidade [C]arisma · [0] sair: ")
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
# v3: conquistas por categoria, com condição livre ("cond") e Pontos de Lenda ("pts", padrão 5)
_st = lambda j, k: j.stats.get(k, 0)
CONQUISTAS_DEF.update({
    # Combate
    "Cem Abates":         {"cat":"Combate","desc":"Venceu 100 monstros","ouro":30,"xp":40,"pts":5,"cond":lambda j: _st(j,"monstro") >= 100},
    "Mil Abates":         {"cat":"Combate","desc":"Venceu 1.000 monstros","ouro":200,"xp":200,"pts":15,"cond":lambda j: _st(j,"monstro") >= 1000},
    "Dez Mil Abates":     {"cat":"Combate","desc":"Venceu 10.000 monstros","ouro":1000,"xp":1000,"pts":30,"cond":lambda j: _st(j,"monstro") >= 10000},
    "Golpe Pesado":       {"cat":"Combate","desc":"Causou 1.000 de dano num golpe","ouro":50,"xp":50,"pts":10,"cond":lambda j: _st(j,"maior_dano") >= 1000},
    "Golpe de Lenda":     {"cat":"Combate","desc":"Causou 100.000 de dano num golpe","ouro":500,"xp":500,"pts":25,"cond":lambda j: _st(j,"maior_dano") >= 100000},
    "Caçador de Chefes":  {"cat":"Combate","desc":"Venceu 25 chefes","ouro":150,"xp":150,"pts":15,"cond":lambda j: _st(j,"chefe") >= 25},
    # Coleção
    "Primeiro Brilho":    {"cat":"Coleção","desc":"Encontrou um item Raro","ouro":20,"xp":20,"pts":5,"cond":lambda j: _st(j,"maior_rank") >= 2},
    "Roxo no Escuro":     {"cat":"Coleção","desc":"Encontrou um item Épico","ouro":60,"xp":60,"pts":10,"cond":lambda j: _st(j,"maior_rank") >= 3},
    "Coisa de Lenda":     {"cat":"Coleção","desc":"Encontrou um item Lendário","ouro":150,"xp":150,"pts":20,"cond":lambda j: _st(j,"maior_rank") >= 4},
    "Mito":               {"cat":"Coleção","desc":"Encontrou um item Mítico","ouro":500,"xp":500,"pts":40,"cond":lambda j: _st(j,"maior_rank") >= 5},
    "Abridor de Baús":    {"cat":"Coleção","desc":"Abriu 25 baús","ouro":80,"xp":80,"pts":10,"cond":lambda j: _st(j,"bau") >= 25},
    "Conjunto Completo":  {"cat":"Coleção","desc":"Vestiu 4 peças do mesmo conjunto","ouro":120,"xp":120,"pts":20,
                           "cond":lambda j: any(sum(1 for i in j.equip.values() if i.get("conjunto") == c) >= 4 for c in CONJUNTOS)},
    "Estudioso":          {"cat":"Coleção","desc":"50 abates de 10 monstros diferentes","ouro":100,"xp":100,"pts":15,
                           "cond":lambda j: sum(1 for v in j.bestiario.values() if v >= 50) >= 10},
    # História
    "Contratado":         {"cat":"História","desc":"Cumpriu um contrato do Porto","ouro":20,"xp":20,"pts":5,"cond":lambda j: _st(j,"contrato") >= 1},
    "Palavra Cumprida":   {"cat":"História","desc":"Cumpriu 25 contratos","ouro":200,"xp":200,"pts":15,"cond":lambda j: _st(j,"contrato") >= 25},
    "Terceira Volta":     {"cat":"História","desc":"Chegou à Volta 3","ouro":100,"xp":100,"pts":10,"volta":3},
    "Décima Volta":       {"cat":"História","desc":"Chegou à Volta 10","ouro":1000,"xp":1000,"pts":30,"volta":10},
    # Excentricidades
    "Ofensa Mútua":       {"cat":"Excentricidades","desc":"Venceu 100 Caranguejos Gigantes","ouro":40,"xp":40,"pts":5,
                           "cond":lambda j: j.bestiario.get("Caranguejo Gigante", 0) >= 100},
    "Bolso Fundo":        {"cat":"Excentricidades","desc":"Ganhou 1 milhão de ouro no total","ouro":0,"xp":200,"pts":10,"cond":lambda j: _st(j,"ouro") >= 10**6},
    "Volta Relâmpago":    {"cat":"Excentricidades","desc":"Completou uma volta em menos de 15 min","ouro":200,"xp":200,"pts":15,
                           "cond":lambda j: 0 < _st(j,"volta_rapida") <= 900},
})

# Títulos: liberados por conquista + nível; o melhor liberado fica ativo e dá bônus
TITULOS_DEF = {
    "Aventurier": {"req_nivel":1,"conquista":None,"status":"Explorador dos mares.","bonus_atq":0,"bonus_def":0},
    "Caçador de Sombras": {"req_nivel":5,"conquista":"Crista Azul","status":"Possui a Crista Azul.","bonus_atq":3,"bonus_def":2},
    "Guardião do Rei": {"req_nivel":8,"conquista":"Portão Aberto","status":"Passou pelo portão do Castelo.","bonus_atq":5,"bonus_def":5},
    "Matador de Dragões": {"req_nivel":10,"conquista":"Matador de Dragão","status":"O Dragão caiu.","bonus_atq":8,"bonus_def":8},
    "Lenda do Porto": {"req_nivel":15,"conquista":"Dono do Porto","status":"Completou a torre.","bonus_atq":10,"bonus_def":10},
    "Lenda do Cais": {"req_nivel":20,"conquista":None,"req_lenda":120,"status":"120 Pontos de Lenda.","bonus_atq":14,"bonus_def":14},
    "Andante Eterno": {"req_nivel":40,"conquista":None,"req_lenda":300,"status":"300 Pontos de Lenda.","bonus_atq":22,"bonus_def":22},
}

def pontos_lenda(jogador):
    return sum(d.get("pts", 5) for c, d in CONQUISTAS_DEF.items() if jogador.conquistas.get(c))

def checar_conquistas(jogador):
    """Libera conquistas novas (dá ouro/XP) e escolhe o melhor título. Retorna as linhas a mostrar."""
    linhas = []
    for nome, c in CONQUISTAS_DEF.items():
        if jogador.conquistas.get(nome):
            continue
        ok = (all(jogador.flags.get(f) for f in c.get("flags", [])) and jogador.ciclo >= c.get("volta", 1)
              and (not c.get("cond") or c["cond"](jogador)))
        if ok:
            jogador.conquistas[nome] = True
            anotar_diario(jogador, f"Conquista: {nome} — {c['desc']}.")
            jogador.ouro += c["ouro"]
            jogador.ganhar_xp(c["xp"], silencioso=True)
            linhas.append(f"🏆 Conquista: {nome} (+{c['ouro']} ouro, +{c['xp']} XP)")
    lenda = pontos_lenda(jogador)
    liberados = [t for t, d in TITULOS_DEF.items()
                 if jogador.nivel >= d["req_nivel"] and (d["conquista"] is None or jogador.conquistas.get(d["conquista"]))
                 and lenda >= d.get("req_lenda", 0)]
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
        "🔔 O sino do porto toca três vezes. Ninguém sabe por quê.",
        "🌫️ A névoa sobe do mar e esconde a torre por um instante.",
        "🍺 Na taverna, alguém aposta que você não passa do Castelo.",
        "🦀 Um caranguejo te encara de lado, ofendido.",
        "🎣 O Pescador remenda a rede sem tirar os olhos da torre.",
        "🌊 Uma onda traz uma garrafa vazia. Nenhum bilhete. Desta vez.",
        "🪵 As tábuas do cais rangem no mesmo ritmo dos seus passos."],
    2: ["🏰 Um estandarte rasgado bate no vento. O brasão do Rei está apagado.",
        "🗝️ A chave do castelo esquenta no seu bolso.",
        "🪑 O trono está coberto de pó. Só o assento está limpo.",
        "🐀 Ratos marcham em fila pelo corredor, como soldados.",
        "🛡️ Uma armadura vazia vira a cabeça quando você passa.",
        "📯 Uma trombeta toca ao longe. Ninguém a segura.",
        "🍷 Há uma mesa posta para um banquete que nunca começou.",
        "🕸️ As teias no salão formam o desenho de uma coroa."],
    3: ["🔥 O chão da caverna está morno. Algo grande respira lá embaixo.",
        "💎 Escamas antigas brilham entre as pedras.",
        "🦴 Ossos de aventureiros, todos virados para a saída.",
        "💨 Um vento quente sobe pelos túneis e cheira a enxofre.",
        "⛏️ Uma picareta enterrada até o cabo. Alguém desistiu aqui.",
        "🪙 Moedas derretidas grudadas na parede, como gotas de ouro.",
        "🌋 O teto pinga pedra derretida. Você anda mais rápido.",
        "👂 Lá no fundo, um ronco. Ou uma risada."],
    4: ["🕯️ As velas do Templo acendem sozinhas quando você passa.",
        "🙏 Alguém deixou uma oferenda fresca no altar vazio.",
        "📜 Pergaminhos se reescrevem enquanto você lê.",
        "🔔 Um sino sem badalo soa uma vez.",
        "🗿 As estátuas têm o seu rosto. Todas um pouco mais velhas.",
        "🌸 Flores brotam entre as lajes e murcham no mesmo minuto.",
        "🧎 Um acólito cego reza seu nome sem nunca tê-lo ouvido.",
        "⚖️ Uma balança no altar pesa algo que você não vê."],
    5: ["🌑 No Abismo não há eco. Seus passos somem antes de chegar ao chão.",
        "👁️ Você tem a impressão de que a escuridão também está subindo.",
        "🕳️ A escada continua para baixo, embora você esteja subindo.",
        "🌌 Estrelas aparecem no chão, não no céu.",
        "🫧 Bolhas de ar sobem. Você está debaixo d'água? Não parece.",
        "🪞 Seu reflexo anda meio passo atrás de você.",
        "🎐 Um sussurro repete a última coisa que o Pescador disse.",
        "🖤 O frio aqui não vem de fora. Vem da lembrança do porto."],
}

# O "trabalho" de cada andar no idle (troca o antigo "Trabalhou no porto" em todo lugar)
TRABALHOS = {
    1: "🔨 Consertou redes no cais",
    2: "🔨 Poliu armaduras no quartel",
    3: "⛏️  Minerou cristais na caverna",
    4: "📜 Copiou pergaminhos do templo",
    5: "🗺️  Mapeou um trecho da escuridão",
}

# Encontros raros no idle: texto + recompensa (ouro/xp em "por andar", cura em % da vida)
ENCONTROS = [
    {"texto": "🧳 Um mercador ambulante erra o troco a seu favor.", "ouro": 40},
    {"texto": "🩹 Você divide uma poção com um viajante ferido. Ele te ensina um atalho.", "xp": 30},
    {"texto": "🐦 Um corvo deixa cair uma moeda antiga aos seus pés.", "ouro": 25},
    {"texto": "🔥 Uma fogueira abandonada ainda está quente. Você descansa.", "cura": 0.5},
    {"texto": "📖 Um andante anterior deixou anotações na parede. Você aprende algo.", "xp": 45},
    {"texto": "🎲 Três esqueletos jogam dados. Você ganha a rodada.", "ouro": 60},
    {"texto": "🍞 Uma padeira do porto mandou pão. Ninguém sabe como chegou aqui.", "cura": 1.0},
    {"texto": "💰 Um baú sem fechadura. Dentro, só ouro e um bilhete: 'boa sorte'.", "ouro": 90},
]

# Força dos inimigos (ajuste de dificuldade; medir com scripts/ritmo.py)
CHEFE_VIDA = 5.5
CHEFE_ATQ = 3.0
CHEFE_POR_VOLTA = 1.13      # chefes ficam 13% mais fortes a cada volta, além da escala (Forja e Altar precisam acompanhar)
MONSTRO_VIDA = 1.0
MONSTRO_ATQ = 1.0

def stats_chefe(jogador):
    """(vida, ataque) do chefe do andar atual, escalando com a volta na torre."""
    e = jogador.escala() * CHEFE_POR_VOLTA ** (jogador.ciclo - 1)
    return int((40 + jogador.andar * 30) * e * CHEFE_VIDA), int((10 + jogador.andar * 5) * e * CHEFE_ATQ)

def stats_monstro(jogador):
    e = jogador.escala()
    return int((15 + jogador.andar * 12) * e * MONSTRO_VIDA), int((5 + jogador.andar * 4) * e * MONSTRO_ATQ)

def poder_contra(jogador, vida_inimigo, atq_inimigo):
    """Quantas vezes você aguenta mais que o inimigo (>1 = deve vencer).
    Compara turnos para matar x turnos para morrer, com a vida cheia (já com lentidão e efeitos de chefe)."""
    b = jogador.bonus
    vida_inimigo *= 1 - min(50, b.get("chefe_vida", 0)) / 100
    atq_inimigo *= 1 - min(50, b.get("lentidao", 0)) / 100
    turnos_matar = vida_inimigo / max(3, jogador.dano_por_turno())
    dano_recebido = max(1, (atq_inimigo - jogador.def_ / 2) * (1 - min(40, b.get("esquiva", 0)) / 100))
    turnos_morrer = jogador.vida_max / dano_recebido
    return turnos_morrer / max(0.1, turnos_matar)

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
    frag = FRAGMENTOS_REI if n == 5 else FRAGMENTOS_CHEFE
    jogador.fragmentos += frag
    conchas = CONCHAS_REI if n == 5 else CONCHAS_CHEFE
    jogador.conchas += conchas
    vender_excesso(jogador, [info.get("recompensa", "Troféu")])
    guardar_bau(jogador, "Baú de Prata" if n == 5 else "Baú de Bronze")
    linhas.append(f"🎁 Recompensa: {info.get('recompensa', 'Troféu')} · ✦ +{frag} fragmento(s) · +{conchas} conchas · "
                  + ("Baú de Prata" if n == 5 else "Baú de Bronze"))
    evento(jogador, "chefe", andar=n, nome=info["chefe"])
    if jogador.stats.get("chefe", 0) == 1:
        anotar_diario(jogador, f"Venceu o primeiro chefe: {info['chefe']}.")
    if n < 5:
        jogador.andar += 1
        linhas.append(f"🏛️  Você sobe para o Andar {jogador.andar}: {ANDARES[jogador.andar]['nome']}")
    else:
        duracao = jogador.stats.get("ticks_volta", 0)
        if duracao and (not jogador.stats.get("volta_rapida") or duracao < jogador.stats["volta_rapida"]):
            jogador.stats["volta_rapida"] = duracao
        jogador.stats["ticks_volta"] = 0
        jogador.ciclo += 1
        jogador.andar = 1
        for f in jogador.flags:
            jogador.flags[f] = False
        linhas.append(f"🌀 O Rei das Sombras cai. A torre gira. Volta {jogador.ciclo} começa no Porto.")
        anotar_diario(jogador, f"O Rei das Sombras caiu. A torre girou: começa a Volta {jogador.ciclo}.")
        evento(jogador, "volta")
    jogador._recalcular()
    return linhas

CONCHAS_CHEFE = 2           # moeda do Sino do Porto
CONCHAS_REI = 10

def desenhar_torre(jogador):
    """Torre vertical: do Abismo (topo) ao Porto (base)."""
    for i in range(5, 0, -1):
        info = ANDARES[i]
        if jogador.andar > i:
            marca, cor, chefe = "✔", GN, f"{info['chefe']} derrotado"
        elif jogador.andar == i:
            marca, cor, chefe = "▶", YW + BOLD, f"{info['chefe']} espera"
        else:
            marca, cor, chefe = "·", DIM, "fechado"
        print(f"  {cor}│ {marca} Andar {i} · {info['nome']:<18}{RESET} {DIM}{chefe}{RESET}")
    print(f"  {DIM}└─ Porto: o mar escuro lá embaixo · Volta {jogador.ciclo}{RESET}")

# =====================================================================
# v3 · Fase 0 — Desbloqueios, eventos, avisos e Diário (docs/PLANEJAMENTO.md)
# =====================================================================
# Registros onde cada sistema v3 se pendura (assim o núcleo não precisa conhecer todos):
GANCHOS_IDLE = []        # f(j, anota): roda a cada passo do idle
LINHAS_IDLE_EXTRA = []   # f(j) -> [linhas] na seção "Progresso" do painel do idle
DICAS_EXTRA = []         # f(j) -> texto ou None (dica do menu)
OFFLINE_EXTRA = []       # f(j, minutos) -> [linhas] no quadro "enquanto você estava fora"
BLOCOS_SAVE = []         # (título, salvar(j) -> linhas "- ...", carregar(j, linha sem "- "))
CHAVES_SAVE = []         # (salvar(j) -> [(chave, valor)], carregar(j, chave, valor) -> True se reconheceu)

# Cada sistema aparece aos poucos. Condições: nivel / chefes (vencidos na vida toda) / volta / marcas.
# "evento": True = revelado por algo que acontece no jogo (ex.: primeiro item Raro).
# "menu": tecla no menu principal (sem "menu" = melhoria silenciosa, só o aviso).
DESBLOQUEIOS = {
    "forja":       {"nome": "Forja", "menu": "F", "nivel": 3,
                    "texto": "🔨 O ferreiro acende a forja pela primeira vez. Forja liberada [F]."},
    "equipamento": {"nome": "Equipamento", "menu": "E", "evento": True, "dica": "ache um item Raro",
                    "texto": "💠 Algo brilha azul entre os despojos. Equipamento liberado [E]."},
    "baus":        {"nome": "Baús", "menu": "B", "evento": True, "dica": "ganhe um baú",
                    "texto": "🧰 Um baú trancado, pesado de promessa. Baús liberados [B]."},
    "contratos":   {"nome": "Contratos", "menu": "C", "chefes": 1,
                    "texto": "📋 Um quadro de avisos aparece no cais. Contratos liberados [C]."},
    "diario":      {"nome": "Diário", "menu": "J", "chefes": 1,
                    "texto": "📔 Você começa a anotar o caminho. Diário de Bordo liberado [J]."},
    "habilidades": {"nome": "Habilidades", "menu": "H", "nivel": 8,
                    "texto": "🌿 Você sente o corpo aprender sozinho. Árvore de habilidades liberada [H]."},
    "gacha":       {"nome": "Sino do Porto", "menu": "S", "chefes": 2,
                    "texto": "🔔 O sino do porto toca três vezes. Agora você sabe por quê [S]."},
    "grupo":       {"nome": "Grupo", "menu": "G", "chefes": 2,
                    "texto": "🤝 Alguém decide subir com você. Grupo liberado [G]."},
    "passe":       {"nome": "Passe da Torre", "menu": "P", "nivel": 10,
                    "texto": "🎟️  O Pescador te dá um cartão de cortiça com 30 furos. Passe da Torre [P]."},
    "dungeons":    {"nome": "Dungeons", "menu": "D", "nivel": 12,
                    "texto": "🕳️  Debaixo do cais, uma escada que não estava lá. Dungeons liberadas [D]."},
    "recordes":    {"nome": "Recordes", "menu": "R", "chefes": 5,
                    "texto": "📜 Alguém começou a contar seus feitos. Recordes e Bestiário [R]."},
    "altar":       {"nome": "Altar", "menu": "A", "volta": 2,
                    "texto": "✦ Os fragmentos que você guardou começam a zumbir. Altar liberado [A]."},
    "mapa":        {"nome": "Mapa", "menu": "M", "volta": 2,
                    "texto": "🗺️  A torre gira. Lá fora, o mar recua e mostra ilhas. Mapa aberto [M]."},
    "botas":       {"nome": "Botas Ligeiras", "volta": 2,
                    "texto": "👢 O ferreiro tira da prateleira um par de botas leves. Novo na Forja."},
    "heroica":     {"nome": "Dificuldade Heroica", "volta": 2,
                    "texto": "⚔️  As dungeons agora podem ser enfrentadas no Heroico."},
    "grupo2":      {"nome": "2º companheiro", "nivel": 20,
                    "texto": "🤝 Há espaço para mais um no seu grupo."},
    "ramo2":       {"nome": "2º ramo de habilidades", "nivel": 20,
                    "texto": "🌿 Um segundo ramo da sua árvore desperta."},
    "subclasse":   {"nome": "Subclasse", "nivel": 30,
                    "texto": "🎭 Você pode escolher uma subclasse na tela de Habilidades [H]."},
    "torres":      {"nome": "Torres", "menu": "T", "volta": 3,
                    "texto": "🗼 No horizonte, outras torres. Torre Infinita e Torre Afogada [T]."},
    "pesadelo":    {"nome": "Dificuldade Pesadelo", "volta": 4,
                    "texto": "💀 As dungeons agora podem ser enfrentadas no Pesadelo."},
    "torre_vidro": {"nome": "Torre de Vidro", "volta": 5,
                    "texto": "🔷 Uma torre de vidro aparece onde antes havia névoa."},
    "grupo3":      {"nome": "3º companheiro", "nivel": 50,
                    "texto": "🤝 O grupo completo: três andantes e você."},
    "ramo3":       {"nome": "3º ramo de habilidades", "nivel": 50,
                    "texto": "🌿 O último ramo da sua árvore desperta."},
    "despertar":   {"nome": "Despertar", "nivel": 60,
                    "texto": "🌅 Seu corpo chegou ao limite de um mortal. Algo pede mais."},
    "torre_tempo": {"nome": "Torre do Tempo", "nivel": 60,
                    "texto": "⏳ A Torre do Tempo abre. Ela muda toda semana."},
}

def desbloqueado(j, chave):
    return chave in j.revelados

def _cond_ok(j, d):
    if d.get("evento"):
        return False
    return (j.nivel >= d.get("nivel", 0) and j.stats.get("chefe", 0) >= d.get("chefes", 0)
            and j.ciclo >= d.get("volta", 1) and all(j.marcas.get(m) for m in d.get("marcas", [])))

def requisito_texto(chave):
    d = DESBLOQUEIOS[chave]
    if d.get("evento"): return d.get("dica", "descubra")
    if d.get("volta"): return f"Volta {d['volta']}"
    if d.get("nivel"): return f"Nv {d['nivel']}"
    if d.get("chefes"): return f"{d['chefes']} chefe(s)"
    return "?"

def revelar(j, chave, silencioso=False):
    if chave in j.revelados or chave not in DESBLOQUEIOS:
        return False
    j.revelados.append(chave)
    if not silencioso:
        avisar(j, DESBLOQUEIOS[chave]["texto"], grande=True)
        anotar_diario(j, DESBLOQUEIOS[chave]["texto"].split(" ", 1)[1])
    return True

def atualizar_desbloqueios(j, silencioso=False):
    return [k for k, d in DESBLOQUEIOS.items() if k not in j.revelados and _cond_ok(j, d) and revelar(j, k, silencioso)]

def avisar(j, texto, grande=False):
    """Fila de mensagens: o idle mostra no log, o menu mostra antes da tela."""
    j.avisos.append((texto, grande))
    del j.avisos[:-40]

def anotar_diario(j, texto):
    j.diario.append(f"Volta {j.ciclo} · Nv {j.nivel} · {texto}")
    del j.diario[:-150]

def evento(j, tipo, qt=1, **ctx):
    """Algo aconteceu: soma no contador e avança contratos, missões e passe que dependem disso.
    Tipos: monstro, chefe, ouro, item, bau, contrato, missao, dungeon, casa, habilidade, sino, volta."""
    j.stats[tipo] = j.stats.get(tipo, 0) + qt
    progresso_contratos(j, tipo, qt, ctx)
    progresso_missoes(j, tipo, qt, ctx)
    ganhar_passe(j, tipo, qt)

def dar_recompensa(j, r):
    """Aplica um dict de recompensa (ouro, xp, conchas, fragmentos, po, bau, item). Retorna o texto."""
    partes = []
    if r.get("ouro"):
        j.ouro += int(r["ouro"]); partes.append(f"+{fmt_num(r['ouro'])} ouro")
    if r.get("xp"):
        xp = r["xp"] * RITMO_XP
        j.ganhar_xp(xp, silencioso=True); partes.append(f"+{fmt_num(xp * j.mult_xp())} XP")
    if r.get("conchas"):
        j.conchas += int(r["conchas"]); partes.append(f"+{r['conchas']} conchas")
    if r.get("fragmentos"):
        j.fragmentos += int(r["fragmentos"]); partes.append(f"+{r['fragmentos']} ✦")
    if r.get("po"):
        j.po_forja += int(r["po"]); partes.append(f"+{r['po']} pó de forja")
    if r.get("bau"):
        guardar_bau(j, r["bau"]); partes.append(r["bau"])
    if r.get("pontos_hab"):
        j.pontos_hab_extra = getattr(j, "pontos_hab_extra", 0) + int(r["pontos_hab"]); partes.append(f"+{r['pontos_hab']} ponto(s) de habilidade")
    return ", ".join(partes)

def renda_minuto(j):
    """Ouro médio por minuto de idle no andar atual (base para recompensas que acompanham o jogo)."""
    return 360 * j.andar * j.escala() * j.mult_ouro()

# =====================================================================
# v3 · Fase 1 — Loot com ranks, baús, contratos, presente do Porto, bestiário
# =====================================================================
RANKS = [
    {"letra": "F", "nome": "Comum",    "cor": WT, "peso": 60,  "afixos": 0, "mult": 1.00, "po": 1},
    {"letra": "E", "nome": "Incomum",  "cor": GN, "peso": 25,  "afixos": 1, "mult": 1.25, "po": 2},
    {"letra": "D", "nome": "Raro",     "cor": CY, "peso": 10,  "afixos": 2, "mult": 1.55, "po": 4},
    {"letra": "C", "nome": "Épico",    "cor": MG, "peso": 4,   "afixos": 3, "mult": 1.90, "po": 8},
    {"letra": "B", "nome": "Lendário", "cor": YW, "peso": 0.4, "afixos": 3, "mult": 2.40, "po": 20},
    {"letra": "A", "nome": "Mítico",   "cor": RD, "peso": 0.04, "afixos": 4, "mult": 3.00, "po": 50},
]
LOOT_CHANCE = 0.06          # por monstro vencido (chefe: sempre)
PIEDADE_LOOT = 60           # itens seguidos sem Épico → o próximo é Épico

SLOTS = {   # status principal do espaço: plano, cresce com o nível do item (ilvl)
    "arma":     {"nome": "Arma",     "stat": "atq",  "base": 3,  "por_ilvl": 0.8},
    "elmo":     {"nome": "Elmo",     "stat": "def",  "base": 2,  "por_ilvl": 0.45},
    "peito":    {"nome": "Peitoral", "stat": "vida", "base": 12, "por_ilvl": 4},
    "botas":    {"nome": "Botas",    "stat": "def",  "base": 1,  "por_ilvl": 0.35},
    "anel":     {"nome": "Anel",     "stat": "atq",  "base": 1,  "por_ilvl": 0.45},
    "amuleto":  {"nome": "Amuleto",  "stat": "vida", "base": 8,  "por_ilvl": 2.5},
    "reliquia": {"nome": "Relíquia", "stat": "mana", "base": 6,  "por_ilvl": 2.5},
}
STAT_NOME = {"atq": "ATQ", "def": "DEF", "vida": "Vida", "mana": "Mana"}

AFIXOS = {   # percentuais; valor sorteado × (1 + 0,25 × rank)
    "atq%":   {"nome": "ATQ",     "min": 2, "max": 4},
    "def%":   {"nome": "DEF",     "min": 2, "max": 4},
    "vida%":  {"nome": "Vida",    "min": 2, "max": 5},
    "ouro%":  {"nome": "ouro",    "min": 3, "max": 7},
    "xp%":    {"nome": "XP",      "min": 2, "max": 5},
    "crit%":  {"nome": "crítico", "min": 1, "max": 3},
    "sorte%": {"nome": "sorte",   "min": 3, "max": 7},
}

NOMES_BASE = {
    "arma": {"Guerreiro": ["Espada", "Machado", "Lâmina"], "Mago": ["Cajado", "Varinha", "Tomo"],
             "Arqueiro": ["Arco", "Besta", "Arco Curto"]},
    "elmo": ["Elmo", "Capuz", "Tiara"], "peito": ["Peitoral", "Cota", "Manto"],
    "botas": ["Botas", "Grevas", "Sandálias"], "anel": ["Anel", "Aro", "Selo"],
    "amuleto": ["Amuleto", "Pingente", "Colar"], "reliquia": ["Relíquia", "Concha", "Lanterna"],
}
SUFIXOS_ANDAR = {
    1: ["do Cais", "das Redes", "da Maré", "do Farol"],
    2: ["do Rei", "do Quartel", "da Ponte", "do Trono"],
    3: ["de Brasa", "de Enxofre", "das Escamas", "do Ninho"],
    4: ["das Velas", "do Acólito", "da Balança", "do Claustro"],
    5: ["sem Fundo", "da Sombra", "do Eco", "da Escada"],
}
ORIGENS = {   # uma linha de "onde isso veio" para os itens Raros ou melhores
    1: ["Saiu das redes do cais, ainda pingando.",
        "Um caranguejo guardava isso como se fosse dele.",
        "Veio numa garrafa. Sem bilhete, de novo.",
        "O Pescador jura que nunca viu isso antes. Ele está mentindo."],
    2: ["Estava no pé do trono, onde ninguém olha.",
        "Um soldado fantasma entregou sem dizer nada.",
        "Tem o brasão do Rei raspado com uma faca.",
        "Achado num banquete que nunca começou."],
    3: ["Morno ao toque, como se o dragão ainda respirasse nele.",
        "Tirado de entre ossos virados para a saída.",
        "Derreteu e endureceu de novo. Duas vezes, pelo menos.",
        "Um kobold mineiro trocou por um pedaço de pão."],
    4: ["Uma vela se apagou quando você pegou isso.",
        "Tem o seu nome gravado. Em letra de outra pessoa.",
        "A balança do altar pesou isso e mandou você levar.",
        "Um acólito cego apontou exatamente para onde estava."],
    5: ["Subiu do escuro sozinho, como uma bolha.",
        "Seu reflexo segurava isso meio passo antes de você.",
        "Frio de um jeito que não vem de fora.",
        "Ninguém deixou isso aqui. Isso estava esperando."],
}
LENDARIOS = [   # rank B: nome e efeito únicos (efeito: chave lida em calcular_bonus / luta_auto)
    {"nome": "Coroa Partida do Rei",      "slot": "elmo",     "efeito": "chefe_vida", "valor": 10, "desc": "chefes começam com -10% de vida",
     "origem": "A metade que falta deve estar no Abismo."},
    {"nome": "Rede do Pescador",          "slot": "reliquia", "efeito": "loot",       "valor": 50, "desc": "+50% de chance de equipamento",
     "origem": "Remendada tantas vezes que já não sobra fio original."},
    {"nome": "Escama Viva",               "slot": "peito",    "efeito": "regen",      "valor": 3,  "desc": "recupera 3% da vida por turno",
     "origem": "Ela ainda cresce. Devagar, mas cresce."},
    {"nome": "Vela que Não Apaga",        "slot": "amuleto",  "efeito": "xp%",        "valor": 20, "desc": "+20% XP",
     "origem": "Já tentaram apagar com água do mar. Ela riu."},
    {"nome": "Olho Sem Fundo",            "slot": "anel",     "efeito": "crit_dano",  "valor": 50, "desc": "críticos causam +50% de dano",
     "origem": "Ele pisca quando você não está olhando."},
    {"nome": "Lâmina do Afogado",         "slot": "arma",     "efeito": "dano",       "valor": 15, "desc": "+15% de dano",
     "origem": "Encontrada presa nas redes. O cabo ainda está molhado."},
    {"nome": "Botas do Primeiro Andante", "slot": "botas",    "efeito": "acao_extra", "valor": 6,  "desc": "+6% de ação extra no idle",
     "origem": "Gastas exatamente no formato dos seus pés."},
    {"nome": "Manto da Padeira",          "slot": "peito",    "efeito": "ouro%",      "valor": 25, "desc": "+25% ouro",
     "origem": "Cheira a pão quente. Em qualquer andar."},
    {"nome": "Selo do Guardião",          "slot": "anel",     "efeito": "def%",       "valor": 15, "desc": "+15% DEF",
     "origem": "A ordem do Rei, finalmente. Tarde demais para ele."},
    {"nome": "Lanterna do Farol Apagado", "slot": "reliquia", "efeito": "sorte%",     "valor": 30, "desc": "+30% sorte",
     "origem": "Não ilumina nada. Mas as coisas boas a encontram."},
]
MITICOS = [   # rank A: só de chefes, baú Abissal e Pesadelo
    {"nome": "Coração do Mar Escuro",     "slot": "amuleto",  "efeito": "tudo",       "valor": 15, "desc": "+15% ATQ, DEF e Vida",
     "origem": "Bate. Fora do ritmo do seu, mas bate."},
    {"nome": "Coroa do Rei das Sombras",  "slot": "elmo",     "efeito": "chefe_vida", "valor": 25, "desc": "chefes começam com -25% de vida",
     "origem": "A outra metade. Ela encaixa na Coroa Partida."},
    {"nome": "Âncora da Primeira Volta",  "slot": "arma",     "efeito": "dano",       "valor": 35, "desc": "+35% de dano",
     "origem": "Pesada como tudo que você já recomeçou."},
]
EFEITO_NOME = {"chefe_vida": "chefes -{v}% vida", "loot": "+{v}% equipamento", "regen": "regenera {v}%/turno",
               "crit_dano": "+{v}% dano crítico", "dano": "+{v}% dano", "acao_extra": "+{v}% ação extra",
               "tudo": "+{v}% ATQ/DEF/Vida", "xp%": "+{v}% XP", "ouro%": "+{v}% ouro", "def%": "+{v}% DEF",
               "sorte%": "+{v}% sorte", "atq%": "+{v}% ATQ", "vida%": "+{v}% Vida", "crit%": "+{v}% crítico"}

CONJUNTOS = {   # 2 e 4 peças do mesmo conjunto (andar ou dungeon de origem)
    "afogado": {"nome": "Vestes do Afogado", "sufixo": "do Afogado", "andar": 1, 2: {"ouro%": 10}, 4: {"vida%": 15}},
    "real":    {"nome": "Guarda Real",       "sufixo": "da Guarda",  "andar": 2, 2: {"def%": 10}, 4: {"atq%": 10}},
    "brasa":   {"nome": "Couraça de Brasa",  "sufixo": "Ardente",    "andar": 3, 2: {"atq%": 10}, 4: {"crit%": 5}},
    "templo":  {"nome": "Vestes do Templo",  "sufixo": "Votivo",     "andar": 4, 2: {"xp%": 15},  4: {"regen": 2}},
    "abismo":  {"nome": "Pele do Abismo",    "sufixo": "Abissal",    "andar": 5, 2: {"sorte%": 15}, 4: {"tudo": 8}},
}
CONJUNTO_ANDAR = {c["andar"]: k for k, c in CONJUNTOS.items()}

BAUS = {   # ouro = minutos de renda; minimo = rank mínimo dos itens
    "Baú de Bronze": {"curto": "Bronze",  "itens": 1, "minimo": 0, "ouro": 3,  "conchas": 0},
    "Baú de Prata":  {"curto": "Prata",   "itens": 2, "minimo": 1, "ouro": 6,  "conchas": 2},
    "Baú de Ouro":   {"curto": "Ouro",    "itens": 3, "minimo": 2, "ouro": 12, "conchas": 5},
    "Baú Abissal":   {"curto": "Abissal", "itens": 3, "minimo": 3, "ouro": 25, "conchas": 15, "mitico": True},
}
BAU_LIMITE = 15             # acima disso o baú abre sozinho
BAU_CURTO = {b["curto"]: n for n, b in BAUS.items()}

def chance_critico(j):
    """(chance 0-0,6, multiplicador) — crítico vem de afixos, conjuntos, habilidades e grupo."""
    b = j.bonus
    return min(0.6, b.get("crit%", 0) / 100), 2.0 + b.get("crit_dano", 0) / 100

def _somar(b, chave, valor):
    b[chave] = b.get(chave, 0) + valor

def calcular_bonus(j):
    """Soma tudo que vem de fora dos atributos: equipamento, conjuntos, habilidades, grupo e maestria.
    Planos (atq/def/vida/mana) entram antes dos multiplicadores; % e efeitos são lidos onde importam."""
    b = {}
    conj = {}
    for it in getattr(j, "equip", {}).values():
        memoria = 1 + min(10, it.get("abates", 0) // 100) / 100 if it["rank"] >= 4 else 1
        _somar(b, SLOTS[it["slot"]]["stat"], it["main"] * memoria)
        for k, v in it["afixos"].items():
            _somar(b, k, v)
        if it.get("efeito"):
            _somar(b, it["efeito"][0], it["efeito"][1])
        if it.get("conjunto"):
            conj[it["conjunto"]] = conj.get(it["conjunto"], 0) + 1
    for c, n in conj.items():
        for pecas in (2, 4):
            if n >= pecas and c in CONJUNTOS:
                for k, v in CONJUNTOS[c][pecas].items():
                    _somar(b, k, v)
    _bonus_habilidades(j, b)
    _bonus_grupo(j, b)
    _bonus_maestria(j, b)
    return b

def nomes_base(j, slot):
    n = NOMES_BASE[slot]
    return n.get(j.classe, n["Guerreiro"]) if isinstance(n, dict) else n

def rolar_rank(j, bonus=0, mitico=False, minimo=0):
    """Sorteia o rank (0=F … 5=A). Sorte aumenta as chances do Raro para cima; piedade garante Épico."""
    sorte = min(100, j.bonus.get("sorte%", 0)) / 100       # sorte tem teto: +100%
    pesos = [r["peso"] * (1 + sorte * (i - 1) / 2) if i >= 2 else r["peso"] for i, r in enumerate(RANKS)]
    if not mitico:
        pesos[5] = 0
    idx = max(minimo, random.choices(range(len(RANKS)), weights=pesos, k=1)[0]) + bonus
    j.piedade_loot += 1
    if idx < 3 and j.piedade_loot >= PIEDADE_LOOT:
        idx = 3
    idx = min(5 if mitico else 4, idx)
    if idx >= 3:
        j.piedade_loot = 0
    return idx

def gerar_item(j, rank, slot=None, ilvl=None, andar=None, conjunto=None):
    andar = andar or j.andar
    ilvl = ilvl or j.nivel
    efeito, origem = None, ""
    if rank >= 4:
        unico = random.choice(MITICOS if rank == 5 else LENDARIOS)
        slot, nome, efeito, origem = unico["slot"], unico["nome"], (unico["efeito"], unico["valor"]), unico["origem"]
    else:
        slot = slot or random.choice(list(SLOTS))
        if conjunto is None and rank >= 2 and random.random() < 0.25:
            conjunto = CONJUNTO_ANDAR.get(andar)
        if rank < 2:
            conjunto = None
        sufixo = CONJUNTOS[conjunto]["sufixo"] if conjunto else random.choice(SUFIXOS_ANDAR.get(andar, SUFIXOS_ANDAR[1]))
        nome = f"{random.choice(nomes_base(j, slot))} {sufixo}"
        if rank >= 2:
            origem = random.choice(ORIGENS.get(andar, ORIGENS[1]))
    s = SLOTS[slot]
    main = max(1, int((s["base"] + s["por_ilvl"] * ilvl) * RANKS[rank]["mult"]))
    afixos = {}
    for k in random.sample(list(AFIXOS), RANKS[rank]["afixos"]):
        a = AFIXOS[k]
        afixos[k] = max(1, int(random.randint(a["min"], a["max"]) * (1 + 0.25 * rank)))
    return {"slot": slot, "nome": nome, "rank": rank, "ilvl": ilvl, "main": main, "afixos": afixos,
            "efeito": efeito, "conjunto": conjunto if rank < 4 else None, "abates": 0, "origem": origem}

def fmt_item(it):
    r = RANKS[it["rank"]]
    marca = " ⟡" if it.get("conjunto") else ""
    return f"{r['cor']}{BOLD}{it['nome']}{RESET}{r['cor']} [{r['letra']} {r['nome']}]{marca}{RESET}"

def fmt_detalhes(it):
    s = SLOTS[it["slot"]]
    partes = [f"+{it['main']} {STAT_NOME[s['stat']]}"]
    partes += [f"+{v}% {AFIXOS[k]['nome']}" for k, v in it["afixos"].items()]
    if it.get("efeito"):
        partes.append(EFEITO_NOME.get(it["efeito"][0], "{v}").format(v=it["efeito"][1]))
    if it["rank"] >= 4:
        partes.append(f"memória {min(10, it.get('abates', 0) // 100)}% ({it.get('abates', 0)} abates)")
    return " · ".join(partes) + f" · ilvl {it['ilvl']}"

def valor_item(j, it):
    """Quanto o item vale para este personagem, em 'ATQ equivalente' (usado para equipar sozinho)."""
    peso = {"atq": 1.0, "def": 1.2, "vida": 0.2, "mana": 0.03}
    v = peso[SLOTS[it["slot"]]["stat"]] * it["main"]
    escala_pct = {"atq%": j.atq, "def%": j.def_ * 1.2, "vida%": j.vida_max * 0.2, "crit%": j.atq,
                  "ouro%": j.atq * 0.5, "xp%": j.atq * 0.6, "sorte%": j.atq * 0.4}
    for k, x in it["afixos"].items():
        v += x * escala_pct.get(k, j.atq * 0.3) / 100
    if it.get("efeito"):
        v += j.atq * (0.35 if it["rank"] == 5 else 0.2)
    if it.get("conjunto"):
        v += j.atq * 0.04 * sum(1 for o in j.equip.values() if o is not it and o.get("conjunto") == it["conjunto"])
    return v

def desmanchar(j, it):
    """Item que sobrou vira pó de forja e um pouco de ouro. Retorna (pó, ouro)."""
    po = RANKS[it["rank"]]["po"]
    j.po_forja += po
    ouro = j.ganhar_ouro(it["ilvl"] * 4 * (it["rank"] + 1))
    return po, ouro

def receber_item(j, it, silencioso=False):
    """Equipa se for melhor (o idle faz isso sozinho); senão desmancha. Retorna a linha do log."""
    evento(j, "item", rank=it["rank"])
    j.stats["maior_rank"] = max(j.stats.get("maior_rank", 0), it["rank"])
    if it["rank"] >= 2:
        revelar(j, "equipamento")
    atual = j.equip.get(it["slot"])
    if atual is None or valor_item(j, it) > valor_item(j, atual):
        if atual:
            desmanchar(j, atual)
        j.equip[it["slot"]] = it
        j._recalcular()
        txt = f"💠 Equipou {fmt_item(it)}"
    else:
        po, _ = desmanchar(j, it)
        txt = f"♻️  {fmt_item(it)} virou {po} pó de forja"
    if it["rank"] >= 3 and not silencioso:
        avisar(j, f"✨ {RANKS[it['rank']]['nome'].upper()}! {it['nome']}", grande=True)
    if it["rank"] >= 4:
        anotar_diario(j, f"Encontrou {it['nome']} [{RANKS[it['rank']]['nome']}]. {it.get('origem', '')}".strip())
    return txt

def loot_vitoria(j, chefe=False, andar=None, bonus=0, mitico=False, conjunto=None, mult_chance=1.0):
    """Talvez cai um equipamento depois de uma vitória. Retorna a linha do log ou None."""
    chance = 1.0 if chefe else LOOT_CHANCE * mult_chance * (1 + j.bonus.get("loot", 0) / 100)
    if random.random() >= chance:
        return None
    rank = rolar_rank(j, bonus=bonus, minimo=1 if chefe else 0, mitico=mitico or chefe)
    return receber_item(j, gerar_item(j, rank, andar=andar, conjunto=conjunto))

def marcar_abates(j, qt=1):
    """Itens Lendários/Míticos lembram quantos inimigos derrubaram (+1% a cada 100, até +10%)."""
    mudou = False
    for it in j.equip.values():
        if it["rank"] >= 4:
            antes = it.get("abates", 0) // 100
            it["abates"] = it.get("abates", 0) + qt
            mudou = mudou or it["abates"] // 100 != antes
    if mudou:
        j._recalcular()

def custo_rerrolar(it):
    return 6 * (it["rank"] + 1)

def custo_atualizar(it):
    return 4 * (it["rank"] + 1)

def rerrolar_afixos(j, slot):
    it = j.equip.get(slot)
    if not it or j.po_forja < custo_rerrolar(it) or not it["afixos"]:
        return False
    j.po_forja -= custo_rerrolar(it)
    novo = gerar_item(j, it["rank"], slot=slot, ilvl=it["ilvl"])
    it["afixos"] = novo["afixos"] if it["rank"] < 4 else {k: max(1, int(random.randint(AFIXOS[k]["min"], AFIXOS[k]["max"]) * (1 + 0.25 * it["rank"])))
                                                         for k in random.sample(list(AFIXOS), RANKS[it["rank"]]["afixos"])}
    j._recalcular()
    return True

def atualizar_item(j, slot):
    """Traz o item para o seu nível atual (útil para não largar um Lendário)."""
    it = j.equip.get(slot)
    if not it or it["ilvl"] >= j.nivel or j.po_forja < custo_atualizar(it):
        return False
    j.po_forja -= custo_atualizar(it)
    s = SLOTS[slot]
    it["ilvl"] = j.nivel
    it["main"] = max(1, int((s["base"] + s["por_ilvl"] * j.nivel) * RANKS[it["rank"]]["mult"]))
    j._recalcular()
    return True

def guardar_bau(j, nome):
    nome = BAU_CURTO.get(nome, nome)
    if nome not in BAUS:
        return
    revelar(j, "baus")
    j.inven[nome] = j.inven.get(nome, 0) + 1
    if j.inven[nome] > BAU_LIMITE:   # cheio: abre o excedente sozinho
        abrir_bau(j, nome)

def abrir_bau(j, nome):
    """Abre um baú. Retorna (itens recebidos, linhas)."""
    if j.inven.get(nome, 0) <= 0:
        return [], []
    j.inven[nome] -= 1
    if not j.inven[nome]:
        del j.inven[nome]
    b = BAUS[nome]
    evento(j, "bau")
    itens, linhas = [], []
    for _ in range(b["itens"]):
        it = gerar_item(j, rolar_rank(j, minimo=b["minimo"], mitico=b.get("mitico", False)))
        itens.append(it)
        linhas.append(receber_item(j, it))
    linhas.append(dar_recompensa(j, {"ouro": renda_minuto(j) * b["ouro"], "conchas": b["conchas"]}))
    return itens, linhas

# ---------- Contratos do Porto (metas de médio prazo) ----------
CONTRATOS_ATIVOS = 3
CONTRATOS_RENOVAM_H = 4

def gerar_contrato(j):
    tipos = ["monstro", "ouro", "chefe", "item"]
    # TODO Fase 4: voltar a gerar "dungeon" e "casa" quando dungeons e mapa existirem
    if desbloqueado(j, "habilidades"): tipos.append("habilidade")
    ativos = {c["tipo"] for c in j.contratos if not c["feito"]}
    tipo = random.choice([t for t in tipos if t not in ativos] or tipos)
    renda = renda_minuto(j)
    filtro = {}
    if tipo == "monstro":
        qt = random.randint(5, 12) * 5; filtro = {"andar": j.andar}
        texto = f"Derrote {qt} monstros no Andar {j.andar} ou acima"
    elif tipo == "ouro":
        qt = int(renda * random.randint(8, 15)); texto = f"Ganhe {fmt_num(qt)} de ouro"
    elif tipo == "chefe":
        qt = random.randint(1, 3); texto = f"Vença {qt} chefe(s)"
    elif tipo == "item":
        qt = random.randint(2, 4); filtro = {"rank": 2}; texto = f"Encontre {qt} equipamentos Raros ou melhores"
    elif tipo == "dungeon":
        qt = random.randint(1, 2); texto = f"Complete {qt} dungeon(s)"
    elif tipo == "casa":
        qt = random.randint(4, 10); texto = f"Revele {qt} casas do mapa"
    else:
        qt = random.randint(4, 8) * 10; texto = f"Use habilidades {qt} vezes"
    rec = {"ouro": int(renda * random.randint(3, 6)), "conchas": random.choice([3, 5, 5, 8])}
    sorte = random.random()
    if sorte < 0.15: rec["fragmentos"] = 1
    elif sorte < 0.45: rec["bau"] = "Baú de Bronze"
    elif sorte < 0.6: rec["bau"] = "Baú de Prata"
    return {"texto": texto, "tipo": tipo, "qt": qt, "prog": 0, "filtro": filtro, "recompensa": rec, "feito": False}

def renovar_contratos(j, agora=None):
    if not desbloqueado(j, "contratos"):
        return
    agora = agora or time.time()
    if len(j.contratos) < CONTRATOS_ATIVOS or agora >= j.contratos_renovam:
        if j.contratos and agora >= j.contratos_renovam and any(c["feito"] for c in j.contratos):
            avisar(j, "📋 O quadro do cais tem contratos novos.")
        if agora >= j.contratos_renovam:
            j.contratos = [c for c in j.contratos if not c["feito"]]
            j.contratos_renovam = agora + CONTRATOS_RENOVAM_H * 3600
        while len(j.contratos) < CONTRATOS_ATIVOS:
            j.contratos.append(gerar_contrato(j))

def _filtro_ok(filtro, ctx):
    for k, v in filtro.items():
        if k == "andar" and ctx.get("andar", 0) < v: return False
        if k == "rank" and ctx.get("rank", -1) < v: return False
    return True

def progresso_contratos(j, tipo, qt, ctx):
    for c in getattr(j, "contratos", []):
        if c["feito"] or c["tipo"] != tipo or not _filtro_ok(c["filtro"], ctx):
            continue
        c["prog"] = min(c["qt"], c["prog"] + qt)
        if c["prog"] >= c["qt"]:
            c["feito"] = True
            texto = dar_recompensa(j, c["recompensa"])
            avisar(j, f"📋 Contrato cumprido: {c['texto']} ({texto})", grande=True)
            anotar_diario(j, f"Contrato cumprido: {c['texto']}.")
            evento(j, "contrato")

# ---------- Presente do Porto (retorno diário, sem punição) ----------
PRESENTE_HORAS = 20

def presente_do_porto(j, agora=None):
    """Dá o presente se passou um dia desde o último. A sequência só pausa (nunca zera). Retorna linhas ou []."""
    agora = agora or time.time()
    if j.presente_ultimo and agora - j.presente_ultimo < PRESENTE_HORAS * 3600:
        return []
    j.presente_seq = j.presente_seq % 7 + 1
    j.presente_ultimo = agora
    d = j.presente_seq
    r = {"ouro": int(renda_minuto(j) * 5 * d), "conchas": 5 * d}
    if d == 7: r["bau"] = "Baú de Ouro"
    elif d in (3, 5): r["bau"] = "Baú de Prata"
    texto = dar_recompensa(j, r)
    bilhete = ("A padeira deixou um embrulho na porta. Sem bilhete, desta vez." if j.marcas.get("padeira_traida")
               else "A padeira deixou um embrulho na porta, com um bilhete: 'volte'.")
    return [f"🎁 Presente do Porto · dia {d}/7: {texto}",
            f"   {DIM}{bilhete} (A sequência nunca zera, só pausa.){RESET}"]

# ---------- Bestiário ----------
BESTIARIO = {
    "Goblin da Floresta": "Rouba o que brilha. Joga fora quando para de brilhar.",
    "Lobo Magro": "Segue os andantes de longe. Come o que eles largam.",
    "Caranguejo Gigante": "Guarda tesouros que não sabe usar. Ofende-se fácil.",
    "Soldado Fantasma": "Ainda espera ordens do Rei. Vai esperar para sempre.",
    "Rato do Castelo": "Marcham em fila. Alguém os ensinou, há muito tempo.",
    "Armadura Vazia": "Vazia não é bem a palavra. Algo ocupa o lugar do dono.",
    "Morcego de Brasa": "Nasce das faíscas do ninho e morre quando esfria.",
    "Kobold Mineiro": "Cava em direção ao calor. Troca qualquer coisa por pão.",
    "Filhote de Dragão": "Mais curioso que perigoso. Até crescer.",
    "Sacerdote Oco": "Reza com a boca, mas não tem nada dentro.",
    "Estátua Viva": "Tem um rosto conhecido. O seu, mais velho.",
    "Acólito Cego": "Vê o que vai acontecer. Não o que está na frente.",
    "Sombra Errante": "Era alguém. Agora procura quem.",
    "Eco do Abismo": "Repete sua última palavra. Às vezes, a próxima.",
    "Olho Sem Fundo": "Não pisca. Nunca piscou. Você pisca por ele.",
}
BESTIARIO_POR_BONUS = 50    # a cada 50 abates de um monstro: +1% de dano contra ele (até +5%)

def registrar_abate(j, nome, andar=None):
    """Monstro vencido: bestiário, contadores (contratos/missões/passe) e memória dos Lendários."""
    novo = nome not in j.bestiario
    j.bestiario[nome] = j.bestiario.get(nome, 0) + 1
    if j.bestiario[nome] % BESTIARIO_POR_BONUS == 0 and j.bestiario[nome] <= BESTIARIO_POR_BONUS * 5 and desbloqueado(j, "recordes"):
        avisar(j, f"📖 Bestiário: {nome} ×{j.bestiario[nome]} (+{bonus_bestiario(j, nome)}% de dano contra ele)")
    evento(j, "monstro", andar=andar or j.andar, nome=nome, grupo=tuple(j.grupo))
    marcar_abates(j)
    registrar_batalha_grupo(j)
    return novo

def manutencao_idle(j, anota):
    """Coisas que o idle faz sozinho a cada passo (as fases seguintes acrescentam aqui)."""
    for gancho in GANCHOS_IDLE:
        gancho(j, anota)


def bonus_bestiario(j, nome):
    return min(5, j.bestiario.get(nome, 0) // BESTIARIO_POR_BONUS) if nome else 0

# Gancho da fase seguinte (substituído mais abaixo quando o sistema existe)
def ganhar_passe(j, tipo, qt): pass

# =====================================================================
# v3 · Fase 2 — Árvores de habilidade, ativas, elementos, subclasses, faixas de nível
# =====================================================================
# Efeitos (somados em calcular_bonus): atq% def% vida% ouro% xp% crit% sorte% crit_dano loot regen dano
# acao_extra chefe_vida tudo · regras de luta: contra_ataque furia comando fogo_cadeia lentidao
# escudo_mana tiro_duplo esquiva cd ativa%
EFEITO_NOME.update({"contra_ataque": "reflete {v}% do dano", "furia": "+{v}% dano com vida < 50%",
                    "comando": "+{v}% dano do grupo", "fogo_cadeia": "+{v}% Bola de Fogo",
                    "lentidao": "inimigo -{v}% ATQ", "escudo_mana": "mana absorve {v}% do dano",
                    "tiro_duplo": "{v}% de golpe duplo", "esquiva": "{v}% de esquiva",
                    "cd": "-{v} turno de recarga", "ativa%": "+{v}% dano das ativas"})

def _no(id_, nome, efeito, valor, maximo=1, chave=False):
    return {"id": id_, "nome": nome, "efeito": efeito, "valor": valor, "max": maximo, "chave": chave}

ARVORES = {
    "Guerreiro": [
        {"nome": "Muralha", "desc": "DEF, vida e contra-ataque", "nos": [
            _no("pele_grossa", "Pele Grossa", "def%", 3, 5), _no("postura", "Postura", "vida%", 3, 5),
            _no("contra_ataque", "Contra-ataque", "contra_ataque", 20, chave=True), _no("escudo_firme", "Escudo Firme", "def%", 4, 3),
            _no("resistir", "Resistir", "regen", 1, 2), _no("inabalavel", "Inabalável", "lentidao", 15, chave=True),
            _no("muralha_viva", "Muralha Viva", "vida%", 5, 3), _no("fortaleza", "Fortaleza", "tudo", 6, chave=True)]},
        {"nome": "Fúria", "desc": "dano que cresce com a vida baixa", "nos": [
            _no("golpes_brutos", "Golpes Brutos", "atq%", 3, 5), _no("sede", "Sede de Luta", "crit%", 2, 3),
            _no("furia", "Fúria", "furia", 30, chave=True), _no("lamina_pesada", "Lâmina Pesada", "crit_dano", 10, 3),
            _no("impeto", "Ímpeto", "dano", 3, 3), _no("massacre", "Massacre", "tiro_duplo", 15, chave=True),
            _no("sangue_quente", "Sangue Quente", "atq%", 4, 3), _no("berserk", "Berserk", "dano", 15, chave=True)]},
        {"nome": "Comando", "desc": "fortalece o grupo e a coleta", "nos": [
            _no("voz_firme", "Voz Firme", "comando", 5, 5), _no("estandarte", "Estandarte", "ouro%", 4, 3),
            _no("formacao", "Formação", "comando", 25, chave=True), _no("instrutor", "Instrutor", "xp%", 4, 3),
            _no("logistica", "Logística", "loot", 10, 3), _no("ordem_rapida", "Ordem Rápida", "cd", 1, chave=True),
            _no("veterano", "Veterano", "def%", 3, 3), _no("lenda_cais", "Lenda do Cais", "comando", 30, chave=True)]},
    ],
    "Mago": [
        {"nome": "Chama", "desc": "Bola de Fogo em cadeia e crítico", "nos": [
            _no("faisca", "Faísca", "fogo_cadeia", 6, 5), _no("calor", "Calor", "crit%", 2, 3),
            _no("bola_cadeia", "Bola em Cadeia", "fogo_cadeia", 50, chave=True), _no("combustao", "Combustão", "crit_dano", 10, 3),
            _no("fornalha", "Fornalha", "dano", 3, 3), _no("queimadura", "Queimadura", "dano", 12, chave=True),
            _no("pira", "Pira", "ativa%", 8, 3), _no("sol_pequeno", "Sol Pequeno", "fogo_cadeia", 60, chave=True)]},
        {"nome": "Maré", "desc": "gelo e água: o inimigo fica lento", "nos": [
            _no("correnteza", "Correnteza", "lentidao", 3, 5), _no("mare_alta", "Maré Alta", "vida%", 3, 3),
            _no("gelo", "Gelo", "lentidao", 15, chave=True), _no("ressaca", "Ressaca", "regen", 1, 2),
            _no("profundeza", "Profundeza", "def%", 4, 3), _no("afogar", "Afogar", "chefe_vida", 8, chave=True),
            _no("calmaria", "Calmaria", "xp%", 4, 3), _no("tsunami", "Tsunami", "ativa%", 30, chave=True)]},
        {"nome": "Arcano", "desc": "mana, escudos e recarga", "nos": [
            _no("erudicao", "Erudição", "xp%", 3, 5), _no("mana_densa", "Mana Densa", "escudo_mana", 5, 3),
            _no("escudo_mana", "Escudo de Mana", "escudo_mana", 25, chave=True), _no("foco", "Foco", "crit%", 2, 3),
            _no("sabedoria_antiga", "Sabedoria Antiga", "ouro%", 4, 3), _no("tempo_curto", "Tempo Curto", "cd", 1, chave=True),
            _no("runas", "Runas", "tudo", 2, 3), _no("arquimago", "Arquimago", "ativa%", 40, chave=True)]},
    ],
    "Arqueiro": [
        {"nome": "Precisão", "desc": "crítico e dano crítico", "nos": [
            _no("olho_treinado", "Olho Treinado", "crit%", 2, 5), _no("ponta_fina", "Ponta Fina", "crit_dano", 8, 3),
            _no("tiro_certeiro", "Tiro Certeiro", "crit%", 10, chave=True), _no("paciencia", "Paciência", "dano", 3, 3),
            _no("mira", "Mira", "atq%", 3, 3), _no("ponto_fraco", "Ponto Fraco", "crit_dano", 50, chave=True),
            _no("calma", "Calma", "crit%", 2, 3), _no("olho_falcao", "Olho de Falcão", "dano", 15, chave=True)]},
        {"nome": "Rastro", "desc": "ouro, loot e sorte", "nos": [
            _no("faro", "Faro", "ouro%", 4, 5), _no("batedor", "Batedor", "loot", 8, 3),
            _no("saqueador", "Saqueador", "sorte%", 25, chave=True), _no("armadilhas", "Armadilhas", "lentidao", 4, 3),
            _no("mochila_funda", "Mochila Funda", "xp%", 4, 3), _no("cacador_tesouro", "Caçador de Tesouro", "loot", 40, chave=True),
            _no("atalhos", "Atalhos", "acao_extra", 2, 3), _no("mestre_rastro", "Mestre do Rastro", "sorte%", 30, chave=True)]},
        {"nome": "Vento", "desc": "golpes duplos e esquiva", "nos": [
            _no("leveza", "Leveza", "esquiva", 2, 5), _no("rajada", "Rajada", "acao_extra", 1, 3),
            _no("tiro_duplo", "Tiro Duplo", "tiro_duplo", 20, chave=True), _no("correr", "Correr", "def%", 3, 3),
            _no("brisa", "Brisa", "regen", 1, 2), _no("vendaval", "Vendaval", "tiro_duplo", 15, chave=True),
            _no("pes_leves", "Pés Leves", "esquiva", 2, 3), _no("tempestade", "Tempestade", "dano", 15, chave=True)]},
    ],
}
RAMO_DESBLOQUEIO = ["habilidades", "ramo2", "ramo3"]
NOS = {n["id"]: n for arv in ARVORES.values() for ramo in arv for n in ramo["nos"]}

# Habilidades ativas: usadas sozinhas pela rotação no idle; sobem de rank com o uso (I-V)
ATIVAS = {
    "golpe_pesado": {"nome": "Golpe Pesado",     "classe": "Guerreiro", "cd": 3, "mana": 0,  "tipo": "dano", "valor": 1.8},
    "grito":        {"nome": "Grito de Guerra",  "classe": "Guerreiro", "cd": 6, "mana": 0,  "tipo": "buff_dano", "valor": 0.25, "duracao": 3},
    "muralha":      {"nome": "Muralha de Escudo", "classe": "Guerreiro", "cd": 5, "mana": 0, "tipo": "reduz", "valor": 0.5, "duracao": 2},
    "lanca_gelo":   {"nome": "Lança de Gelo",    "classe": "Mago", "cd": 3, "mana": 10, "tipo": "dano", "valor": 1.5, "elem": "Água", "magia": True},
    "meteoro":      {"nome": "Meteoro",          "classe": "Mago", "cd": 6, "mana": 20, "tipo": "dano", "valor": 2.8, "elem": "Fogo", "magia": True},
    "barreira":     {"nome": "Barreira Arcana",  "classe": "Mago", "cd": 5, "mana": 12, "tipo": "reduz", "valor": 0.5, "duracao": 2},
    "flecha_dupla": {"nome": "Flecha Dupla",     "classe": "Arqueiro", "cd": 3, "mana": 0, "tipo": "dano", "valor": 2.0},
    "flecha_pedra": {"nome": "Flecha de Pedra",  "classe": "Arqueiro", "cd": 4, "mana": 0, "tipo": "dano", "valor": 1.7, "elem": "Terra"},
    "olho_aguia":   {"nome": "Olho de Águia",    "classe": "Arqueiro", "cd": 6, "mana": 0, "tipo": "buff_crit", "valor": 0.3, "duracao": 3},
    # ativas de subclasse
    "luz_cais":     {"nome": "Luz do Cais",      "cd": 5, "mana": 0,  "tipo": "dano", "valor": 2.4, "elem": "Luz"},
    "furia_cega":   {"nome": "Fúria Cega",       "cd": 6, "mana": 0,  "tipo": "dano", "valor": 3.2},
    "maremoto":     {"nome": "Maremoto",         "cd": 5, "mana": 18, "tipo": "dano", "valor": 2.6, "elem": "Água", "magia": True},
    "vela_negra":   {"nome": "Vela Negra",       "cd": 5, "mana": 18, "tipo": "dano", "valor": 2.6, "elem": "Sombra", "magia": True},
    "tiro_sujo":    {"nome": "Tiro Sujo",        "cd": 4, "mana": 0,  "tipo": "dano", "valor": 2.2, "elem": "Terra"},
    "feixe_farol":  {"nome": "Feixe do Farol",   "cd": 6, "mana": 0,  "tipo": "dano", "valor": 3.0, "elem": "Luz"},
}
USOS_RANK = [0, 100, 400, 1200, 3000]     # usos para chegar ao rank I, II, III, IV, V
ROMANO = ["I", "II", "III", "IV", "V"]

SUBCLASSES = {
    "Guerreiro": [
        {"nome": "Paladino do Cais", "desc": "DEF e cura; ataca com luz", "bonus": {"def%": 12, "regen": 1}, "ativa": "luz_cais"},
        {"nome": "Berserker", "desc": "ATQ e fúria; golpes enormes", "bonus": {"atq%": 12, "furia": 20}, "ativa": "furia_cega"}],
    "Mago": [
        {"nome": "Maremante", "desc": "água e lentidão; aguenta mais", "bonus": {"vida%": 12, "lentidao": 10}, "ativa": "maremoto"},
        {"nome": "Necromante das Velas", "desc": "sombra; dano bruto", "bonus": {"dano": 12, "crit%": 3}, "ativa": "vela_negra"}],
    "Arqueiro": [
        {"nome": "Batedor", "desc": "loot e sorte; acha de tudo", "bonus": {"loot": 30, "sorte%": 20}, "ativa": "tiro_sujo"},
        {"nome": "Atirador do Farol", "desc": "crítico e luz; um tiro, um fim", "bonus": {"crit%": 8, "crit_dano": 30}, "ativa": "feixe_farol"}],
}
SUBCLASSE_AUTO_NIVEL = 35   # quem nunca escolheu ganha a primeira opção (o idle não pode travar)

# ---------- Faixas de nível ----------
NIVEL_MORTAL = 60           # acima disso só depois do Despertar (missão "O Segundo Fôlego")
NIVEL_MAX = 120             # depois disso o XP vai para a Maestria
MAESTRIA_POR_PONTO = 0.5    # % no status escolhido

def nivel_teto(j):
    return NIVEL_MAX if j.marcas.get("despertado") else NIVEL_MORTAL

def nivel_efetivo(j):
    """Nível usado para os requisitos da torre: nível + pontos de Maestria."""
    return j.nivel + sum(getattr(j, "maestria", {}).values())

def xp_maestria(j):
    return int(xp_para_nivel(NIVEL_MAX) * 1.5 * (1 + 0.02 * sum(j.maestria.values())))

def pontos_hab_total(j):
    return (max(0, min(j.nivel, NIVEL_MORTAL) - 7) + max(0, min(j.nivel, NIVEL_MAX) - NIVEL_MORTAL) // 2
            + getattr(j, "pontos_hab_extra", 0))

def pontos_hab_livres(j):
    return max(0, pontos_hab_total(j) - sum(j.habilidades.values())) if desbloqueado(j, "habilidades") else 0

def ramos_liberados(j):
    return [i for i, chave in enumerate(RAMO_DESBLOQUEIO) if desbloqueado(j, chave)]

def pode_aprender(j, no_id):
    arv = ARVORES.get(j.classe, ARVORES["Guerreiro"])
    for i, ramo in enumerate(arv):
        ids = [n["id"] for n in ramo["nos"]]
        if no_id in ids:
            pos = ids.index(no_id)
            return (i in ramos_liberados(j) and j.habilidades.get(no_id, 0) < NOS[no_id]["max"]
                    and (pos == 0 or j.habilidades.get(ids[pos - 1], 0) >= 1))
    return False

def aprender(j, no_id):
    if pontos_hab_livres(j) <= 0 or not pode_aprender(j, no_id):
        return False
    j.habilidades[no_id] = j.habilidades.get(no_id, 0) + 1
    j._recalcular()
    return True

def auto_habilidades(j):
    """Gasta os pontos livres na ordem da árvore (ramo por ramo). Retorna quantos gastou."""
    gastos = 0
    arv = ARVORES.get(j.classe, ARVORES["Guerreiro"])
    while pontos_hab_livres(j) > 0:
        alvo = next((n["id"] for i in ramos_liberados(j) for n in arv[i]["nos"] if pode_aprender(j, n["id"])), None)
        if not alvo or not aprender(j, alvo):
            break
        gastos += 1
    return gastos

def custo_reset(j):
    return 0 if j.reset_volta < j.ciclo else int(renda_minuto(j) * 10)

def resetar_habilidades(j):
    custo = custo_reset(j)
    if j.ouro < custo:
        return False
    j.ouro -= custo
    if custo == 0:
        j.reset_volta = j.ciclo
    j.habilidades = {}
    j._recalcular()
    return True

def _bonus_habilidades(j, b):
    for no_id, rank in getattr(j, "habilidades", {}).items():
        if no_id in NOS and rank:
            _somar(b, NOS[no_id]["efeito"], NOS[no_id]["valor"] * rank)
    sub = subclasse_info(j)
    if sub:
        for k, v in sub["bonus"].items():
            _somar(b, k, v)

def _bonus_maestria(j, b):
    for stat, pts in getattr(j, "maestria", {}).items():
        _somar(b, f"{stat}%", pts * MAESTRIA_POR_PONTO)

def subclasse_info(j):
    for s in SUBCLASSES.get(j.classe, []):
        if s["nome"] == getattr(j, "subclasse", ""):
            return s
    return None

def escolher_subclasse(j, indice):
    opcoes = SUBCLASSES.get(j.classe, [])
    if j.subclasse or not desbloqueado(j, "subclasse") or not 0 <= indice < len(opcoes):
        return False
    j.subclasse = opcoes[indice]["nome"]
    j.rotacao = ativas_da_classe(j)
    anotar_diario(j, f"Escolheu a subclasse {j.subclasse}.")
    j._recalcular()
    return True

def ativas_da_classe(j):
    ids = [k for k, a in ATIVAS.items() if a.get("classe") == j.classe]
    sub = subclasse_info(j)
    if sub:
        ids.insert(0, sub["ativa"])
    return ids

def rank_ativa(j, ativa_id):
    usos = j.usos.get(ativa_id, 0)
    return sum(1 for u in USOS_RANK if usos >= u)

def rotacao_valida(j):
    disponiveis = ativas_da_classe(j)
    rot = [a for a in j.rotacao if a in disponiveis]
    return rot + [a for a in disponiveis if a not in rot]

# ---------- Luta: ativas, buffs, regras (substituem os ganchos da Fase 1) ----------
def nova_luta(j, regras=()):
    b = j.bonus
    return {"regras": regras, "cd": {}, "buff_dano": (0, 0), "reduz": (0, 0), "crit_extra": (0, 0),
            "mult_dano": 1.0, "mult_inimigo": 1 - min(50, b.get("lentidao", 0)) / 100,
            "reflexo": b.get("contra_ataque", 0) / 100,
            "ativas": rotacao_valida(j) if desbloqueado(j, "habilidades") else [],
            "grupo": [] if "sem_grupo" in regras else grupo_em_luta(j)}

def _dano_ativa(j, a, elemento):
    base = j.dano_fogo() if a.get("magia") else j.atq
    rank = rank_ativa(j, a["id"])
    return base * a["valor"] * (1 + 0.15 * (rank - 1)) * (1 + j.bonus.get("ativa%", 0) / 100) * mult_elemento(a.get("elem"), elemento)

def usar_ativa(j, luta, ativa_id, elemento):
    """Aplica uma ativa. Retorna o dano (0 para buffs)."""
    a = dict(ATIVAS[ativa_id], id=ativa_id)
    j.mana -= a["mana"]
    luta["cd"][ativa_id] = max(1, a["cd"] - int(j.bonus.get("cd", 0)))
    j.usos[ativa_id] = j.usos.get(ativa_id, 0) + 1
    if j.usos[ativa_id] in USOS_RANK[1:]:
        avisar(j, f"🌿 {a['nome']} chegou ao rank {ROMANO[rank_ativa(j, ativa_id) - 1]}!")
    evento(j, "habilidade")
    rank_mult = 1 + 0.15 * (rank_ativa(j, ativa_id) - 1)
    if a["tipo"] == "dano":
        return _dano_ativa(j, a, elemento)
    chave = {"buff_dano": "buff_dano", "reduz": "reduz", "buff_crit": "crit_extra"}[a["tipo"]]
    luta[chave] = (a["valor"] * rank_mult, a["duracao"])
    return 0

def acao_luta(j, luta, vida_inimigo, elemento):
    """Escolhe a ação do turno pela rotação: buffs prontos são gratuitos; depois a ativa de dano pronta.
    Retorna o dano ou None (ação básica)."""
    furia = j.bonus.get("furia", 0) / 100 if j.vida < j.vida_max * 0.5 else 0
    luta["mult_dano"] = (1 + luta["buff_dano"][0]) * (1 + furia)
    for aid in luta["ativas"]:
        a = ATIVAS[aid]
        if luta["cd"].get(aid, 0) or j.mana < a["mana"]:
            continue
        if a["tipo"] != "dano":
            if luta[{"buff_dano": "buff_dano", "reduz": "reduz", "buff_crit": "crit_extra"}[a["tipo"]]][1] == 0:
                usar_ativa(j, luta, aid, elemento)
                luta["mult_dano"] = (1 + luta["buff_dano"][0]) * (1 + furia)
            continue
        if vida_inimigo > j.atq:   # não gasta ativa para terminar um inimigo quase morto
            return usar_ativa(j, luta, aid, elemento)
    return None

def defesa_luta(j, luta, recebido):
    b = j.bonus
    if random.random() < min(40, b.get("esquiva", 0)) / 100:
        return 0
    if luta["reduz"][1]:
        recebido = int(recebido * (1 - luta["reduz"][0]))
    pct = min(60, b.get("escudo_mana", 0)) / 100
    if pct and j.mana > 0:
        absorvido = min(int(recebido * pct), j.mana * 2)
        j.mana -= absorvido // 2
        recebido -= absorvido
    return max(0, recebido)

def fim_turno_luta(j, luta):
    for aid in list(luta["cd"]):
        luta["cd"][aid] = max(0, luta["cd"][aid] - 1)
    for chave in ("buff_dano", "reduz", "crit_extra"):
        valor, dur = luta[chave]
        luta[chave] = (valor, dur - 1) if dur > 1 else (0, 0)

def _gancho_habilidades(j, anota):
    if not desbloqueado(j, "habilidades"):
        return
    if j.auto_hab and pontos_hab_livres(j):
        n = auto_habilidades(j)
        if n:
            anota(f"🌿 +{n} ponto(s) de habilidade aplicados")
    if not j.subclasse and j.nivel >= SUBCLASSE_AUTO_NIVEL and desbloqueado(j, "subclasse"):
        escolher_subclasse(j, 0)
        anota(f"🎭 Subclasse escolhida pelo idle: {j.subclasse} (troque nada: é para sempre)")
GANCHOS_IDLE.append(_gancho_habilidades)

def _dica_habilidades(j):
    if pontos_hab_livres(j) and not j.auto_hab:
        return f"Você tem {pontos_hab_livres(j)} ponto(s) de habilidade [H]."
    if desbloqueado(j, "subclasse") and not j.subclasse:
        return "Escolha sua subclasse na tela de Habilidades [H]."
    return None
DICAS_EXTRA.append(_dica_habilidades)

def tela_habilidades(j):
    msg = ""
    arv = ARVORES.get(j.classe, ARVORES["Guerreiro"])
    ramo = (ramos_liberados(j) or [0])[0]
    letras = "abcdefgh"
    while True:
        limpar()
        print(secao(f"HABILIDADES · {j.classe}{linha_classe_extra(j)}", GN, grossa=True))
        print(f" Pontos livres {YW}{BOLD}{pontos_hab_livres(j)}{RESET} · auto {'ligado' if j.auto_hab else 'desligado'}"
              f" {DIM}(1 ponto por nível do 8 ao 60){RESET}")
        abas = []
        for i, r in enumerate(arv):
            if i not in ramos_liberados(j):
                abas.append(f"{DIM}[{i + 1}] ??? ({requisito_texto(RAMO_DESBLOQUEIO[i])}){RESET}")
            else:
                abas.append(f"{BOLD + YW if i == ramo else ''}[{i + 1}] {r['nome']}{RESET}")
        print(" " + "   ".join(abas))
        r = arv[ramo]
        print(secao(f"{r['nome']} — {r['desc']}"))
        for letra, n in zip(letras, r["nos"]):
            pts = j.habilidades.get(n["id"], 0)
            cor = GN if pts else (YW if pode_aprender(j, n["id"]) else DIM)
            efeito = EFEITO_NOME.get(n["efeito"], n["efeito"]).format(v=n["valor"])
            print(cortar(f" {cor}[{letra}] {'◆ ' if n['chave'] else '  '}{n['nome']:<18}{RESET} {'●' * pts + '○' * (n['max'] - pts):<6}"
                         f" {DIM}{efeito}{' /ponto' if n['max'] > 1 else ''}{RESET}"))
        print(secao("Ativas (ordem da rotação)"))
        for k, aid in enumerate(rotacao_valida(j), 1):
            a = ATIVAS[aid]
            rk = rank_ativa(j, aid)
            prox = f"{j.usos.get(aid, 0)}/{USOS_RANK[rk]} usos" if rk < 5 else "máx"
            print(cortar(f" {k}. {a['nome']:<17} [{ROMANO[rk - 1]}] recarga {a['cd']} mana {a['mana']}"
                         f"{' · ' + a['elem'] if a.get('elem') else ''} {DIM}({prox}){RESET}"))
        print(secao())
        opcoes = "[a-h] aprender [1-3] ramo [M] auto [O] ordem [Z] reset"
        if desbloqueado(j, "subclasse") and not j.subclasse:
            opcoes += f" {YW}[X] subclasse{RESET}"
        if j.nivel >= NIVEL_MAX:
            opcoes += f" [K] maestria {j.maestria_foco}"
        print(cortar(f" {opcoes} [0] sair"))
        if msg:
            print(cortar(f" {CY}{msg}{RESET}"))
        es = ler_tecla()
        msg = ""
        if es in ("0", ""):
            return
        if es.lower() in letras:
            no = r["nos"][letras.index(es.lower())]
            msg = (f"{no['nome']} agora {j.habilidades.get(no['id'], 0)}/{no['max']}." if aprender(j, no["id"])
                   else "Não dá: sem pontos, no máximo, ramo fechado ou falta o anterior.")
        elif es in ("1", "2", "3"):
            if int(es) - 1 in ramos_liberados(j):
                ramo = int(es) - 1
            else:
                msg = f"Esse ramo abre com {requisito_texto(RAMO_DESBLOQUEIO[int(es) - 1])}."
        elif es == "M":
            j.auto_hab = not j.auto_hab
            msg = "O idle gasta os pontos sozinho." if j.auto_hab else "Você escolhe onde gastar."
        elif es == "Z":
            msg = "Árvore zerada: os pontos voltaram." if resetar_habilidades(j) else "Ouro insuficiente."
        elif es == "O":
            rot = rotacao_valida(j)
            print(" Ordem atual: " + " > ".join(f"{i}.{ATIVAS[a]['nome']}" for i, a in enumerate(rot, 1)))
            nova = input(" Nova ordem (ex.: 2 1 3) e ENTER: ").split()
            if sorted(nova) == sorted(str(i) for i in range(1, len(rot) + 1)):
                j.rotacao = [rot[int(n) - 1] for n in nova]
                msg = "Rotação salva."
            else:
                msg = "Ordem inválida."
        elif es == "X" and desbloqueado(j, "subclasse") and not j.subclasse:
            limpar()
            print(secao("SUBCLASSE · escolha para sempre", YW, grossa=True))
            for i, s in enumerate(SUBCLASSES[j.classe], 1):
                print(f" [{i}] {BOLD}{s['nome']}{RESET} — {s['desc']}")
                print(cortar(f"     {DIM}ativa: {ATIVAS[s['ativa']]['nome']} · bônus: "
                             + ", ".join(EFEITO_NOME.get(k, k).format(v=v) for k, v in s["bonus"].items()) + RESET))
            print(" [0] Voltar")
            esc = ler_tecla()
            if esc.isdigit() and escolher_subclasse(j, int(esc) - 1):
                msg = f"Agora você é {j.subclasse}."
        elif es == "K" and j.nivel >= NIVEL_MAX:
            j.maestria_foco = {"atq": "def", "def": "vida", "vida": "atq"}[j.maestria_foco]
            msg = f"Maestria agora vai para {j.maestria_foco}."

def _salvar_habilidades(j):
    return [f"- {k}: {v}" for k, v in j.habilidades.items() if v] + [f"- uso.{k}: {v}" for k, v in j.usos.items()]

def _ler_habilidade(j, linha):
    nome, _, v = linha.rpartition(":")
    nome = nome.strip()
    if nome.startswith("uso."):
        j.usos[nome[4:]] = int(v)
    elif nome in NOS:
        j.habilidades[nome] = min(NOS[nome]["max"], int(v))

# =====================================================================
# v3 · Fase 3 — Companheiros (Sino do Porto) e missões com escolhas
# =====================================================================
# Lore nova (v3): ver .claude/skills/narrativa-andante/references/lore.md, seção "v3".
COMPANHEIROS = {
    "mare": {
        "nome": "Maré", "estrelas": 5, "funcao": "Suporte", "elem": "Água",
        "passiva": {"vida%": 10, "regen": 1}, "ativa": {"nome": "Onda que Volta", "tipo": "cura", "valor": 0.20, "cd": 5},
        "lore": ["Era guarda do Rei. A melhor da ponte. Tinha medo de altura e subiu mesmo assim.",
                 "Levou o barco do pai sem pedir. Deixou a chave do castelo no lugar, como pagamento.",
                 "No Abismo aprendeu que a água não tem fundo. Só tem mais água.",
                 "Segurou a porta com o Rei por um tempo. Depois ele pediu que ela fosse embora.",
                 "Não voltou ao porto porque não sabia como contar ao pai que o Rei ainda está lá."],
        "segredo": "Ela escreve ao pai todo dia. As garrafas chegam vazias porque a tinta do Abismo não seca.",
        "falas": ["🌊 Maré olha para baixo da escada como quem conhece o caminho.",
                  '🌊 Maré: "Meu pai ainda remenda a rede? Claro que remenda."',
                  "🌊 Maré cantarola uma música de pescador. Fora do tom."],
        "missao_fim": "Maré escreve com tinta do porto. Desta vez a garrafa chega com bilhete.",
    },
    "primeiro": {
        "nome": "O Primeiro Andante", "estrelas": 5, "funcao": "Dano", "elem": "Sombra",
        "passiva": {"dano": 10, "crit%": 4}, "ativa": {"nome": "Passo Adiante", "tipo": "dano", "valor": 3.0, "cd": 5},
        "lore": ["Ninguém lembra o nome dele. Nem ele. Só que foi o primeiro a subir.",
                 "Escreveu o Manuscrito com tinta de lula, a única que não apaga no Abismo. Quase.",
                 "Deu ao Rei a ideia de segurar a porta. Se arrepende disso todo dia.",
                 "Girou a torre pela primeira vez. Não sabia que ela ia continuar girando.",
                 "Está cansado. Subiu com você porque queria ver alguém fazer isso melhor."],
        "segredo": "As estátuas do Templo têm o seu rosto porque são feitas para o próximo andante. Ele posou para a primeira.",
        "falas": ["📜 O Primeiro Andante corrige uma página do Manuscrito. Só uma vírgula.",
                  '📜 O Primeiro Andante: "Eu caí nesse degrau. Você não. Bom."',
                  "📜 O Primeiro Andante conta os andares em voz baixa. Erra de propósito."],
        "missao_fim": "Ele lembra o próprio nome por um segundo. Sorri. Esquece de novo, mais leve.",
    },
    "rei": {
        "nome": "Rei sem Coroa", "estrelas": 5, "funcao": "Tanque", "elem": "Luz",
        "passiva": {"def%": 15, "vida%": 6}, "ativa": {"nome": "Ordem Real", "tipo": "escudo", "valor": 0.5, "cd": 5, "duracao": 2},
        "lore": ["Um homem velho de armadura sem brasão. Diz que já foi rei de alguma coisa.",
                 "Desceu primeiro para segurar a porta do Abismo. A sombra que sobe é o que vazou.",
                 "O Rei das Sombras é o que sobrou dele lá embaixo. Este é o que ele conseguiu salvar.",
                 "Quebrou a coroa em duas. Uma metade ficou com a sombra. A outra se perdeu no castelo.",
                 "Não dá ordens há anos porque a última foi 'fiquem'. E todos ficaram."],
        "segredo": "Se as duas metades da coroa se juntarem, ele pode descer de novo. E desta vez não voltar.",
        "falas": ['👑 Rei sem Coroa: "Fiquem." Ele se arrepende assim que fala.',
                  "👑 O Rei sem Coroa passa a mão onde a coroa estaria.",
                  "👑 O Rei sem Coroa saúda um soldado fantasma. O soldado chora."],
        "missao_fim": "Ele diz 'podem ir' para o castelo vazio. Lá longe, armaduras caem no chão, em paz.",
    },
    "brasa": {
        "nome": "Brasa", "estrelas": 4, "funcao": "Dano", "elem": "Fogo",
        "passiva": {"atq%": 6}, "ativa": {"nome": "Sopro", "tipo": "dano", "valor": 2.2, "cd": 4},
        "lore": ["Saiu do ovo no dia em que o Dragão Antigo caiu. Achou que você era a mãe.",
                 "Come carvão, moedas e, uma vez, uma bota inteira.",
                 "Cresce um palmo por volta da torre. Ninguém sabe até onde vai.",
                 "O Dragão Antigo guardava o calor da caverna para o Abismo não congelar tudo.",
                 "Um dia Brasa vai voltar para a caverna e esquentar o mundo. Ainda não. Ainda é pequeno."],
        "segredo": "Brasa sabe o caminho de volta para o ninho. Só não quer ir sozinho.",
        "falas": ["🔥 Brasa espirra. Uma tocha acende sozinha.", "🔥 Brasa dorme no seu colo. Está quente demais.",
                  "🔥 Brasa rosna para um Filhote de Dragão. Ciúme."],
        "missao_fim": "Brasa cospe a primeira chama de verdade. Ele mesmo se assusta.",
    },
    "vela": {
        "nome": "Irmã Vela", "estrelas": 4, "funcao": "Suporte", "elem": "Luz",
        "passiva": {"xp%": 10, "regen": 1}, "ativa": {"nome": "Prece", "tipo": "cura", "valor": 0.15, "cd": 4},
        "lore": ["Reza nomes que nunca ouviu. O seu estava na lista antes de você chegar.",
                 "Ficou cega olhando para as velas que acendem sozinhas. Não se arrepende.",
                 "Ela vê o que vai acontecer. Hoje, você tropeça. Cuidado.",
                 "As velas do Templo acendem para cada andante que sobe. Algumas já se apagaram.",
                 "A sua vela é a mais alta do altar. Ela não diz se isso é bom."],
        "segredo": "Ela já viu como termina. Escolheu subir com você mesmo assim.",
        "falas": ['🕯️ Irmã Vela: "Degrau solto. Esquerda." Ela está certa.', "🕯️ Irmã Vela reza baixinho um nome. O seu.",
                  "🕯️ Irmã Vela acende uma vela com os dedos. Ninguém pergunta."],
        "missao_fim": "Ela toca o seu rosto e diz que você é mais alto do que ela imaginava.",
    },
    "osso": {
        "nome": "Ferreiro Osso", "estrelas": 4, "funcao": "Coleta", "elem": "Terra",
        "passiva": {"ouro%": 12, "loot": 15}, "ativa": {"nome": "Martelada", "tipo": "dano", "valor": 1.8, "cd": 4},
        "lore": ["Ouro primeiro, conversa depois. A conversa nunca chega.",
                 "Forjou a armadura do Guardião. E a lança. E, ele jura, a ponte.",
                 "Perdeu dois dedos na forja e um irmão na torre. Fala mais dos dedos.",
                 "O irmão subiu com uma espada que o Osso fez. A espada voltou. Ele não.",
                 "Cada melhoria que ele te vende é uma que o irmão não teve."],
        "segredo": "A Lâmina do Afogado é a espada do irmão. Ele reconheceu na hora. Não disse nada.",
        "falas": ['🔨 Ferreiro Osso: "Isso aí tá torto." Não está.', "🔨 Ferreiro Osso afia sua lâmina sem pedir.",
                  "🔨 Ferreiro Osso cobra pela conversa. Você nem falou."],
        "missao_fim": 'Osso grava um nome na sua arma. "Pro caso de ela voltar sem você também."',
    },
    "corvo": {
        "nome": "Corvo", "estrelas": 4, "funcao": "Sorte", "elem": "Sombra",
        "passiva": {"sorte%": 20, "loot": 10}, "ativa": {"nome": "Bicada", "tipo": "dano", "valor": 1.5, "cd": 3},
        "lore": ["Trazia moedas antigas para os seus pés. Agora traz para o seu bolso.",
                 "Pousa no ombro de quem vai subir. Já pousou em muitos ombros.",
                 "Entende tudo o que você diz. Responde quando quer.",
                 "Era o mensageiro do Rei. Ainda leva mensagens. Ninguém escreve mais.",
                 "Conta as voltas da torre. A sua é a mais longa que ele já viu."],
        "segredo": "É o Corvo quem toca o sino. Três vezes: uma para cada andante que ainda vai subir.",
        "falas": ["🐦 O Corvo deixa cair uma moeda. É sua. Era sua o tempo todo.", "🐦 O Corvo grasna três vezes. O sino responde.",
                  "🐦 O Corvo rouba uma poção e devolve vazia."],
        "missao_fim": "O Corvo traz uma mensagem do Rei, escrita há cem anos. Diz só: 'obrigado'.",
    },
    "lua": {
        "nome": "Padeira Lua", "estrelas": 3, "funcao": "Cura", "elem": "Luz",
        "passiva": {"vida%": 5}, "ativa": {"nome": "Pão Quente", "tipo": "cura", "valor": 0.12, "cd": 5},
        "lore": ["Faz pão às quatro da manhã. Ninguém sabe para quem são os que sobram.",
                 "Manda pão para os andares. Ninguém sabe como chega. Ela sabe.",
                 "Foi noiva de um guarda do castelo. O pão do Guardião é por ele.",
                 "Não sobe. Diz que alguém precisa ficar para quem volta.",
                 "Toda manhã conta os andantes que passam. Toda noite, os que voltam."],
        "segredo": "O Guardião é o noivo dela. Ele não desce porque não quer que ela veja o que ele virou.",
        "falas": ["🍞 Padeira Lua tira um pão quente de dentro do casaco. De onde?", '🍞 Padeira Lua: "Come. Depois você luta."',
                  "🍞 Padeira Lua olha para o castelo por tempo demais."],
        "missao_fim": "Lua sobe até o portão do castelo pela primeira vez. Não entra. Deixa o pão.",
    },
    "ossos": {
        "nome": "Três Ossos", "estrelas": 3, "funcao": "Sorte", "elem": "Sombra",
        "passiva": {"ouro%": 8, "sorte%": 5}, "ativa": {"nome": "Aposta", "tipo": "aposta", "valor": 3.0, "cd": 4},
        "lore": ["Três esqueletos que contam como um. Discordam sobre quase tudo.",
                 "Jogavam dados no Castelo há cem anos. A aposta era quem ia subir.",
                 "Os três perderam. Subiram juntos. Desceram assim.",
                 "Ainda apostam. Você é a aposta deles agora.",
                 "Dois apostaram que você chega ao fim. Um apostou contra. Ele não diz qual."],
        "segredo": "O dado deles tem seis faces iguais. Sempre teve.",
        "falas": ["🎲 Os Três Ossos apostam se você vai tropeçar. Você tropeça. Um deles comemora.",
                  "🎲 Os Três Ossos discutem sobre quem é o do meio.", "🎲 Um dos Três Ossos perde um dedo. Os outros dois apostam onde caiu."],
        "missao_fim": "Os três jogam o dado uma última vez. Sai seis. Sempre sai seis.",
    },
    "troco": {
        "nome": "Mercador Troco", "estrelas": 3, "funcao": "Coleta", "elem": "Terra",
        "passiva": {"ouro%": 10}, "ativa": {"nome": "Troco Errado", "tipo": "dano", "valor": 1.4, "cd": 4},
        "lore": ["Erra o troco a seu favor. Sempre. Diz que é estratégia.",
                 "Vende para os andares de cima e compra dos de baixo. O lucro é a escada.",
                 "Já vendeu uma coroa partida ao meio. Ninguém comprou a outra metade.",
                 "Tem medo de altura. Sobe mesmo assim, porque lá em cima o ouro vale menos.",
                 "Erra o troco porque um andante errou o dele, uma vez, e salvou a loja."],
        "segredo": "Ele sabe onde está a outra metade da coroa. Está esperando o preço certo.",
        "falas": ["💰 Mercador Troco te dá troco de uma compra que você não fez.", "💰 Mercador Troco vende uma pedra para um monstro.",
                  '💰 Mercador Troco: "Isso aqui? Raríssimo." É uma colher.'],
        "missao_fim": "Troco acerta o troco pela primeira vez. Fica tão abalado que fecha a loja por um dia.",
    },
    "soldado": {
        "nome": "Soldado Fantasma", "estrelas": 3, "funcao": "Tanque", "elem": "Luz",
        "passiva": {"def%": 6}, "ativa": {"nome": "Escudo Velho", "tipo": "escudo", "valor": 0.35, "cd": 5, "duracao": 2},
        "lore": ["Ainda espera ordens do Rei. Aceitou as suas, por enquanto.",
                 "Morreu na ponte. Ficou porque ninguém o dispensou.",
                 "Conhece cada pedra do castelo. Contou todas, duas vezes.",
                 "Marchou com o Guardião. Era o mais baixo da fila.",
                 "Ouviu a última ordem do Rei: 'fiquem'. Ficou."],
        "segredo": "Se o Rei disser 'podem ir', todos os soldados do castelo descansam. Ele quer ouvir isso.",
        "falas": ["🛡️ O Soldado Fantasma bate continência para uma porta.", "🛡️ O Soldado Fantasma marcha no mesmo passo que você.",
                  "🛡️ O Soldado Fantasma pergunta se o Rei já deu alguma ordem nova."],
        "missao_fim": "Ele tira o elmo pela primeira vez em cem anos. Não tem rosto. Parece aliviado.",
    },
    "kobold": {
        "nome": "Kobold Mineiro", "estrelas": 3, "funcao": "Coleta", "elem": "Terra",
        "passiva": {"loot": 10}, "ativa": {"nome": "Picareta", "tipo": "dano", "valor": 1.5, "cd": 3},
        "lore": ["Troca qualquer coisa por pão. Troca pão por nada.",
                 "Cava em direção ao calor desde que nasceu. Diz que é o caminho de casa.",
                 "Acha pó de forja onde ninguém acha. Ou rouba. Não fica claro.",
                 "A família dele vive mais fundo que o Abismo. Subiu para pedir ajuda e esqueceu para quê.",
                 "Lembrou: o calor está acabando lá embaixo. Ele precisa da Brasa."],
        "segredo": "Kobolds e dragões são primos. Ele não quer que a Brasa saiba ainda.",
        "falas": ["⛏️ O Kobold cava um buraco no meio da sala. Só porque sim.", "⛏️ O Kobold troca uma pedra brilhante por meio pão seu.",
                  "⛏️ O Kobold encosta a orelha no chão e sorri."],
        "missao_fim": "O Kobold desenha um mapa do caminho de casa. Para no meio. 'Depois', ele diz.",
    },
}
ESTRELAS = {3: {"cor": WT, "chance": 85}, 4: {"cor": MG, "chance": 13}, 5: {"cor": YW, "chance": 2}}
PODER_FUNCAO = {"Dano": 0.22, "Tanque": 0.08, "Suporte": 0.08, "Coleta": 0.06, "Sorte": 0.06, "Cura": 0.06}
SINO_1X, SINO_10X = 10, 90
PIEDADE_4, PIEDADE_5 = 10, 90
MEMORIAS_MAX = 5
CONCHAS_POR_MEMORIA_EXTRA = 15
DESTAQUES = ["mare", "primeiro", "rei"]      # o ★5 em destaque muda a cada volta

def destaque_sino(j):
    return DESTAQUES[(j.ciclo - 1) % len(DESTAQUES)]

def slots_grupo(j):
    return sum(1 for k in ("grupo", "grupo2", "grupo3") if desbloqueado(j, k))

def comp_nivel(c):
    return min(50, 1 + int((c["xp"] / 20) ** 0.5))

def dar_companheiro(j, cid):
    """Novo companheiro ou Memória (repetido). Retorna o texto."""
    info = COMPANHEIROS[cid]
    c = j.companheiros.get(cid)
    if c is None:
        j.companheiros[cid] = {"xp": 0, "memorias": 0, "afinidade": 3 if cid == "lua" and not j.marcas.get("padeira_traida") else 0,
                               "batalhas": 0}
        anotar_diario(j, f"{info['nome']} se juntou a você. {info['lore'][0]}")
        if len(j.grupo) < slots_grupo(j):
            j.grupo.append(cid)
            j._recalcular()
        return f"NOVO! {info['nome']}"
    if c["memorias"] < MEMORIAS_MAX:
        c["memorias"] += 1
        if c["memorias"] < len(info["lore"]):
            anotar_diario(j, f"Memória de {info['nome']}: {info['lore'][c['memorias']]}")
        j._recalcular()
        return f"Memória {c['memorias']}/{MEMORIAS_MAX} de {info['nome']}"
    j.conchas += CONCHAS_POR_MEMORIA_EXTRA
    return f"{info['nome']} (memórias completas: +{CONCHAS_POR_MEMORIA_EXTRA} conchas)"

def tocar_sino(j, vezes=1):
    """Gacha: retorna [(cid, texto)]. Piedade: ★4 a cada 10, ★5 em 90; 10× garante ★4+."""
    custo = SINO_10X if vezes == 10 else SINO_1X * vezes
    if j.conchas < custo:
        return []
    j.conchas -= custo
    resultado = []
    for i in range(vezes):
        j.piedade4 += 1; j.piedade5 += 1
        r = random.random() * 100
        estrelas = 5 if r < ESTRELAS[5]["chance"] else 4 if r < ESTRELAS[5]["chance"] + ESTRELAS[4]["chance"] else 3
        if j.piedade5 >= PIEDADE_5:
            estrelas = 5
        elif estrelas < 4 and (j.piedade4 >= PIEDADE_4 or (vezes == 10 and i == 9 and not any(COMPANHEIROS[c]["estrelas"] >= 4 for c, _ in resultado))):
            estrelas = 4
        if estrelas == 5:
            j.piedade5 = 0
        if estrelas >= 4:
            j.piedade4 = 0
        pool = [c for c, d in COMPANHEIROS.items() if d["estrelas"] == estrelas]
        if estrelas == 5:
            dest = destaque_sino(j)
            cid = dest if random.random() < 0.5 else random.choice(pool)
            if cid != dest and j.marcas.get("mare_chamada") and random.random() < 0.5:
                cid = "mare"
        else:
            cid = random.choice(pool)
        resultado.append((cid, dar_companheiro(j, cid)))
    evento(j, "sino", vezes)
    return resultado

def _mult_comp(j, cid):
    c = j.companheiros[cid]
    return (1 + 0.2 * c["memorias"]) * (1 + 0.01 * comp_nivel(c))

def _bonus_grupo(j, b):
    for cid in getattr(j, "grupo", []):
        if cid in j.companheiros:
            m = _mult_comp(j, cid)
            for k, v in COMPANHEIROS[cid]["passiva"].items():
                _somar(b, k, v * m)

def grupo_em_luta(j):
    return [cid for cid in getattr(j, "grupo", []) if cid in j.companheiros]

def ataque_grupo(j, luta, elemento):
    """Cada companheiro do grupo ataca todo turno e usa a ativa dele quando a recarga deixa."""
    total = 0
    comando = 1 + j.bonus.get("comando", 0) / 100
    for cid in luta["grupo"]:
        info, c = COMPANHEIROS[cid], j.companheiros[cid]
        forca = j.atq * (1 + 0.02 * (comp_nivel(c) - 1)) * comando
        total += forca * PODER_FUNCAO[info["funcao"]] * mult_elemento(info["elem"], elemento)
        chave = "cd_" + cid
        if luta["cd"].get(chave, 0):
            continue
        a = info["ativa"]
        final = 1.5 if j.marcas.get(f"laco_{cid}") else 1.0      # missão pessoal: habilidade final
        luta["cd"][chave] = a["cd"]
        if a["tipo"] == "dano":
            total += forca * a["valor"] * 0.5 * final * mult_elemento(info["elem"], elemento)
        elif a["tipo"] == "aposta":
            total += forca * random.uniform(0, a["valor"]) * 0.5 * final
        elif a["tipo"] == "cura":
            j.vida = min(j.vida_max, j.vida + int(j.vida_max * a["valor"] * final))
        elif a["tipo"] == "escudo" and not luta["reduz"][1]:
            luta["reduz"] = (min(0.8, a["valor"] * final), a.get("duracao", 2))
    return int(total)

def _gancho_grupo(j, anota):
    if not desbloqueado(j, "gacha"):
        return
    if "corvo" not in j.companheiros and not j.marcas.get("corvo_veio"):
        j.marcas["corvo_veio"] = True
        dar_companheiro(j, "corvo")
        anota("🐦 Do alto do sino, um corvo desce e pousa no seu ombro. Ele fica.")
    vagas = slots_grupo(j) - len(j.grupo)
    if j.auto_grupo and vagas > 0:
        livres = sorted((c for c in j.companheiros if c not in j.grupo),
                        key=lambda c: (COMPANHEIROS[c]["estrelas"], j.companheiros[c]["memorias"], j.companheiros[c]["xp"]), reverse=True)
        for cid in livres[:vagas]:
            j.grupo.append(cid)
            anota(f"🤝 {COMPANHEIROS[cid]['nome']} entrou no grupo.")
        if livres[:vagas]:
            j._recalcular()
GANCHOS_IDLE.append(_gancho_grupo)

def registrar_batalha_grupo(j):
    """Depois de cada vitória: XP e afinidade dos companheiros do grupo (afinidade por luta vai até 8)."""
    mudou = False
    for cid in j.grupo:
        c = j.companheiros.get(cid)
        if not c:
            continue
        nv = comp_nivel(c)
        c["xp"] += 1; c["batalhas"] += 1
        if comp_nivel(c) != nv:
            mudou = True
        if c["batalhas"] % 300 == 0 and c["afinidade"] < 8:
            subir_afinidade(j, cid)
    if mudou:
        j._recalcular()

def subir_afinidade(j, cid):
    c, info = j.companheiros[cid], COMPANHEIROS[cid]
    c["afinidade"] = min(10, c["afinidade"] + 1)
    avisar(j, f"💞 Afinidade com {info['nome']}: {c['afinidade']}/10")
    if c["afinidade"] == 10:
        avisar(j, f"💞 {info['nome']} te conta um segredo. (Grupo [G])", grande=True)
        anotar_diario(j, f"Segredo de {info['nome']}: {info['segredo']}")

def custo_presente(j, cid):
    return 20 * (j.companheiros[cid]["afinidade"] + 1)

def dar_presente(j, cid):
    c = j.companheiros.get(cid)
    if not c or c["afinidade"] >= 10 or j.po_forja < custo_presente(j, cid):
        return False
    j.po_forja -= custo_presente(j, cid)
    subir_afinidade(j, cid)
    return True

def _dica_grupo(j):
    if desbloqueado(j, "gacha") and j.conchas >= SINO_10X:
        return f"{j.conchas} conchas: o Sino do Porto dá 10 toques [S]."
    if j.escolha_pendente:
        return "Uma escolha espera por você (aparece ao voltar ao menu)."
    return None
DICAS_EXTRA.append(_dica_grupo)

def _linhas_grupo_idle(j):
    if not j.grupo:
        return []
    nomes = " · ".join(f"{COMPANHEIROS[c]['nome']} Nv{comp_nivel(j.companheiros[c])}" for c in j.grupo if c in j.companheiros)
    return [f" Grupo {nomes}"]

LINHAS_IDLE_EXTRA.append(_linhas_grupo_idle)

# ---------- Missões ----------
# obj: evento (ver evento()), qt e filtro (andar = andar ou acima, andar_exato, grupo = companheiro no grupo).
# req: nivel, volta, chefes, missao (feita), marca, desbloqueio, companheiro, afinidade (cid, n).
# escolha: o idle espera 10 s por [1]/[2]; sem resposta, fica a opção "padrao".
MISSOES = {
    # --- O Mar Escuro (Pescador) ---
    "mar_escuro_1": {"cadeia": "O Mar Escuro", "nome": "A Rede Vazia", "tipo": "História",
        "req": {"chefes": 1}, "obj": {"evento": "chefe", "qt": 3}, "objetivo": "Vença 3 chefes",
        "inicio": ['Pescador: "Você voltou. Então talvez volte de novo."',
                   'Pescador: "Ninguém pergunta por que um pescador tem a chave do castelo."'],
        "escolha": {"pergunta": 'Pescador: "Quer saber de quem é a chave?"', "padrao": 0, "opcoes": [
            {"texto": "Quero saber.", "resposta": 'Pescador: "Da minha filha. Guarda do Rei. Subiu e não desceu."',
             "marcas": ["pescador_confiou"], "bom": True},
            {"texto": "Não é da minha conta.", "resposta": 'Pescador: "Bom. Ninguém nunca acha que é."',
             "marcas": ["pescador_calado"], "recompensa": {"ouro_min": 10}}]},
        "recompensa": {"conchas": 10, "xp": 200}},
    "mar_escuro_2": {"cadeia": "O Mar Escuro", "nome": "A Assinatura", "tipo": "História",
        "req": {"missao": "mar_escuro_1", "volta": 2}, "obj": {"evento": "chefe", "qt": 1, "filtro": {"andar_exato": 4}},
        "objetivo": "Vença o Cumulador",
        "inicio": ["O Manuscrito pesa mais que ontem. Uma página nova apareceu no fim."],
        "fim": ["À luz das velas do Templo, uma assinatura: 'o primeiro'.",
                "Alguém subiu antes de todos. E escreveu para quem viesse depois."],
        "recompensa": {"conchas": 15, "bau": "Baú de Prata"}, "marcas": ["manuscrito_assinado"]},
    "mar_escuro_3": {"cadeia": "O Mar Escuro", "nome": "Notícia do Abismo", "tipo": "História",
        "req": {"missao": "mar_escuro_2", "volta": 3}, "obj": {"evento": "chefe", "qt": 1, "filtro": {"andar_exato": 5}},
        "objetivo": "Vença o Rei das Sombras",
        "inicio": ['Pescador: "Se você descer lá de novo... escuta por mim."'],
        "escolha": {"pergunta": "No Abismo, uma voz repete a última coisa que o Pescador disse.", "padrao": 0, "opcoes": [
            {"texto": "Chamar a filha dele pelo nome.", "resposta": "A escuridão para de repetir. Por um instante, ela escuta.",
             "marcas": ["mare_chamada"], "recompensa": {"conchas": 30}, "bom": True},
            {"texto": "Ficar em silêncio.", "resposta": "O eco se cala com você. Você sobe com algo frio no bolso.",
             "marcas": ["abismo_silencio"], "recompensa": {"bau": "Baú Abissal"}}]},
        "recompensa": {"xp": 500}},
    "mar_escuro_4": {"cadeia": "O Mar Escuro", "nome": "O Barco", "tipo": "História",
        "req": {"missao": "mar_escuro_3", "nivel": 20, "desbloqueio": "mapa"}, "obj": {"evento": "casa", "qt": 10},
        "objetivo": "Revele 10 casas do mapa",
        "inicio": ['Pescador: "Ela levou o meu barco. Eu construí outro, devagar."'],
        "fim": ['Pescador: "Ele é seu. A Ilha do Farol fica a leste. Não se perca."'],
        "recompensa": {"conchas": 20}, "marcas": ["barco"]},
    # --- O Sino (gacha) ---
    "sino_tres": {"cadeia": "O Sino", "nome": "Três Toques", "tipo": "História",
        "req": {"desbloqueio": "gacha"}, "obj": {"evento": "sino", "qt": 1}, "objetivo": "Toque o Sino do Porto [S]",
        "inicio": ["O sino tocou três vezes de novo. Desta vez, alguém viu: era o Corvo."],
        "fim": ["Cada toque chama alguém que também está subindo. Alguns você já conhece."],
        "recompensa": {"conchas": 10}, "marcas": ["sino_tres"]},
    # --- A Padeira e o Guardião ---
    "padeira": {"cadeia": "A Padeira e o Guardião", "nome": "Pão para o Castelo", "tipo": "Secundária",
        "req": {"volta": 2}, "obj": {"evento": "monstro", "qt": 80, "filtro": {"andar": 2}},
        "objetivo": "Derrote 80 monstros no Castelo ou acima",
        "inicio": ['Padeira: "Leva esse pão para o Guardião. Ele não come há anos. Diz que não precisa."'],
        "escolha": {"pergunta": "O pão ainda está quente quando você chega ao portão.", "padrao": 0, "opcoes": [
            {"texto": "Entregar o pão ao Guardião.", "resposta": 'Guardião: "...Diga a ela que o portão nunca foi para ela."',
             "marcas": ["guardiao_amigo"], "recompensa": {"xp": 300}, "bom": True},
            {"texto": "Comer o pão no caminho.", "resposta": "Estava ótimo. A padeira vai saber. Padeiras sempre sabem.",
             "marcas": ["padeira_traida"], "recompensa": {"ouro_min": 20}}]},
        "recompensa": {"conchas": 10}},
    # --- Páginas do Manuscrito (uma por volta) ---
    "pagina_1": {"cadeia": "Páginas do Manuscrito", "nome": "Página 1", "tipo": "História",
        "req": {"volta": 2}, "obj": {"evento": "volta", "qt": 1}, "objetivo": "Complete a volta",
        "fim": ["📖 'Subi cinco andares e desci ao mar. A torre não sobe. Ela afunda, e nós com ela.'"],
        "recompensa": {"conchas": 15}},
    "pagina_2": {"cadeia": "Páginas do Manuscrito", "nome": "Página 2", "tipo": "História",
        "req": {"missao": "pagina_1", "volta": 3}, "obj": {"evento": "volta", "qt": 1}, "objetivo": "Complete a volta",
        "fim": ["📖 'O Rei não morreu. Desceu primeiro para segurar a porta. Ficou do outro lado.'"],
        "recompensa": {"conchas": 15}},
    "pagina_3": {"cadeia": "Páginas do Manuscrito", "nome": "Página 3", "tipo": "História",
        "req": {"missao": "pagina_2", "volta": 4}, "obj": {"evento": "volta", "qt": 1}, "objetivo": "Complete a volta",
        "fim": ["📖 'O Cumulador guarda o que deixamos para trás a cada volta. Está ficando pesado.'"],
        "recompensa": {"conchas": 20}},
    "pagina_4": {"cadeia": "Páginas do Manuscrito", "nome": "Página 4", "tipo": "História",
        "req": {"missao": "pagina_3", "volta": 5}, "obj": {"evento": "volta", "qt": 1}, "objetivo": "Complete a volta",
        "fim": ["📖 'Quando o Rei cai, a torre gira para não afundar de vez. Alguém precisa continuar subindo.'"],
        "recompensa": {"conchas": 20}},
    "pagina_5": {"cadeia": "Páginas do Manuscrito", "nome": "Página 5", "tipo": "História",
        "req": {"missao": "pagina_4", "volta": 6}, "obj": {"evento": "volta", "qt": 1}, "objetivo": "Complete a volta",
        "fim": ["📖 'Se você está lendo isto, você é o próximo. Sinto muito. E obrigado. — o primeiro'"],
        "recompensa": {"conchas": 40, "bau": "Baú de Ouro"}, "marcas": ["manuscrito_completo"]},
    # --- Despertar ---
    "segundo_folego": {"cadeia": "O Segundo Fôlego", "nome": "O Segundo Fôlego", "tipo": "História",
        "req": {"desbloqueio": "despertar"}, "obj": {"evento": "chefe", "qt": 10}, "objetivo": "Vença 10 chefes no nível máximo",
        "inicio": ["Seu corpo parou de crescer. A torre, não.",
                   "Irmã Vela, de longe: 'Respira. O segundo fôlego dói mais que o primeiro.'"],
        "fim": ["🌅 Você respira fundo e o mundo fica um pouco mais largo. Nível máximo: 120."],
        "recompensa": {"conchas": 50, "bau": "Baú Abissal"}, "marcas": ["despertado"]},
}

def _gerar_missoes_pessoais():
    for cid, info in COMPANHEIROS.items():
        MISSOES[f"laco_{cid}"] = {
            "cadeia": f"Laço: {info['nome']}", "nome": f"Laço: {info['nome']}", "tipo": "Pessoal",
            "req": {"companheiro": cid, "afinidade": (cid, 5)}, "obj": {"evento": "monstro", "qt": 150, "filtro": {"grupo": cid}},
            "objetivo": f"Vença 150 monstros com {info['nome']} no grupo",
            "inicio": [f"{info['nome']} pede para conversar a sós. Depois, só pede que você suba junto."],
            "fim": [info["missao_fim"], f"[✨ {info['ativa']['nome']} agora é a habilidade final: +50%]"],
            "recompensa": {"conchas": 20}, "marcas": [f"laco_{cid}"]}
_gerar_missoes_pessoais()
ESPERA_ESCOLHA = 10         # segundos que o idle espera por uma escolha

def _req_missao_ok(j, req):
    if j.nivel < req.get("nivel", 0) or j.ciclo < req.get("volta", 1) or j.stats.get("chefe", 0) < req.get("chefes", 0):
        return False
    if req.get("missao") and req["missao"] not in j.missoes_feitas:
        return False
    if req.get("marca") and not j.marcas.get(req["marca"]):
        return False
    if req.get("desbloqueio") and not desbloqueado(j, req["desbloqueio"]):
        return False
    if req.get("companheiro") and req["companheiro"] not in j.companheiros:
        return False
    if req.get("afinidade"):
        cid, n = req["afinidade"]
        if j.companheiros.get(cid, {}).get("afinidade", 0) < n:
            return False
    return True

def atualizar_missoes(j):
    for mid, m in MISSOES.items():
        if mid in j.missoes_feitas or mid in j.missoes_ativas or not _req_missao_ok(j, m["req"]):
            continue
        j.missoes_ativas[mid] = 0
        avisar(j, f"📜 Missão: {m['nome']} — {m['objetivo']}", grande=True)
        for linha in m.get("inicio", []):
            avisar(j, f"   {linha}")
        anotar_diario(j, f"Missão começou: {m['nome']}.")

def _filtro_missao_ok(filtro, ctx):
    for k, v in filtro.items():
        if k == "andar" and ctx.get("andar", 0) < v: return False
        if k == "andar_exato" and ctx.get("andar") != v: return False
        if k == "grupo" and v not in ctx.get("grupo", ()): return False
    return True

def progresso_missoes(j, tipo, qt, ctx):
    for mid in list(getattr(j, "missoes_ativas", {})):
        m = MISSOES.get(mid)
        if not m or m["obj"]["evento"] != tipo or not _filtro_missao_ok(m["obj"].get("filtro", {}), ctx):
            continue
        if j.missoes_ativas[mid] >= m["obj"]["qt"]:
            continue
        j.missoes_ativas[mid] = min(m["obj"]["qt"], j.missoes_ativas[mid] + qt)
        if j.missoes_ativas[mid] >= m["obj"]["qt"]:
            if m.get("escolha") and not j.escolha_pendente:
                j.escolha_pendente = mid
                j.escolha_prazo = time.time() + ESPERA_ESCOLHA
                avisar(j, f"❓ {m['escolha']['pergunta']}", grande=True)
            elif not m.get("escolha"):
                finalizar_missao(j, mid, None)

def finalizar_missao(j, mid, opcao):
    m = MISSOES[mid]
    linhas = []
    r = dict(m.get("recompensa", {}))
    marcas = list(m.get("marcas", []))
    if m.get("escolha"):
        op = m["escolha"]["opcoes"][opcao if opcao is not None else m["escolha"]["padrao"]]
        linhas.append(f"   ▸ {op['texto']}")
        linhas.append(f"   {op['resposta']}")
        for k, v in op.get("recompensa", {}).items():
            r[k] = r.get(k, 0) + v if k != "bau" else v
        marcas += op.get("marcas", [])
        if op.get("bom"):
            j.dialogo_bom()
        j.missoes_feitas[mid] = (opcao if opcao is not None else m["escolha"]["padrao"]) + 1
    else:
        j.missoes_feitas[mid] = 0
    if "ouro_min" in r:
        r["ouro"] = r.get("ouro", 0) + int(renda_minuto(j) * r.pop("ouro_min"))
    for marca in marcas:
        j.marcas[marca] = True
    j.missoes_ativas.pop(mid, None)
    if j.escolha_pendente == mid:
        j.escolha_pendente = ""
    texto = dar_recompensa(j, r)
    avisar(j, f"📜 Missão cumprida: {m['nome']} ({texto})", grande=True)
    for linha in linhas + [f"   {l}" for l in m.get("fim", [])]:
        avisar(j, linha)
    anotar_diario(j, f"Missão cumprida: {m['nome']}." + (f" Escolha: {linhas[0].strip()[2:]}" if linhas else ""))
    for l in m.get("fim", []):
        anotar_diario(j, l)
    evento(j, "missao")

def resolver_escolha(j, opcao=None):
    """Resolve a escolha pendente (opcao None = padrão). Retorna True se havia uma."""
    mid = j.escolha_pendente
    if not mid or mid not in MISSOES:
        j.escolha_pendente = ""
        return False
    n = len(MISSOES[mid]["escolha"]["opcoes"])
    finalizar_missao(j, mid, opcao if opcao is not None and 0 <= opcao < n else None)
    return True

def _gancho_missoes(j, anota):
    atualizar_missoes(j)
    if j.escolha_pendente and (not j.idle_interativo or time.time() >= j.escolha_prazo):
        resolver_escolha(j)
GANCHOS_IDLE.append(_gancho_missoes)

def linhas_escolha(j):
    """Bloco mostrado no painel do idle enquanto espera a escolha."""
    m = MISSOES.get(j.escolha_pendente)
    if not m:
        return []
    resta = max(0, int(j.escolha_prazo - time.time()))
    linhas = [secao(f"ESCOLHA · {m['nome']} · {resta}s", MG, grossa=True), f" {m['escolha']['pergunta']}"]
    for i, op in enumerate(m["escolha"]["opcoes"], 1):
        padrao = f" {DIM}(padrão){RESET}" if i - 1 == m["escolha"]["padrao"] else ""
        linhas.append(f"  {BOLD}[{i}]{RESET} {op['texto']}{padrao}")
    return linhas

def escolher_no_menu(j):
    m = MISSOES.get(j.escolha_pendente)
    if not m:
        j.escolha_pendente = ""
        return
    print(secao(f"ESCOLHA · {m['nome']}", MG, grossa=True))
    for l in quebrar(visivel(m["escolha"]["pergunta"])):
        digitar(l)
    for i, op in enumerate(m["escolha"]["opcoes"], 1):
        print(f" [{i}] {op['texto']}")
    es = ler_tecla()
    resolver_escolha(j, int(es) - 1 if es.isdigit() else None)
    print()
    for t, _ in j.avisos:
        for l in quebrar(visivel(t).strip()):
            digitar(l)
    j.avisos.clear()
    pausa()



def tela_sino(j):
    msg = []
    while True:
        limpar()
        dest = COMPANHEIROS[destaque_sino(j)]
        print(secao("SINO DO PORTO", YW, grossa=True))
        print(f" Conchas {CY}{BOLD}◎ {j.conchas}{RESET}   Destaque desta volta: {YW}{BOLD}★5 {dest['nome']}{RESET}")
        for l in quebrar(f'"{dest["lore"][0]}"'):
            print(f"{DIM}{l}{RESET}")
        print(f" ★3 85% · ★4 13% · ★5 2%   {DIM}piedade: ★4 em {PIEDADE_4 - j.piedade4} · ★5 em {PIEDADE_5 - j.piedade5}{RESET}")
        print(f" {DIM}Repetido vira Memória: um capítulo de lore e +20% de força (até {MEMORIAS_MAX}).{RESET}")
        print(secao())
        print(f" [1] Tocar 1× ({SINO_1X} ◎)   [2] Tocar 10× ({SINO_10X} ◎, garante ★4+)   [0] Voltar")
        for l in msg:
            print(" " + l)
        es = ler_tecla()
        msg = []
        if es in ("0", ""):
            return
        if es in ("1", "2"):
            res = tocar_sino(j, 1 if es == "1" else 10)
            if not res:
                msg = ["Conchas insuficientes. Chefes, contratos, missões e o Presente do Porto dão mais."]
                continue
            limpar()
            print(secao("SINO DO PORTO", YW, grossa=True))
            sys.stdout.write(" 🔔 ")
            for _ in range(3):
                sys.stdout.write("dlim... "); sys.stdout.flush(); time.sleep(0.35)
            print()
            for cid, texto in res:
                info = COMPANHEIROS[cid]
                cor = ESTRELAS[info["estrelas"]]["cor"]
                print(cortar(f"   {cor}{BOLD}{'★' * info['estrelas']:<5} {info['nome']:<19}{RESET} {DIM}{texto}{RESET}"))
                if info["estrelas"] >= 4:
                    time.sleep(0.3)
            pausa()

def tela_grupo(j):
    msg = ""
    letras = "abcdefghijkl"
    while True:
        limpar()
        print(secao(f"GRUPO · {len(j.grupo)}/{slots_grupo(j)} no grupo · coleção {len(j.companheiros)}/{len(COMPANHEIROS)}", CY, grossa=True))
        print(f" {DIM}Quem está no grupo luta com você, dá a passiva e ganha afinidade.{RESET}")
        donos = sorted(j.companheiros, key=lambda c: (-COMPANHEIROS[c]["estrelas"], COMPANHEIROS[c]["nome"]))
        for letra, cid in zip(letras, donos):
            info, c = COMPANHEIROS[cid], j.companheiros[cid]
            cor = ESTRELAS[info["estrelas"]]["cor"]
            marca = f"{GN}● grupo{RESET}" if cid in j.grupo else ""
            print(cortar(f" [{letra}] {cor}{BOLD}{'★' * info['estrelas']:<5} {info['nome']:<19}{RESET} Nv {comp_nivel(c):<3}"
                         f" {RD}{'♥' * c['afinidade']}{RESET}{DIM}{'·' * (10 - c['afinidade'])}{RESET} mem {c['memorias']} {marca}"))
        print(secao())
        print(f" [letra] ficha, entrar/sair, presente   [M] auto-grupo: {'ligado' if j.auto_grupo else 'desligado'}   [0] Voltar")
        if msg:
            print(cortar(f" {CY}{msg}{RESET}"))
        es = ler_tecla()
        msg = ""
        if es in ("0", ""):
            return
        if es == "M":
            j.auto_grupo = not j.auto_grupo
            msg = "Auto-grupo " + ("ligado: vagas são preenchidas sozinhas." if j.auto_grupo else "desligado.")
        elif es.lower() in letras[:len(donos)]:
            msg = ficha_companheiro(j, donos[letras.index(es.lower())])

def ficha_companheiro(j, cid):
    info, c = COMPANHEIROS[cid], j.companheiros[cid]
    limpar()
    print(secao(f"{'★' * info['estrelas']} {info['nome']}", ESTRELAS[info["estrelas"]]["cor"], grossa=True))
    m = _mult_comp(j, cid)
    passiva = ", ".join(EFEITO_NOME.get(k, k).format(v=round(v * m, 1)) for k, v in info["passiva"].items())
    a = info["ativa"]
    print(cortar(f" {info['funcao']} · {info['elem']} · Nv {comp_nivel(c)} · {c['batalhas']} batalhas · afinidade {c['afinidade']}/10"))
    print(cortar(f" Passiva: {passiva}   Ativa: {a['nome']}" + (" (final +50%)" if j.marcas.get(f"laco_{cid}") else "")))
    print(secao("Lore"))
    for i, cap in enumerate(info["lore"]):
        if i <= c["memorias"]:
            for l in quebrar(cap, f" {i + 1}. "):
                print(l)
        else:
            print(f" {DIM}{i + 1}. ??? (Memória {i}){RESET}")
    print(secao("Segredo"))
    for l in (quebrar(info["segredo"]) if c["afinidade"] >= 10 else [f" {DIM}??? (afinidade 10){RESET}"]):
        print(l)
    laco = f"laco_{cid}"
    estado = "cumprida" if laco in j.missoes_feitas else "ativa" if laco in j.missoes_ativas else "começa na afinidade 5"
    print(f" {DIM}Missão pessoal: {estado}{RESET}")
    print(secao())
    acao = "sair do grupo" if cid in j.grupo else "entrar no grupo"
    print(f" [G] {acao}   [P] presente ({custo_presente(j, cid)} pó, você tem {j.po_forja})   [0] Voltar")
    es = ler_tecla()
    if es == "G":
        if cid in j.grupo:
            j.grupo.remove(cid); j._recalcular()
            return f"{info['nome']} saiu do grupo."
        if len(j.grupo) < slots_grupo(j):
            j.grupo.append(cid); j._recalcular()
            return f"{info['nome']} entrou no grupo."
        return "Grupo cheio: tire alguém antes."
    if es == "P":
        return (f"{info['nome']} gostou. Afinidade {c['afinidade']}/10." if dar_presente(j, cid)
                else f"Precisa de {custo_presente(j, cid)} pó de forja (ou a afinidade já é 10).")
    return ""

def _salvar_companheiros(j):
    return [f"- {COMPANHEIROS[cid]['nome']} | xp={c['xp']} memorias={c['memorias']} afinidade={c['afinidade']} batalhas={c['batalhas']}"
            + (" | grupo" if cid in j.grupo else "") for cid, c in j.companheiros.items()]

def _ler_companheiro(j, linha):
    partes = [p.strip() for p in linha.split("|")]
    por_nome = {d["nome"]: k for k, d in COMPANHEIROS.items()}
    cid = por_nome.get(partes[0])
    if not cid:
        return
    kv = _kv(partes[1]) if len(partes) > 1 else {}
    j.companheiros[cid] = {"xp": int(kv.get("xp", 0)), "memorias": min(MEMORIAS_MAX, int(kv.get("memorias", 0))),
                           "afinidade": min(10, int(kv.get("afinidade", 0))), "batalhas": int(kv.get("batalhas", 0))}
    if len(partes) > 2 and partes[2] == "grupo" and cid not in j.grupo:
        j.grupo.append(cid)

def _salvar_missoes(j):
    return ([f"- [x] {mid}" + (f" | escolha={v}" if v else "") for mid, v in j.missoes_feitas.items()]
            + [f"- [ ] {mid} | {prog}/{MISSOES[mid]['obj']['qt']}" for mid, prog in j.missoes_ativas.items() if mid in MISSOES])

def _ler_missao(j, linha):
    m = re.match(r"\[( |x|X)\] (\w+)\s*(?:\|\s*(.*))?$", linha)
    if not m or m.group(2) not in MISSOES:
        return
    resto = (m.group(3) or "").strip()
    if m.group(1).lower() == "x":
        j.missoes_feitas[m.group(2)] = int(_kv(resto).get("escolha", 0))
    else:
        j.missoes_ativas[m.group(2)] = int(resto.split("/")[0]) if resto else 0

# ---------- Combate ----------
def combate(jogador, nome, vida_inimigo, atq_inimigo):
    """Combate por turnos: uma tecla por turno, o resultado do turno anterior fica na tela.
    Bônus de Escudo/Impulso/Defender valem só no turno — nada fica permanente."""
    import contextlib, io
    j = jogador
    v_inim = vida_inimigo
    luta = nova_luta(j)
    elemento = ELEMENTO_ANDAR.get(j.andar)
    ultimo = [f"{nome} aparece. {DIM}(elemento do andar: {elemento}){RESET}"]
    while v_inim > 0 and j.vida > 0:
        j.aplicar_passivas()
        j.mana = min(j.mana_max, j.mana + 1 + j.atributos["inteligencia"] // 5)
        bonus_def = FEITICOS["Escudo Arcano"]["def_bonus"] if j.escudo_ativo > 0 else 0
        bonus_atq = FEITICOS["Impulso"]["atq_bonus"] if j.impulso_ativo > 0 else 0
        limpar()
        print(secao(f"COMBATE · {nome} · Andar {j.andar}", RD, grossa=True))
        print(f" {'Você':<16} {barra(j.vida, j.vida_max, 20, GN)} {fmt_num(max(0, j.vida))}/{fmt_num(j.vida_max)}"
              f"  Mana {fmt_num(j.mana)}/{fmt_num(j.mana_max)}  Poções {j.inven.get('Poção de Vida', 0)}")
        print(f" {nome[:16]:<16} {barra(v_inim, vida_inimigo, 20, RD)} {fmt_num(max(0, v_inim))}/{fmt_num(vida_inimigo)}")
        efeitos = ([f"{CY}Escudo{RESET}"] if bonus_def else []) + ([f"{YW}Impulso{RESET}"] if bonus_atq else [])
        if luta["buff_dano"][1]: efeitos.append(f"{YW}+dano{RESET}")
        if luta["reduz"][1]: efeitos.append(f"{CY}proteção{RESET}")
        if efeitos:
            print(f" Ativo: {' · '.join(efeitos)}")
        print(secao("Último turno"))
        for l in ultimo[-6:]:
            print(cortar(f" {l}"))
        print(secao())
        print(" [A] Atacar  [D] Defender  [C] Poção  [M] Magia" + ("  [H] Habilidade" if luta["ativas"] else "") + "  [F] Fugir")
        acao = ler_tecla(" Ação: ")
        ultimo = []
        if acao == "F":
            print(" Você foge!")
            j.escudo_ativo = j.impulso_ativo = 0
            pausa()
            return False
        rec = 0
        if acao == "H" and luta["ativas"]:
            for i, aid in enumerate(luta["ativas"], 1):
                cd = luta["cd"].get(aid, 0)
                print(f"  [{i}] {ATIVAS[aid]['nome']} (mana {ATIVAS[aid]['mana']})" + (f" {DIM}recarga {cd}{RESET}" if cd else ""))
            esc = ler_tecla(" Habilidade: ")
            if not (esc.isdigit() and 1 <= int(esc) <= len(luta["ativas"])):
                ultimo = ["Nenhuma habilidade escolhida."]; continue
            aid = luta["ativas"][int(esc) - 1]
            if luta["cd"].get(aid, 0) or j.mana < ATIVAS[aid]["mana"]:
                ultimo = [f"{ATIVAS[aid]['nome']} ainda não está pronta (recarga ou mana)."]; continue
            dano = int(usar_ativa(j, luta, aid, elemento) * luta["mult_dano"])
            v_inim -= dano
            ultimo.append(f"🌿 {ATIVAS[aid]['nome']}" + (f": {dano} de dano!" if dano else " ativada!"))
            rec = max(0, atq_inimigo - (j.def_ + bonus_def))
        elif acao == "M":
            for i, f in enumerate(j.feiticos_aprendidos, 1):
                info = FEITICOS.get(f, {}); print(f"  [{i}] {f} (mana {info.get('custo_mana', '?')})")
            k = ler_tecla(" Feitiço: ")
            nome_f = j.feiticos_aprendidos[int(k) - 1] if k.isdigit() and 1 <= int(k) <= len(j.feiticos_aprendidos) else k
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                lancou = j.usar_magia(nome_f)
            ultimo += [l for l in saida.getvalue().splitlines() if l.strip()]
            if lancou and j.ultimo_dano:
                v_inim -= j.ultimo_dano
            rec = max(0, atq_inimigo - (j.def_ + bonus_def))
        elif acao == "A":
            dano = int(max(3, j.atq + bonus_atq - 2 + random.randint(-2, 2)) * (1 + luta["buff_dano"][0]))
            v_inim -= dano
            rec = max(0, atq_inimigo - (j.def_ + bonus_def))
            ultimo.append(f"⚔️  Você causa {dano}.")
        elif acao == "D":
            rec = max(0, atq_inimigo - (j.def_ + bonus_def + 8))
            ultimo.append("🛡️  Defesa reforçada neste turno.")
        elif acao == "C":
            ultimo.append("🧪 Poção usada." if j.usar_poção() else "Sem poções!")
            rec = max(0, atq_inimigo - (j.def_ + bonus_def))
        else:
            ultimo = [f"{DIM}Tecla sem ação. Use A, D, C, M" + (", H" if luta["ativas"] else "") + f" ou F.{RESET}"]
            continue
        if j.escudo_ativo > 0: j.escudo_ativo -= 1
        if j.impulso_ativo > 0: j.impulso_ativo -= 1
        rec = int(rec * (1 - luta["reduz"][0]))
        fim_turno_luta(j, luta)
        if v_inim <= 0:
            j.ganhar_xp(20 + j.nivel * 3)
            j.ouro += 10 + j.andar * 5
            limpar()
            print(secao(f"VITÓRIA · {nome}", GN, grossa=True))
            for l in ultimo:
                print(cortar(f" {l}"))
            if nome == ANDARES[j.andar]["chefe"]:
                print(" [👑 CHEFE DERROTADO!]")
                linha_loot = loot_vitoria(j, chefe=True)
                for linha in vencer_chefe(j) + [linha_loot]:
                    print(cortar(f" {linha}"))
            else:
                registrar_abate(j, nome)
                linha_loot = loot_vitoria(j, mult_chance=3)   # luta manual: mais chance de loot
                if linha_loot:
                    print(cortar(f" {linha_loot}"))
            for texto, _ in j.avisos:
                print(cortar(f" {texto}"))
            j.avisos.clear()
            j.escudo_ativo = j.impulso_ativo = 0
            pausa(); return True
        if rec:
            j.vida -= rec
            ultimo.append(f"💥 {nome} revida: -{fmt_num(rec)} HP.")
    j.escudo_ativo = j.impulso_ativo = 0
    if j.vida <= 0:
        limpar()
        print(secao("DERROTA", RD, grossa=True))
        for l in ultimo:
            print(cortar(f" {l}"))
        print(" Você acorda no Porto, com metade da vida.")
        j.vida = max(10, j.vida_max // 2)
        pausa()
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
        if jogador.marcas.get("mare_chamada"):
            digitar('Pescador: "Você ouviu ela, não ouviu? Não me conta. Ainda não."')
        elif jogador.marcas.get("abismo_silencio"):
            digitar('Pescador: "Você voltou quieto do Abismo. Eu entendo. Eu também volto quieto do mar."')
        elif jogador.marcas.get("pescador_confiou"):
            digitar('Pescador: "Se encontrar uma guarda com a minha cara, mais bonita, diz que a rede está remendada."')
        else:
            digitar('Pescador: "O mar continua escuro. Suba, andante. É lá que está a resposta."')
        return
    digitar('Pescador: "Se você me ajudar, te darei o caminho."')
    print("[1] Aceitar ajudar\n[2] Perguntar sobre a torre\n[3] Ir embora")
    es = ler_tecla()
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
        if jogador.marcas.get("guardiao_amigo"):
            digitar('Guardião: "O pão dela ainda estava quente. Ela sempre soube a hora em que eu acordo."')
        elif jogador.marcas.get("padeira_traida"):
            digitar('Guardião: "Você cheira a pão. Não o meu, imagino."')
        else:
            digitar('Guardião: "Você de novo. Passe, antes que eu mude de ideia."')
        return
    digitar('Guardião: "Ninguém passa sem ordem do Rei. E o Rei não dá ordens há anos."')
    print("[1] Mostrar o Manuscrito Antigo\n[2] Desafiar o Guardião\n[3] Ir embora")
    es = ler_tecla()
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
    print(secao(f"{cena['titulo']} · Andar {jogador.andar} · Volta {jogador.ciclo}", CY, grossa=True))
    digitar(cena["desc"])
    print(secao())
    for l in menu_opcoes([f"[1] {cena['npc']}", f"[2] Ir para {cena['sala']}", "[3] Modo Idle",
                          "[4] Usar Magia", "[5] Status", "[6] Salvar", "[0] Voltar"], 2):
        print(l)
    es = ler_tecla()
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
        _menu_idle(jogador)
    elif es == "4":
        _menu_magia(jogador)
        pausa()
    elif es == "5":
        mostrar_status(jogador)
    elif es == "6":
        salvar_man(jogador)
        pausa()
    jogador.sala_atual = cena["titulo"].title()

# ---------- Telas: Forja / Altar / Status ----------
def _efeito_forja(chave, nivel):
    f = FORJA[chave]
    return f"+{int(f['por_nivel'] * nivel * 100)}% {f['efeito']}"

def tela_forja(jogador):
    j = jogador
    msg = ""
    while True:
        limpar()
        print(secao("FORJA DO PORTO", YW, grossa=True))
        print(f' {DIM}"Ouro primeiro, conversa depois."{RESET}   Ouro: {YW}{BOLD}{fmt_num(j.ouro)}{RESET}')
        print(secao("Melhorias"))
        chaves = [k for k in FORJA if k != "botas" or desbloqueado(j, "botas") or j.forja.get("botas")]
        for i, k in enumerate(chaves, 1):
            f, nv = FORJA[k], j.forja.get(k, 0)
            if forja_no_maximo(j, k):
                preco = f"{GN}máximo{RESET}"
            else:
                custo = custo_forja(j, k)
                preco = f"{(GN if j.ouro >= custo else DIM)}{fmt_num(custo)} ouro{RESET}"
            print(cortar(f" [{i}] {f['nome']:<19} nv {nv:<3} {_efeito_forja(k, nv):<17} → {preco}"))
        tralhas = sum(max(0, qt - LIMITE_ITEM.get(item, qt)) * PRECO_ITEM.get(item, 0) * j.andar for item, qt in j.inven.items())
        print(secao())
        for l in menu_opcoes(["[M] Comprar o máximo", f"[V] Vender (~{fmt_num(tralhas)})",
                              f"[T] Auto: {'ligada' if j.auto_compra else 'desligada'}", "[0] Voltar"], 2):
            print(l)
        if msg:
            print(cortar(f" {CY}{msg}{RESET}"))
        es = ler_tecla()
        msg = ""
        if es in ("0", ""):
            return
        if es == "M":
            n = 0
            while auto_comprar(j):
                n += 1
            msg = f"{n} melhoria(s) compradas." if n else "Ouro insuficiente para qualquer melhoria."
        elif es == "V":
            msg = f"Vendido por {fmt_num(vender_excesso(j))} ouro."
        elif es == "T":
            j.auto_compra = not j.auto_compra
            msg = "Auto-compra " + ("ligada: o idle gasta o ouro sozinho." if j.auto_compra else "desligada: você escolhe as compras.")
        elif es.isdigit() and 1 <= int(es) <= len(chaves):
            k = chaves[int(es) - 1]
            pago = comprar_forja(j, k)
            msg = f"{FORJA[k]['nome']} agora no nível {j.forja[k]} (-{fmt_num(pago)} ouro)." if pago else "Não dá: ouro insuficiente ou nível máximo."

def tela_altar(jogador):
    j = jogador
    msg = ""
    while True:
        limpar()
        print(secao("ALTAR DOS FRAGMENTOS", MG, grossa=True))
        print(f" {DIM}Chefes deixam fragmentos; o que se compra aqui é para sempre.{RESET}   {MG}{BOLD}✦ {j.fragmentos}{RESET}")
        print(secao("Bênçãos"))
        chaves = list(ALTAR)
        for i, k in enumerate(chaves, 1):
            a, nv = ALTAR[k], j.altar.get(k, 0)
            if nv >= a.get("max", 10**9):
                preco = f"{GN}máx{RESET}"
            else:
                c = custo_altar(j, k)
                preco = f"{(GN if j.fragmentos >= c else DIM)}{c} ✦{RESET}"
            print(cortar(f" [{i}] {a['nome']:<16} nv {nv:<2} {preco}  {DIM}{a['desc']}{RESET}"))
        print(secao())
        print(" [0] Voltar")
        if msg:
            print(f" {CY}{msg}{RESET}")
        es = ler_tecla()
        msg = ""
        if es in ("0", ""):
            return
        if es.isdigit() and 1 <= int(es) <= len(chaves):
            k = chaves[int(es) - 1]
            pago = comprar_altar(j, k)
            msg = f"{ALTAR[k]['nome']} agora no nível {j.altar[k]}." if pago else "Fragmentos insuficientes (ou nível máximo)."

def mostrar_status(jogador):
    j = jogador
    a = j.atributos
    t = TITULOS_DEF[j.titulo_ativo]
    linhas = [
        f" {BOLD}{j.nome}{RESET} · {j.classe}{linha_classe_extra(j)} · Volta {j.ciclo} · Andar {j.andar} · Nível {j.nivel}",
        f" Vida {fmt_num(j.vida)}/{fmt_num(j.vida_max)} · Mana {fmt_num(j.mana)}/{fmt_num(j.mana_max)}"
        f" · ATQ {fmt_num(j.atq)} · DEF {fmt_num(j.def_)}",
        f" Atributos: F={a['forca']} D={a['destreza']} I={a['inteligencia']} V={a['vitalidade']} C={a['carisma']}"
        + (f"  {YW}({j.pontos_atributo} livres){RESET}" if j.pontos_atributo else ""),
        f" Título: {CY}{j.titulo_ativo}{RESET} (+{t['bonus_atq']} ATQ / +{t['bonus_def']} DEF) · Pontos de Lenda {pontos_lenda(j)}",
        f" Bônus: ouro ×{j.mult_ouro():.2f} · XP ×{j.mult_xp():.2f}".replace(".", ","),
    ]
    linhas += quebrar(f"Passivas: {', '.join(j.passivas) or 'nenhuma'}")
    linhas += [secao("Forja e Altar"), f" {_resumo_forja(j)}"]
    linhas += quebrar(" · ".join(f"{ALTAR[k]['nome']} {v}" for k, v in j.altar.items()) + f" · ✦ {j.fragmentos}")
    linhas.append(secao("Torre"))
    for i in range(5, 0, -1):
        info = ANDARES[i]
        marca, cor = ("✔", GN) if j.andar > i else ("▶", YW + BOLD) if j.andar == i else ("·", DIM)
        linhas.append(f"  {cor}{marca} Andar {i} · {info['nome']:<18} {info['chefe']}{RESET}")
    linhas.append(secao("Inventário"))
    linhas += quebrar(" · ".join(f"{k} ×{v}" for k, v in j.inven.items()) or "vazio")
    feitas = [c for c, v in j.conquistas.items() if v]
    linhas.append(secao(f"Conquistas {len(feitas)}/{len(CONQUISTAS_DEF)}"))
    for c, d in CONQUISTAS_DEF.items():
        linhas.append(f" {GN + '🏆' if j.conquistas.get(c) else DIM + '· '}{RESET} {c} {DIM}— {d['desc']}{RESET}")
    paginar("STATUS", linhas)

def cena_chefe(jogador):
    info = ANDARES[jogador.andar]
    limpar()
    print(secao(f"CHEFE DO ANDAR {jogador.andar}", RD, grossa=True))
    vida_c, atq_c = stats_chefe(jogador)
    print(f" {info['chefe']} · {fmt_num(vida_c)} HP · ATQ {fmt_num(atq_c)} · seu Poder {_cor_poder(poder_contra(jogador, vida_c, atq_c))}")
    flag = info.get("req_flag")
    print(f" Precisa: Nível {nivel_requerido(jogador)}" + (f" · {FLAG_TEXTO.get(flag, flag)}" if flag else ""))
    if nivel_efetivo(jogador) < nivel_requerido(jogador):
        print(f" {YW}Você ainda não tem nível suficiente — o modo idle treina você.{RESET}")
        pausa(); return
    if flag and not jogador.flags.get(flag):
        print(f" {YW}Ainda falta: {FLAG_TEXTO.get(flag, flag)} (explore o andar [1]).{RESET}")
        pausa(); return
    print(" [1] Combater o chefe   [0] Voltar")
    if ler_tecla() == "1":
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
        f"Fragmentos: {jogador.fragmentos}",
        f"Forja: {' '.join(f'{k}={v}' for k, v in jogador.forja.items())}",
        f"Altar: {' '.join(f'{k}={v}' for k, v in jogador.altar.items())}",
        f"AutoCompra: {'sim' if jogador.auto_compra else 'nao'}",
        f"UltimoAcesso: {int(time.time())}",
    ]
    for salvar, _ in CHAVES_SAVE:
        linhas += [f"{k}: {v}" for k, v in salvar(jogador)]
    linhas += [
        "",
        "## Flags",
    ] + [f"- [{'x' if v else ' '}] {k}" for k, v in jogador.flags.items()] + [
        "",
        "## Inventário",
    ] + [f"- {item}: {qt}" for item, qt in jogador.inven.items()]
    for titulo, salvar, _ in BLOCOS_SAVE:
        linhas += ["", f"## {titulo}"] + salvar(jogador)
    return "\n".join(linhas) + "\n"

def _sem_acento(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c)).lower().strip()

def _kv(texto):
    """'a=1 b=2' -> {'a': '1', 'b': '2'}"""
    return dict(p.partition("=")[::2] for p in texto.split() if "=" in p)



def gravar_save(jogador, caminho, titulo):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto_save(jogador, titulo))

def ler_save(jogador, caminho):
    """Aplica o save no jogador. Retorna o timestamp UltimoAcesso (ou None)."""
    atalhos = {"F": "forca", "D": "destreza", "I": "inteligencia", "V": "vitalidade", "C": "carisma"}
    inteiro = lambda s: int(float(s.split("/")[0].strip()))
    ultimo = None
    inven = {}
    tem_fragmentos = False
    tem_stats = False
    jogador._estado_v3()
    blocos = {_sem_acento(t): carregar for t, _, carregar in BLOCOS_SAVE}
    secao_atual = None
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("## "):
                secao_atual = _sem_acento(linha[3:])
                continue
            if secao_atual in blocos and linha.startswith("- "):
                try:
                    blocos[secao_atual](jogador, linha[2:].strip())
                    tem_stats = tem_stats or secao_atual == "recordes"
                except (ValueError, KeyError, IndexError):
                    pass  # linha estragada na edição manual: ignora
                continue
            m = re.match(r"- \[( |x|X)\] (\w+)$", linha)
            if m and secao_atual in (None, "flags"):
                jogador.flags[m.group(2)] = m.group(1).lower() == "x"
                continue
            m = re.match(r"- (.+):\s*(\d+)$", linha)
            if m and secao_atual in (None, "inventario"):
                inven[m.group(1).strip()] = int(m.group(2))
                continue
            if ":" not in linha or linha.startswith("#") or linha.startswith("- "):
                continue
            chave, valor = [p.strip() for p in linha.split(":", 1)]
            try:
                if any(carregar(jogador, chave, valor) for _, carregar in CHAVES_SAVE):
                    continue
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
                elif chave == "Fragmentos": jogador.fragmentos = inteiro(valor); tem_fragmentos = True
                elif chave in ("Forja", "Altar"):
                    destino = jogador.forja if chave == "Forja" else jogador.altar
                    for par in valor.split():
                        k, _, v = par.partition("=")
                        if k in destino and v.isdigit():
                            destino[k] = int(v)
                elif chave == "AutoCompra": jogador.auto_compra = valor.lower() not in ("nao", "não", "n", "0", "off")
                elif chave == "UltimoAcesso": ultimo = inteiro(valor)
            except ValueError:
                pass  # valor estragado na edição manual: mantém o padrão
    if inven:
        jogador.inven = inven
    if not tem_fragmentos:
        # Save antigo (antes do Altar): devolve os fragmentos dos chefes já vencidos
        por_volta = FRAGMENTOS_CHEFE * 4 + FRAGMENTOS_REI
        jogador.fragmentos = (jogador.ciclo - 1) * por_volta + (jogador.andar - 1) * FRAGMENTOS_CHEFE
    if not tem_stats:
        # Save anterior à v3: estima os chefes já vencidos (para os desbloqueios)
        jogador.stats["chefe"] = (jogador.ciclo - 1) * 5 + jogador.andar - 1
    jogador.xp_max = xp_maestria(jogador) if jogador.nivel >= NIVEL_MAX else xp_para_nivel(jogador.nivel)
    jogador._recalcular()
    jogador._desbloquear_passivas(silencioso=True)
    jogador.aplicar_flags_de_progresso()
    atualizar_desbloqueios(jogador, silencioso=True)
    jogador._recalcular()
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

# ---------- v3 · registro do save por sistema ----------
def _letra_rank(letra):
    return [r["letra"] for r in RANKS].index(letra.strip().upper()[:1])

def _salvar_equip(j):
    linhas = []
    for slot in SLOTS:
        it = j.equip.get(slot)
        if not it:
            continue
        af = " ".join(f"{k}={v}" for k, v in it["afixos"].items()) or "-"
        meta = f"ilvl={it['ilvl']} abates={it.get('abates', 0)}"
        if it.get("conjunto"): meta += f" conjunto={it['conjunto']}"
        if it.get("efeito"): meta += f" efeito={it['efeito'][0]}:{it['efeito'][1]}"
        linhas.append(f"- {slot}: {it['nome']} | {RANKS[it['rank']]['letra']} | {it['main']} | {af} | {meta}"
                      + (f" | {it['origem']}" if it.get("origem") else ""))
    return linhas

def _ler_equip(j, linha):
    slot, _, resto = linha.partition(":")
    slot = slot.strip()
    partes = [p.strip() for p in resto.split("|")]
    if slot not in SLOTS or len(partes) < 5:
        return
    nome, letra, main, af, meta = partes[:5]
    meta = _kv(meta)
    efeito = None
    if "efeito" in meta:
        k, _, v = meta["efeito"].partition(":")
        efeito = (k, int(v))
    j.equip[slot] = {"slot": slot, "nome": nome, "rank": _letra_rank(letra), "ilvl": int(meta.get("ilvl", j.nivel)),
                     "main": int(main), "afixos": {k: int(v) for k, v in _kv(af).items() if k in AFIXOS},
                     "efeito": efeito, "conjunto": meta.get("conjunto") if meta.get("conjunto") in CONJUNTOS else None,
                     "abates": int(meta.get("abates", 0)), "origem": " | ".join(partes[5:])}

def _rec_txt(r):
    return " ".join(f"{k}={BAUS[v]['curto'] if k == 'bau' else v}" for k, v in r.items()) or "-"

def _rec_ler(texto):
    r = {}
    for k, v in _kv(texto).items():
        r[k] = BAU_CURTO.get(v, v) if k == "bau" else int(v)
    return r

def _salvar_contratos(j):
    return [f"- [{'x' if c['feito'] else ' '}] {c['texto']} | {c['tipo']} | {c['prog']}/{c['qt']} | "
            f"{' '.join(f'{k}={v}' for k, v in c['filtro'].items()) or '-'} | {_rec_txt(c['recompensa'])}" for c in j.contratos]

def _ler_contrato(j, linha):
    m = re.match(r"\[( |x|X)\] (.*)$", linha)
    partes = [p.strip() for p in m.group(2).split("|")]
    prog, _, qt = partes[2].partition("/")
    j.contratos.append({"texto": partes[0], "tipo": partes[1], "prog": int(prog), "qt": int(qt),
                        "filtro": {k: int(v) for k, v in _kv(partes[3]).items()}, "recompensa": _rec_ler(partes[4]),
                        "feito": m.group(1).lower() == "x"})

def _ler_marcado(destino):
    """Carregador de listas '- [x] nome' (desbloqueios e marcas)."""
    def carregar(j, linha):
        m = re.match(r"\[( |x|X)\] (\w+)$", linha)
        if not m:
            return
        if destino == "revelados":
            if m.group(1).lower() == "x" and m.group(2) in DESBLOQUEIOS and m.group(2) not in j.revelados:
                j.revelados.append(m.group(2))
        else:
            getattr(j, destino)[m.group(2)] = m.group(1).lower() == "x"
    return carregar

def _ler_numero(destino):
    def carregar(j, linha):
        nome, _, v = linha.rpartition(":")
        getattr(j, destino)[nome.strip()] = int(v)
    return carregar

BLOCOS_SAVE += [
    ("Desbloqueios", lambda j: [f"- [{'x' if k in j.revelados else ' '}] {k}" for k in DESBLOQUEIOS], _ler_marcado("revelados")),
    ("Marcas", lambda j: [f"- [{'x' if v else ' '}] {k}" for k, v in j.marcas.items()], _ler_marcado("marcas")),
    ("Equipamento", _salvar_equip, _ler_equip),
    ("Contratos", _salvar_contratos, _ler_contrato),
    ("Recordes", lambda j: [f"- {k}: {int(v)}" for k, v in j.stats.items()], _ler_numero("stats")),
    ("Bestiário", lambda j: [f"- {k}: {v}" for k, v in j.bestiario.items()], _ler_numero("bestiario")),
    ("Diário", lambda j: [f"- {t}" for t in j.diario], lambda j, linha: j.diario.append(linha)),
]

def _chaves_int(mapa):
    """Chaves soltas inteiras: {'Chave': 'atributo'}."""
    def salvar(j):
        return [(k, int(getattr(j, a))) for k, a in mapa.items()]
    def carregar(j, chave, valor):
        if chave in mapa:
            setattr(j, mapa[chave], int(float(valor)))
            return True
        return False
    return salvar, carregar

BLOCOS_SAVE.append(("Habilidades", _salvar_habilidades, _ler_habilidade))
BLOCOS_SAVE.append(("Companheiros", _salvar_companheiros, _ler_companheiro))
BLOCOS_SAVE.append(("Missões", _salvar_missoes, _ler_missao))
CHAVES_SAVE.append(_chaves_int({"Piedade4": "piedade4", "Piedade5": "piedade5"}))

def _salvar_chaves_fase3(j):
    return [("AutoGrupo", "sim" if j.auto_grupo else "nao"), ("EscolhaPendente", j.escolha_pendente)]

def _ler_chaves_fase3(j, chave, valor):
    if chave == "AutoGrupo":
        j.auto_grupo = valor.lower() not in ("nao", "não", "n", "0", "off")
    elif chave == "EscolhaPendente":
        j.escolha_pendente = valor if valor in MISSOES else ""
        j.escolha_prazo = time.time() + ESPERA_ESCOLHA
    else:
        return False
    return True
CHAVES_SAVE.append((_salvar_chaves_fase3, _ler_chaves_fase3))

def _salvar_chaves_fase2(j):
    return [("Subclasse", j.subclasse), ("Rotacao", " > ".join(ATIVAS[a]["nome"] for a in j.rotacao if a in ATIVAS)),
            ("AutoHabilidades", "sim" if j.auto_hab else "nao"),
            ("Maestria", " ".join(f"{k}={v}" for k, v in j.maestria.items())), ("MaestriaFoco", j.maestria_foco)]

def _ler_chaves_fase2(j, chave, valor):
    if chave == "Subclasse":
        j.subclasse = valor if any(s["nome"] == valor for s in SUBCLASSES.get(j.classe, [])) else ""
    elif chave == "Rotacao":
        por_nome = {a["nome"]: k for k, a in ATIVAS.items()}
        j.rotacao = [por_nome[n.strip()] for n in valor.split(">") if n.strip() in por_nome]
    elif chave == "AutoHabilidades":
        j.auto_hab = valor.lower() not in ("nao", "não", "n", "0", "off")
    elif chave == "Maestria":
        for k, v in _kv(valor).items():
            if k in j.maestria: j.maestria[k] = int(v)
    elif chave == "MaestriaFoco":
        j.maestria_foco = valor if valor in ("atq", "def", "vida") else "atq"
    else:
        return False
    return True

CHAVES_SAVE.append((_salvar_chaves_fase2, _ler_chaves_fase2))
CHAVES_SAVE.append(_chaves_int({"ResetVolta": "reset_volta", "PontosHabExtra": "pontos_hab_extra"}))
CHAVES_SAVE.append(_chaves_int({"Conchas": "conchas", "PoForja": "po_forja", "PiedadeLoot": "piedade_loot",
                                "ContratosRenovam": "contratos_renovam", "PresenteUltimo": "presente_ultimo",
                                "PresenteSequencia": "presente_seq"}))

def mostrar_offline(jogador, ultimo):
    """Aplica e mostra o progresso offline num quadro. Retorna True se houve algo."""
    if not ultimo:
        return False
    r = progresso_offline(jogador, time.time() - ultimo)
    if not r:
        return False
    m = r["minutos"]
    print(secao("⏳ ENQUANTO VOCÊ ESTAVA FORA", YW, grossa=True))
    print(f" O andante seguiu sozinho por {BOLD}{m // 60}h{m % 60:02d}min{RESET}"
          f" {DIM}(rendimento {int(r['eficiencia'] * 100)}% · limite {limite_offline_min(jogador) // 60}h){RESET}")
    print(f"   {YW}+{fmt_num(r['xp'])} XP{RESET}" + (f"  →  {GN}{BOLD}+{r['niveis']} nível(is){RESET} (agora {jogador.nivel})" if r["niveis"] else ""))
    print(f"   {YW}+{fmt_num(r['ouro'])} ouro{RESET}" + (f"  →  {r['compras']} melhoria(s) na Forja" if r["compras"] else ""))
    if r.get("baus"):
        print(f"   {YW}+{r['baus']} Baú(s) de Bronze{RESET} {DIM}esperando no menu [B]{RESET}")
    for linha in r.get("extras", []):
        print(f"   {linha}")
    if r["limitado"]:
        print(f"   {DIM}Você ficou fora mais que o limite. O Altar (Eco do Andante) aumenta isso.{RESET}")
    if requisitos_ok(jogador):
        print(f"   {CY}O chefe {ANDARES[jogador.andar]['chefe']} já pode ser enfrentado — o idle cuida disso.{RESET}")
    print(secao())
    return True

# ---------- v3 · Telas: equipamento, baús, contratos, diário, recordes ----------
def _tempo_txt(segundos):
    segundos = max(0, int(segundos))
    if segundos >= 3600:
        return f"{segundos // 3600}h{segundos % 3600 // 60:02d}"
    return f"{segundos // 60}min{segundos % 60:02d}s" if segundos >= 60 else f"{segundos}s"

def conjuntos_ativos(j):
    linhas = []
    for c, d in CONJUNTOS.items():
        n = sum(1 for it in j.equip.values() if it.get("conjunto") == c)
        if n:
            ativos = [", ".join(EFEITO_NOME.get(k, k).format(v=v) for k, v in d[p].items()) for p in (2, 4) if n >= p]
            linhas.append(f"{d['nome']} ({n}/4)" + (f": {'; '.join(ativos)}" if ativos else ""))
    return linhas

def tela_equipamento(j):
    msg = ""
    slots = list(SLOTS)
    while True:
        limpar()
        print(secao("EQUIPAMENTO", CY, grossa=True))
        print(f" {DIM}O idle equipa o melhor sozinho.{RESET}  Pó de forja {YW}{BOLD}{j.po_forja}{RESET}"
              f"  {DIM}Épico garantido em {PIEDADE_LOOT - j.piedade_loot}{RESET}")
        for i, slot in enumerate(slots, 1):
            it = j.equip.get(slot)
            if not it:
                print(f" [{i}] {SLOTS[slot]['nome']:<9} {DIM}vazio{RESET}")
                continue
            print(cortar(f" [{i}] {SLOTS[slot]['nome']:<9} {fmt_item(it)}"))
            print(cortar(f"     {DIM}{fmt_detalhes(it)}{RESET}"))
        for l in conjuntos_ativos(j):
            print(cortar(f" ⟡ {l}"))
        print(secao())
        print(f" [1-{len(slots)}] ver / melhorar um item   [0] Voltar")
        if msg:
            print(cortar(f" {CY}{msg}{RESET}"))
        es = ler_tecla()
        msg = ""
        if es in ("0", ""):
            return
        if es.isdigit() and 1 <= int(es) <= len(slots) and j.equip.get(slots[int(es) - 1]):
            msg = _tela_item(j, slots[int(es) - 1])

def _tela_item(j, slot):
    it = j.equip[slot]
    limpar()
    print(secao(SLOTS[slot]["nome"].upper(), CY, grossa=True))
    print(cortar(f" {fmt_item(it)}"))
    for l in quebrar(fmt_detalhes(it), "   "):
        print(l)
    if it.get("origem"):
        for l in quebrar(f'"{it["origem"]}"', "   "):
            print(f"{DIM}{l}{RESET}")
    print(secao())
    print(f" [R] Rerrolar afixos ({custo_rerrolar(it)} pó)   [U] Atualizar ao nível {j.nivel} ({custo_atualizar(it)} pó)   [0] Voltar")
    print(f" {DIM}Você tem {j.po_forja} pó.{RESET}")
    acao = ler_tecla()
    if acao == "R":
        return f"Afixos novos: {fmt_detalhes(it)}" if rerrolar_afixos(j, slot) else "Pó insuficiente (ou item sem afixos)."
    if acao == "U":
        return f"Agora ilvl {it['ilvl']}: {fmt_detalhes(it)}" if atualizar_item(j, slot) else "Pó insuficiente (ou já está no seu nível)."
    return ""

def animar_rank(rank, delay=0.22):
    """Suspense do baú: o rank 'sobe' letra por letra até parar."""
    for i in range(rank + 1):
        r = RANKS[i]
        sys.stdout.write(f"\r   {r['cor']}{BOLD}[{r['letra']}] {r['nome']:<10}{RESET}   ")
        sys.stdout.flush()
        time.sleep(delay if i < rank else delay * 2)
    sys.stdout.write("\n")

def tela_baus(j):
    msg = []
    while True:
        limpar()
        print(secao("BAÚS", YW, grossa=True))
        print(cortar(f" {DIM}Chefes, contratos, marcos e presentes dão baús. Acima de {BAU_LIMITE}, abrem sozinhos.{RESET}"))
        nomes = [n for n in BAUS if j.inven.get(n, 0)]
        for i, n in enumerate(nomes, 1):
            b = BAUS[n]
            print(f" [{i}] {n:<14} ×{j.inven[n]:<3} {DIM}{b['itens']} item(ns), mín. {RANKS[b['minimo']]['nome']}{RESET}")
        if not nomes:
            print(f" {DIM}Nenhum baú. O idle traz mais.{RESET}")
        print(secao())
        print(" [n] abrir um (com suspense)   [T] abrir todos   [0] Voltar")
        for l in msg[-(altura_tela() - 10):]:
            print(cortar(" " + l))
        es = ler_tecla()
        msg = []
        if es in ("0", ""):
            return
        if es == "T":
            for n in nomes:
                while j.inven.get(n, 0):
                    _, linhas = abrir_bau(j, n)
                    msg += [l for l in linhas if any(r in visivel(l) for r in ("Épico", "Lendário", "Mítico"))]
            msg = msg or ["Tudo aberto. Nada Épico ou melhor desta vez."]
        elif es.isdigit() and 1 <= int(es) <= len(nomes):
            n = nomes[int(es) - 1]
            itens, linhas = abrir_bau(j, n)
            limpar()
            print(secao(n.upper(), YW, grossa=True))
            for it, linha in zip(itens, linhas):
                animar_rank(it["rank"])
                print(cortar(f"   {linha}"))
            print(cortar(f"   {linhas[-1]}"))
            pausa()

def tela_contratos(j):
    renovar_contratos(j)
    linhas = [f" {DIM}O idle cumpre sozinho. Os cumpridos são trocados em {_tempo_txt(j.contratos_renovam - time.time())}.{RESET}"]
    for c in j.contratos:
        marca = f"{GN}✔{RESET}" if c["feito"] else f"{YW}▸{RESET}"
        linhas.append(f" {marca} {c['texto']}")
        linhas.append(f"   {barra(c['prog'], c['qt'], 16, GN if c['feito'] else CY)} {fmt_num(c['prog'])}/{fmt_num(c['qt'])}"
                      f"  {DIM}→ {_rec_desc(c['recompensa'])}{RESET}")
    linhas.append(secao(f"Missões · cumpridas {len(j.missoes_feitas)}/{len(MISSOES)}"))
    if not j.missoes_ativas:
        linhas.append(f" {DIM}Nenhuma missão ativa. Elas aparecem conforme você sobe.{RESET}")
    for mid, prog in j.missoes_ativas.items():
        m = MISSOES[mid]
        linhas.append(f" {YW}▸{RESET} {BOLD}{m['nome']}{RESET} {DIM}({m['cadeia']}){RESET}")
        linhas.append(f"   {barra(prog, m['obj']['qt'], 16, MG)} {prog}/{m['obj']['qt']}  {m['objetivo']}")
    paginar("CONTRATOS E MISSÕES", linhas)

def _rec_desc(r):
    nomes = {"ouro": "ouro", "conchas": "conchas", "fragmentos": "✦", "po": "pó", "xp": "XP", "pontos_hab": "pt hab."}
    return ", ".join(v if k == "bau" else f"{fmt_num(v)} {nomes.get(k, k)}" for k, v in r.items())


def tela_diario(j):
    linhas = []
    for l in j.diario:
        linhas += quebrar(l, " · ")
    paginar("DIÁRIO DE BORDO", linhas or [f" {DIM}Páginas em branco. Por enquanto.{RESET}"], no_fim=True)

def tela_recordes(j):
    st = j.stats
    vr = st.get("volta_rapida")
    linhas = colunas([f"Maior dano: {fmt_num(st.get('maior_dano', 0))}",
                      f"Volta mais rápida: {_tempo_txt(vr) if vr else '-'}",
                      f"Melhor item: {RANKS[st['maior_rank']]['nome'] if 'maior_rank' in st else '-'}",
                      f"Tempo de idle: {_tempo_txt(st.get('ticks', 0))}",
                      f"Monstros: {fmt_num(st.get('monstro', 0))}", f"Chefes: {fmt_num(st.get('chefe', 0))}",
                      f"Baús abertos: {st.get('bau', 0)}", f"Contratos: {st.get('contrato', 0)}",
                      f"Ouro ganho: {fmt_num(st.get('ouro', 0))}", f"Pontos de Lenda: {pontos_lenda(j)}"])
    linhas = [" " + l for l in linhas]
    linhas.append(secao(f"Bestiário · +1% de dano a cada {BESTIARIO_POR_BONUS} abates"))
    for andar, nomes in MONSTROS.items():
        for nome in nomes:
            n = j.bestiario.get(nome, 0)
            if not n:
                linhas.append(f" {DIM}· ??? (Andar {andar}){RESET}")
                continue
            desc = BESTIARIO.get(nome, "") if n >= 10 else "(vença 10 para saber mais)"
            linhas.append(f" · {nome:<19} ×{fmt_num(n):<6} {GN}+{bonus_bestiario(j, nome)}%{RESET} {DIM}{desc}{RESET}")
    paginar("RECORDES E BESTIÁRIO", linhas)

# ---------- Menu ----------
def criar_personagem():
    print(secao("NOVO ANDANTE", YW, grossa=True))
    nome = input(" Nome do personagem: ").strip() or "Aventurier"
    print(f" {BOLD}[G]{RESET} Guerreiro {DIM}— mais vida, ataque e defesa{RESET}")
    print(f" {BOLD}[M]{RESET} Mago      {DIM}— muita mana e magia, mas frágil{RESET}")
    print(f" {BOLD}[A]{RESET} Arqueiro  {DIM}— equilibrado, começa com ouro{RESET}")
    classe_input = ler_tecla(" Classe (G/M/A): ")
    classe = "Mago" if classe_input == "M" else "Arqueiro" if classe_input == "A" else "Guerreiro"
    idade_str = input(" Idade (número): ").strip()
    j = Jogador(nome, classe, 1)
    j.idade = int(idade_str) if idade_str.isdigit() else 18
    return j

def dica_do_menu(j):
    """Uma sugestão do que fazer agora — a coisa mais útil primeiro."""
    if j.pontos_atributo:
        return f"Você tem {j.pontos_atributo} ponto(s) de atributo para distribuir [5]."
    for dica in DICAS_EXTRA:
        texto = dica(j)
        if texto:
            return texto
    baus = sum(j.inven.get(n, 0) for n in BAUS)
    if baus:
        return f"Você tem {baus} baú(s) esperando para abrir [B]."
    baratos = [custo_altar(j, k) for k in ALTAR if j.altar.get(k, 0) < ALTAR[k].get("max", 10**9)]
    if desbloqueado(j, "altar") and baratos and j.fragmentos >= min(baratos):
        return f"Seus ✦ {j.fragmentos} fragmentos já compram uma bênção no Altar [A]."
    if desbloqueado(j, "forja") and not j.auto_compra and any(j.ouro >= custo_forja(j, k) for k in FORJA if not forja_no_maximo(j, k)):
        return "Tem ouro sobrando: passe na Forja [F]."
    if requisitos_ok(j):
        return f"O chefe {ANDARES[j.andar]['chefe']} está ao seu alcance [2] — ou deixe o idle cuidar disso [3]."
    flag = ANDARES[j.andar].get("req_flag")
    if flag and not j.flags.get(flag):
        return f"Para chegar ao chefe falta: {FLAG_TEXTO.get(flag, flag)} [1]."
    trancados = [k for k, d in DESBLOQUEIOS.items() if d.get("menu") and k not in j.revelados]
    if trancados:
        return f"Deixe o idle rodar [3]. Próximo segredo: {requisito_texto(trancados[0])}."
    return "Deixe o idle rodar [3]: ele luta, compra na Forja e sobe a torre sozinho."


def _menu_magia(j):
    limpar()
    print(secao("MAGIA", MG, grossa=True))
    for i, f in enumerate(j.feiticos_aprendidos, 1):
        info = FEITICOS.get(f, {})
        print(f" [{i}] {f:<16} mana {info.get('custo_mana', '?'):<3} {DIM}{info.get('desc', '')}{RESET}")
    print(f" Mana {fmt_num(j.mana)}/{fmt_num(j.mana_max)}   [0] Voltar")
    k = ler_tecla()
    if k.isdigit() and 1 <= int(k) <= len(j.feiticos_aprendidos):
        j.usar_magia(j.feiticos_aprendidos[int(k) - 1])

def _menu_idle(j):
    res = auto_play(j)
    limpar()
    j.novidades.insert(0, resumo_idle(res))

def _qt_baus(j):
    n = sum(j.inven.get(b, 0) for b in BAUS)
    return f"[B] Baús{f' {YW}{n}{RESET}' if n else ''}"

# tecla -> (desbloqueio necessário ou None, rótulo (texto ou função j), ação(j), pausar depois?)
MENU_OPCOES = {
    "1": (None, "[1] Explorar", lambda j: cena_explorar(j), False),
    "2": (None, "[2] Chefe", lambda j: cena_chefe(j), False),
    "M": ("mapa", "[M] Mapa", lambda j: tela_mapa(j), False),
    "D": ("dungeons", "[D] Dungeons", lambda j: tela_dungeons(j), False),
    "T": ("torres", "[T] Torres", lambda j: tela_torres(j), False),
    "F": ("forja", "[F] Forja", lambda j: tela_forja(j), False),
    "A": ("altar", "[A] Altar", lambda j: tela_altar(j), False),
    "E": ("equipamento", "[E] Equipamento", lambda j: tela_equipamento(j), False),
    "B": ("baus", _qt_baus, lambda j: tela_baus(j), False),
    "H": ("habilidades", lambda j: "[H] Habilidades" + (f" {YW}{pontos_hab_livres(j)}{RESET}" if pontos_hab_livres(j) else ""),
          lambda j: tela_habilidades(j), False),
    "G": ("grupo", "[G] Grupo", lambda j: tela_grupo(j), False),
    "S": ("gacha", lambda j: f"[S] Sino {CY}◎{j.conchas}{RESET}", lambda j: tela_sino(j), False),
    "5": (None, lambda j: "[5] Pontos" + (f" {YW}{j.pontos_atributo}{RESET}" if j.pontos_atributo else ""),
          lambda j: j.distribuir_pontos(), False),
    "4": (None, "[4] Magia", lambda j: (_menu_magia(j), pausa()), False),
    "C": ("contratos", "[C] Missões", lambda j: tela_contratos(j), False),
    "J": ("diario", "[J] Diário", lambda j: tela_diario(j), False),
    "P": ("passe", "[P] Passe", lambda j: tela_passe(j), False),
    "R": ("recordes", "[R] Recordes", lambda j: tela_recordes(j), False),
    "6": (None, "[6] Status", lambda j: mostrar_status(j), False),
    "7": (None, "[7] Salvar", lambda j: (salvar_man(j), pausa()), False),
    "8": (None, "[8] Carregar", lambda j: (carregar_man(j), pausa()), False),
}
MENU_SECOES = [("Jogar", ["1", "2", "M", "D", "T"]),
               ("Personagem", ["F", "A", "E", "B", "H", "G", "S", "5", "4"]),
               ("Progresso", ["C", "J", "P", "R", "6", "7", "8"])]

def _rotulo_menu(j, tecla):
    rotulo = MENU_OPCOES[tecla][1]
    return rotulo(j) if callable(rotulo) else rotulo

def tela_menu(j):
    info = ANDARES[j.andar]
    vida_c, atq_c = stats_chefe(j)
    req = nivel_requerido(j)
    flag = info.get("req_flag")
    ok = lambda b: f"{GN}✔{RESET}" if b else f"{RD}✘{RESET}"
    cond = f"Nv {req} {ok(nivel_efetivo(j) >= req)}" + (f" · falta {FLAG_TEXTO.get(flag, flag)}" if flag and not j.flags.get(flag) else "")
    linhas = [
        secao(f"ANDANTE · {j.nome} · {j.classe}{linha_classe_extra(j)} · Nv {j.nivel}", YW, grossa=True),
        f" Vida {barra(j.vida, j.vida_max, 14, GN)} {fmt_num(j.vida)}/{fmt_num(j.vida_max)}"
        f"  Mana {barra(j.mana, j.mana_max, 8, MG)} {fmt_num(j.mana)}   {CY}{j.titulo_ativo}{RESET}",
        f" XP   {barra(j.xp, j.xp_max, 14, YW)} {fmt_num(j.xp)}/{fmt_num(j.xp_max)}"
        f"  Ouro {YW}{BOLD}{fmt_num(j.ouro)}{RESET}  {MG}✦ {j.fragmentos}{RESET}  {CY}◎ {j.conchas}{RESET}",
        f" Volta {j.ciclo} {_linha_torre(j)}  {CY}{info['nome']}{RESET}",
        f" Chefe {BOLD}{info['chefe']}{RESET} · {cond} · Poder {_cor_poder(poder_contra(j, vida_c, atq_c))}",
    ]
    trancados = []
    for titulo, teclas in MENU_SECOES:
        rotulos = []
        for t in teclas:
            req_d = MENU_OPCOES[t][0]
            if req_d and not desbloqueado(j, req_d):
                trancados.append(f"{DESBLOQUEIOS[req_d]['nome']} ({requisito_texto(req_d)})")
                continue
            rotulos.append(_rotulo_menu(j, t))
        if titulo == "Jogar":
            linhas += [secao("Jogar"), f"  {GN}{BOLD}[ENTER] ▶ MODO IDLE{RESET} {DIM}luta, compra e sobe sozinho{RESET}"]
        else:
            linhas.append(secao(titulo))
        if titulo == MENU_SECOES[-1][0]:
            rotulos.append("[9] Sair")
        linhas += menu_opcoes(rotulos)
    if trancados:
        linhas.append(f" {DIM}Em breve: {' · '.join(trancados[:3])}{RESET}")
    rodape = [secao(grossa=True, cor=YW), f" {YW}💡{RESET} {dica_do_menu(j)}"]
    sobra = altura_tela() - 2 - len(linhas) - len(rodape)
    if j.novidades and sobra >= 2:
        linhas.append(secao("Novidades"))
        linhas += [f" {n.strip()}" for n in j.novidades[:sobra - 1]]
    for l in linhas + rodape:
        print(cortar(l))

def linha_classe_extra(j):
    sub = getattr(j, "subclasse", "")
    return f" ({sub})" if sub else ""

def resumo_idle(res):
    minutos = max(1 / 60, (time.time() - res["inicio"]) / 60)
    return (f"⏸️  Idle: {int(minutos)}min · {res['batalhas']} batalhas · {res['chefes']} chefe(s) · "
            f"+{fmt_num(res['xp_ganho'])} XP · +{fmt_num(res['ouro_ganho'])} ouro")

def coletar_novidades(j):
    """Conquistas, desbloqueios e avisos novos viram a lista 'Novidades' do menu (sem pausar o jogo)."""
    atualizar_desbloqueios(j)
    renovar_contratos(j)
    atualizar_missoes(j)
    novas = checar_conquistas(j) + [t for t, _ in j.avisos]
    j.avisos.clear()
    j.novidades = (novas[::-1] + j.novidades)[:12]

def menu(iniciar_idle=False):
    limpar()
    print(logo_ascii())
    print()
    j = None
    # Jogo idle: se já existe progresso, continua direto
    if os.path.exists(SAVE_AUTO):
        try:
            j = Jogador("Temp", "Guerreiro", 1)
            ultimo = ler_save(j, SAVE_AUTO)
            print(f" Save encontrado: {BOLD}{j.nome}{RESET} · {j.classe} · Volta {j.ciclo} · Andar {j.andar} · Nível {j.nivel}")
            resp = ler_tecla(f" Continuar? {BOLD}[ENTER]{RESET} sim  {DIM}[N] novo personagem (substitui o auto save){RESET} ")
            if resp == "N":
                j = None
            elif mostrar_offline(j, ultimo):
                pausa()
        except Exception as e:
            print(f" {RD}[⚠️ AUTO SAVE ILEGÍVEL]{RESET} {e} — criando personagem novo.")
            j = None
    if j is None:
        j = criar_personagem()
    j.novidades = [visivel(l).strip() for l in presente_do_porto(j)][:1]
    if iniciar_idle:
        _menu_idle(j)
    while True:
        coletar_novidades(j)
        auto_salvar(j)
        if j.escolha_pendente:
            limpar()
            escolher_no_menu(j)
            continue
        limpar()
        tela_menu(j)
        op = ler_tecla(f" {BOLD}Escolha:{RESET} ")
        if op in ("", "3"):
            _menu_idle(j)
        elif op == "9":
            salvar_man(j)
            print(" Salvo. O andante descansa — e o progresso offline continua contando. Até a próxima!")
            break
        elif op in MENU_OPCOES:
            req, _, acao, pausar = MENU_OPCOES[op]
            if req and not desbloqueado(j, req):
                j.novidades.insert(0, f"🔒 {DESBLOQUEIOS[req]['nome']} ainda não: {requisito_texto(req)}.")
                continue
            acao(j)
            if pausar:
                pausa()

# Telas das fases seguintes (substituídas abaixo quando o sistema existe)
def _em_breve(j):
    j.novidades.insert(0, "🚧 Esse sistema ainda está sendo construído.")

tela_mapa = tela_dungeons = tela_torres = tela_passe = _em_breve

if __name__ == "__main__":
    if os.name == 'nt':
        os.system("")  # habilita cores ANSI e redesenho de tela no console do Windows
    try:
        sys.stdout.reconfigure(errors="replace")  # emoji em console sem UTF-8 vira "?" em vez de erro
    except Exception:
        pass
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Uso: andante [--idle]\n  --idle   abre direto no modo idle (continua o save automático)")
        sys.exit(0)
    try:
        menu(iniciar_idle="--idle" in sys.argv)
    except KeyboardInterrupt:
        print("\nSaindo...")
