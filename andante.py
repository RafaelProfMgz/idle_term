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
            "  ▄▀█ █▄ █ █▀▄ ▄▀█ █▄ █ ▀█▀ █▀▀\n"
            "  █▀█ █ ▀█ █▄▀ █▀█ █ ▀█  █  ██▄"
            f"{RESET}\n{DIM}  a torre que se sobe sozinho · idle de terminal{RESET}")

def largura_tela():
    """Largura útil do terminal (entre 60 e 90 colunas)."""
    try:
        import shutil
        return max(60, min(90, shutil.get_terminal_size((80, 24)).columns - 2))
    except Exception:
        return 78

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
    return jogador.nivel >= nivel_requerido(jogador) and (not flag or jogador.flags.get(flag))

def luta_auto(jogador, vida_inimigo, atq_inimigo):
    """Resolve uma luta inteira sem input. Retorna (venceu, dano_recebido)."""
    vida_ini = jogador.vida
    v = vida_inimigo
    while v > 0 and jogador.vida > 0:
        fogo = jogador.dano_fogo()
        if ("Bola de Fogo" in jogador.feiticos_aprendidos and jogador.mana >= FEITICOS["Bola de Fogo"]["custo_mana"]
                and fogo > jogador.atq and v > jogador.atq):
            jogador.mana -= FEITICOS["Bola de Fogo"]["custo_mana"]
            v -= fogo
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
    """Um passo do jogo idle (Botas Ligeiras dão chance de uma ação extra)."""
    _tick_idle(jogador, res, log)
    extra = min(0.6, FORJA["botas"]["por_nivel"] * jogador.forja.get("botas", 0))
    if extra and random.random() < extra:
        _tick_idle(jogador, res, log, extra=True)

def _tick_idle(jogador, res, log, extra=False):
    def anota(txt, grande=False):
        log.append(txt); del log[:-7]
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
        msg = _auto_distribuir(jogador)
        if msg: anota(f"📈 {msg}")
        for linha in checar_conquistas(jogador):
            anota(linha, grande=True)
        if jogador.auto_compra:
            comprado = auto_comprar(jogador)
            if comprado:
                res["compras"] += 1
                anota(f"🔨 Forja: {FORJA[comprado]['nome']} nível {jogador.forja[comprado]}")
    # Chefe: luta sozinho quando os requisitos batem, a vida está boa e não acabou de perder
    limite = 0.5 if "Teleporte Andar" in jogador.passivas else 0.8
    if requisitos_ok(jogador) and jogador.vida >= jogador.vida_max * limite and not jogador.espera_chefe:
        vida_c, atq_c = stats_chefe(jogador)
        res["chefes_tentados"] += 1
        venceu, dano = luta_auto(jogador, vida_c, atq_c)
        if venceu:
            res["chefes"] += 1
            anota(f"👑 {info['chefe']} derrotado! (-{dano} HP)", grande=True)
            for linha in vencer_chefe(jogador):
                anota(linha)
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
        venceu, dano = luta_auto(jogador, *stats_monstro(jogador))
        res["batalhas"] += 1
        if venceu:
            xp_base = random.randint(10, 25) * jogador.andar * escala * RITMO_XP
            nivel_antes, xp_antes = jogador.nivel, jogador.xp
            subiu = jogador.ganhar_xp(xp_base, silencioso=True)
            ouro = jogador.ganhar_ouro(random.randint(5, 15) * jogador.andar * escala)
            res["ouro_ganho"] += ouro; res["xp_ganho"] += int(xp_base * jogador.mult_xp())
            anota(f"⚔️  {monstro} vencido: +{fmt_num(xp_base * jogador.mult_xp())} XP, +{fmt_num(ouro)} ouro"
                  + (f" (-{fmt_num(dano)} HP)" if dano else ""))
            if subiu:
                anota(f"🌟 LEVEL UP! Nível {jogador.nivel}", grande=True)
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
    if jogador.nivel >= req:
        frac_nivel = 1.0
    else:
        base = req - NIVEIS_POR_VOLTA if jogador.ciclo > 1 else 1
        feito = (jogador.nivel - base) + jogador.xp / max(1, jogador.xp_max)
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

def desenhar_idle(jogador, res, log, velocidade):
    info = ANDARES[jogador.andar]
    vida_c, atq_c = stats_chefe(jogador)
    flag = info.get("req_flag")
    req = nivel_requerido(jogador)
    ok = lambda b: f"{GN}✔{RESET}" if b else f"{RD}✘{RESET}"
    minutos = max(1 / 60, (time.time() - res.get("inicio", time.time())) / 60)
    taxa = (f"  {DIM}(+{fmt_num(res['ouro_ganho'] / minutos)} ouro/min · +{fmt_num(res['xp_ganho'] / minutos)} XP/min){RESET}"
            if minutos >= 0.25 else "")
    frag = f"   {MG}✦ {jogador.fragmentos} fragmento(s){RESET}" + (f" {DIM}→ Altar no menu [A]{RESET}" if jogador.fragmentos >= 2 else "")
    rumo = _rumo_ao_chefe(jogador)
    cond = f"Nível {req} {ok(jogador.nivel >= req)}"
    if flag:
        cond += f" · {FLAG_TEXTO.get(flag, flag)} {ok(jogador.flags.get(flag))}"
    espera = f" {DIM}(treinando: {jogador.espera_chefe}){RESET}" if getattr(jogador, "espera_chefe", 0) else ""
    linhas = [
        secao(f"ANDANTE · MODO IDLE · Volta {jogador.ciclo}", YW, grossa=True),
        f" {BOLD}{jogador.nome}{RESET} · {jogador.classe} · Nível {BOLD}{jogador.nivel}{RESET} · {CY}{jogador.titulo_ativo}{RESET}",
        f" Vida {barra(jogador.vida, jogador.vida_max, 18, GN)} {fmt_num(jogador.vida)}/{fmt_num(jogador.vida_max)}"
        f"   Mana {barra(jogador.mana, jogador.mana_max, 10, MG)} {fmt_num(jogador.mana)}",
        f" XP   {barra(jogador.xp, jogador.xp_max, 18, YW)} {fmt_num(jogador.xp)}/{fmt_num(jogador.xp_max)}",
        f" Ouro {YW}{BOLD}{fmt_num(jogador.ouro)}{RESET}{taxa}",
        f"{frag}" if jogador.fragmentos else "",
        secao(f"Torre · Andar {jogador.andar}: {info['nome']}"),
        f" {_linha_torre(jogador)}",
        f" Chefe {BOLD}{info['chefe']}{RESET} · {cond} · Poder {_cor_poder(poder_contra(jogador, vida_c, atq_c))}{espera}",
        f" Rumo ao chefe {barra(rumo, 1, 24, CY)} {int(rumo * 100)}%",
        secao("Forja" + (" · auto-compra ligada" if jogador.auto_compra else " · auto-compra desligada")),
        f" {_resumo_forja(jogador)}",
        secao("Eventos"),
        f" {YW}{BOLD}★ {res['destaque']}{RESET}" if res.get("destaque") else f" {DIM}★ (os grandes momentos aparecem aqui){RESET}",
    ] + [f"   {l}" for l in log] + [""] * (7 - len(log)) + [
        secao(),
        f" {DIM}[Q] menu   [+/-] velocidade ({str(velocidade).replace('.', ',')}s)   [A] auto-compra   · salva sozinho{RESET}",
    ]
    sys.stdout.write("\033[H\033[J" + "\n".join(l for l in linhas) + "\n")
    sys.stdout.flush()

def auto_play(jogador, passos=None, velocidade=1.0, desenhar=True):
    """Modo idle: joga sozinho para sempre, até você apertar Q (ou Ctrl+C).
    `passos` limita os ticks (usado em testes); `velocidade` = segundos por tick."""
    res = novo_res()
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
                    redesenhar = False
                    for t in teclado.ler():
                        if t.lower() == "q":
                            sair = True
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
    while jogador.auto_compra and compras < 500 and auto_comprar(jogador):
        compras += 1
    jogador.vida = jogador.vida_max; jogador.mana = jogador.mana_max
    return {"minutos": minutos, "xp": int(xp_base * jogador.mult_xp()), "ouro": ouro,
            "niveis": jogador.nivel - nivel_antes, "compras": compras, "eficiencia": ef,
            "limitado": segundos // 60 > minutos}

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
        # Forja e Altar multiplicam (percentuais)
        forja, altar = getattr(self, "forja", {}), getattr(self, "altar", {})
        ancestral = 1 + ALTAR["ancestral"]["por_nivel"] * altar.get("ancestral", 0)
        self.atq = int(self.atq * (1 + FORJA["arma"]["por_nivel"] * forja.get("arma", 0)) * ancestral)
        self.def_ = int(self.def_ * (1 + FORJA["armadura"]["por_nivel"] * forja.get("armadura", 0)) * ancestral)
        self.vida_max = int(self.vida_max * (1 + FORJA["coracao"]["por_nivel"] * forja.get("coracao", 0)))
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
        return int(base * self.mult_dano())

    def dano_por_turno(self):
        """Melhor dano que dá para causar num turno (ataque ou Bola de Fogo)."""
        if "Bola de Fogo" in self.feiticos_aprendidos and self.mana_max >= FEITICOS["Bola de Fogo"]["custo_mana"]:
            return max(self.atq, self.dano_fogo())
        return self.atq

    def mult_ouro(self):
        return (1 + FORJA["sorte"]["por_nivel"] * self.forja.get("sorte", 0)) * (1 + ALTAR["ganancia"]["por_nivel"] * self.altar.get("ganancia", 0))

    def mult_xp(self):
        m = (1 + FORJA["estudo"]["por_nivel"] * self.forja.get("estudo", 0)) * (1 + ALTAR["sabedoria"]["por_nivel"] * self.altar.get("sabedoria", 0))
        return m * (1.25 if "Mestre do Andar" in self.passivas else 1)

    def ganhar_ouro(self, qt):
        """Soma ouro já com bônus (Moeda da Sorte, Ganância). Retorna o valor ganho."""
        qt = int(qt * self.mult_ouro())
        self.ouro += qt
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
    Compara turnos para matar x turnos para morrer, com a vida cheia."""
    turnos_matar = vida_inimigo / max(3, jogador.dano_por_turno())
    dano_recebido = max(1, atq_inimigo - jogador.def_ / 2)
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
    vender_excesso(jogador, [info.get("recompensa", "Troféu")])
    linhas.append(f"🎁 Recompensa: {info.get('recompensa', 'Troféu')} · ✦ +{frag} fragmento(s) para o Altar")
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
        print(secao(f"COMBATE · {nome} · Andar {jogador.andar}", RD, grossa=True))
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
    print(secao(f"{cena['titulo']} · Andar {jogador.andar} · Volta {jogador.ciclo}", CY, grossa=True))
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

# ---------- Telas: Forja / Altar / Status ----------
def _efeito_forja(chave, nivel):
    f = FORJA[chave]
    return f"+{int(f['por_nivel'] * nivel * 100)}% {f['efeito']}"

def tela_forja(jogador):
    msg = ""
    while True:
        limpar()
        print(secao("FORJA DO PORTO", YW, grossa=True))
        print(f' {DIM}O ferreiro bate o martelo sem olhar para você. "Ouro primeiro, conversa depois."{RESET}')
        print(f" Ouro: {YW}{BOLD}{fmt_num(jogador.ouro)}{RESET}")
        print(secao("Melhorias"))
        chaves = list(FORJA)
        for i, k in enumerate(chaves, 1):
            f, nv = FORJA[k], jogador.forja.get(k, 0)
            if forja_no_maximo(jogador, k):
                preco = f"{GN}máximo{RESET}"
            else:
                custo = custo_forja(jogador, k)
                preco = f"{(GN if jogador.ouro >= custo else DIM)}{fmt_num(custo)} ouro{RESET}"
            print(f" [{i}] {f['nome']:<20} nível {nv:<3} {_efeito_forja(k, nv):<18} → próximo: {preco}")
        tralhas = sum(max(0, qt - LIMITE_ITEM.get(item, qt)) * PRECO_ITEM.get(item, 0) * jogador.andar
                      for item, qt in jogador.inven.items())
        print(secao())
        for linha in colunas([f"[M] Comprar o máximo",
                              f"[V] Vender tralhas (~{fmt_num(tralhas)} ouro)",
                              f"[T] Auto-compra no idle: {'LIGADA' if jogador.auto_compra else 'desligada'}",
                              "[0] Voltar"]):
            print(" " + linha)
        if msg:
            print(f" {CY}{msg}{RESET}")
        es = input(" Escolha: ").strip().upper()
        msg = ""
        if es in ("0", ""):
            return
        if es == "M":
            n = 0
            while auto_comprar(jogador):
                n += 1
            msg = f"{n} melhoria(s) compradas." if n else "Ouro insuficiente para qualquer melhoria."
        elif es == "V":
            msg = f"Vendido por {fmt_num(vender_excesso(jogador))} ouro."
        elif es == "T":
            jogador.auto_compra = not jogador.auto_compra
            msg = "Auto-compra " + ("ligada: o idle gasta o ouro sozinho." if jogador.auto_compra else "desligada: você escolhe as compras.")
        elif es.isdigit() and 1 <= int(es) <= len(chaves):
            k = chaves[int(es) - 1]
            pago = comprar_forja(jogador, k)
            msg = f"{FORJA[k]['nome']} agora no nível {jogador.forja[k]} (-{fmt_num(pago)} ouro)." if pago else "Não dá: ouro insuficiente ou nível máximo."

def tela_altar(jogador):
    msg = ""
    while True:
        limpar()
        print(secao("ALTAR DOS FRAGMENTOS", MG, grossa=True))
        print(f" {DIM}Cada chefe deixa um fragmento da torre; o Rei das Sombras deixa {FRAGMENTOS_REI}.{RESET}")
        print(f" {DIM}O que se compra aqui fica com você para sempre.{RESET}")
        print(f" {MG}{BOLD}✦ {jogador.fragmentos} fragmento(s){RESET}")
        print(secao("Bênçãos"))
        chaves = list(ALTAR)
        for i, k in enumerate(chaves, 1):
            a, nv = ALTAR[k], jogador.altar.get(k, 0)
            if nv >= a.get("max", 10**9):
                preco = f"{GN}máximo{RESET}"
            else:
                c = custo_altar(jogador, k)
                preco = f"{(GN if jogador.fragmentos >= c else DIM)}{c} ✦{RESET}"
            print(f" [{i}] {a['nome']:<17} nível {nv:<3} {a['desc']:<42} {preco}")
        print(secao())
        print(" [0] Voltar")
        if msg:
            print(f" {CY}{msg}{RESET}")
        es = input(" Escolha: ").strip()
        msg = ""
        if es in ("0", ""):
            return
        if es.isdigit() and 1 <= int(es) <= len(chaves):
            k = chaves[int(es) - 1]
            pago = comprar_altar(jogador, k)
            msg = f"{ALTAR[k]['nome']} agora no nível {jogador.altar[k]}." if pago else "Fragmentos insuficientes (ou nível máximo)."

def mostrar_status(jogador):
    a = jogador.atributos
    print(secao(f"{jogador.nome} · {jogador.classe}", YW, grossa=True))
    print(f" Volta {jogador.ciclo} · Andar {jogador.andar} · Nível {jogador.nivel} · XP {fmt_num(jogador.xp)}/{fmt_num(jogador.xp_max)}")
    print(f" Vida {fmt_num(jogador.vida)}/{fmt_num(jogador.vida_max)} · Mana {fmt_num(jogador.mana)}/{fmt_num(jogador.mana_max)}"
          f" · ATQ {fmt_num(jogador.atq)} · DEF {fmt_num(jogador.def_)}")
    print(f" Atributos: F={a['forca']} D={a['destreza']} I={a['inteligencia']} V={a['vitalidade']} C={a['carisma']}"
          + (f"  {YW}({jogador.pontos_atributo} pontos livres){RESET}" if jogador.pontos_atributo else ""))
    t = TITULOS_DEF[jogador.titulo_ativo]
    print(f" Título: {CY}{jogador.titulo_ativo}{RESET} (+{t['bonus_atq']} ATQ / +{t['bonus_def']} DEF)")
    print(f" Passivas: {', '.join(jogador.passivas) or 'nenhuma'}")
    print(f" Bônus: ouro ×{jogador.mult_ouro():.2f} · XP ×{jogador.mult_xp():.2f}".replace(".", ","))
    print(secao("Forja e Altar"))
    print(f" {_resumo_forja(jogador)}")
    print(" " + " · ".join(f"{ALTAR[k]['nome']} {v}" for k, v in jogador.altar.items()) + f" · ✦ {jogador.fragmentos}")
    feitas = [c for c, v in jogador.conquistas.items() if v]
    print(secao(f"Conquistas {len(feitas)}/{len(CONQUISTAS_DEF)}"))
    for c, d in CONQUISTAS_DEF.items():
        print(f" {GN + '🏆' if jogador.conquistas.get(c) else DIM + '· '}{RESET} {c} {DIM}— {d['desc']}{RESET}")
    print(secao("Inventário"))
    print(" " + (" · ".join(f"{k} ×{v}" for k, v in jogador.inven.items()) or "vazio"))
    print(secao("Torre"))
    desenhar_torre(jogador)

def cena_chefe(jogador):
    info = ANDARES[jogador.andar]
    limpar()
    print(secao(f"CHEFE DO ANDAR {jogador.andar}", RD, grossa=True))
    vida_c, atq_c = stats_chefe(jogador)
    print(f" {info['chefe']} · {fmt_num(vida_c)} HP · ATQ {fmt_num(atq_c)} · seu Poder {_cor_poder(poder_contra(jogador, vida_c, atq_c))}")
    flag = info.get("req_flag")
    print(f" Precisa: Nível {nivel_requerido(jogador)}" + (f" · {FLAG_TEXTO.get(flag, flag)}" if flag else ""))
    if jogador.nivel < nivel_requerido(jogador):
        print(f" {YW}Você ainda não tem nível suficiente — o modo idle [3] treina você.{RESET}")
        pausa(" ENTER..."); return
    if flag and not jogador.flags.get(flag):
        print(f" {YW}Ainda falta: {FLAG_TEXTO.get(flag, flag)} (explore o andar [1]).{RESET}")
        pausa(" ENTER..."); return
    print(" [1] Combater o chefe   [2] Voltar")
    es = input(" Escolha: ").strip()
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
        f"Fragmentos: {jogador.fragmentos}",
        f"Forja: {' '.join(f'{k}={v}' for k, v in jogador.forja.items())}",
        f"Altar: {' '.join(f'{k}={v}' for k, v in jogador.altar.items())}",
        f"AutoCompra: {'sim' if jogador.auto_compra else 'nao'}",
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
    tem_fragmentos = False
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
    if r["limitado"]:
        print(f"   {DIM}Você ficou fora mais que o limite. O Altar (Eco do Andante) aumenta isso.{RESET}")
    if requisitos_ok(jogador):
        print(f"   {CY}O chefe {ANDARES[jogador.andar]['chefe']} já pode ser enfrentado — o idle cuida disso.{RESET}")
    print(secao())
    return True

# ---------- Menu ----------
def criar_personagem():
    print(secao("NOVO ANDANTE", YW, grossa=True))
    nome = input(" Nome do personagem: ").strip() or "Aventurier"
    print(f" {BOLD}[G]{RESET} Guerreiro {DIM}— mais vida, ataque e defesa{RESET}")
    print(f" {BOLD}[M]{RESET} Mago      {DIM}— muita mana e magia, mas frágil{RESET}")
    print(f" {BOLD}[A]{RESET} Arqueiro  {DIM}— equilibrado, começa com ouro{RESET}")
    classe_input = input(" Classe (G/M/A): ").strip().upper()
    classe = "Mago" if classe_input == "M" else "Arqueiro" if classe_input == "A" else "Guerreiro"
    idade_str = input(" Idade (número): ").strip()
    j = Jogador(nome, classe, 1)
    j.idade = int(idade_str) if idade_str.isdigit() else 18
    return j

def dica_do_menu(j):
    """Uma sugestão do que fazer agora — a coisa mais útil primeiro."""
    if j.pontos_atributo:
        return f"Você tem {j.pontos_atributo} ponto(s) de atributo para distribuir [5]."
    baratos = [custo_altar(j, k) for k in ALTAR if j.altar.get(k, 0) < ALTAR[k].get("max", 10**9)]
    if baratos and j.fragmentos >= min(baratos):
        return f"Seus ✦ {j.fragmentos} fragmentos já compram uma bênção no Altar [A]."
    if not j.auto_compra and any(j.ouro >= custo_forja(j, k) for k in FORJA if not forja_no_maximo(j, k)):
        return "Tem ouro sobrando: passe na Forja [F]."
    if requisitos_ok(j):
        return f"O chefe {ANDARES[j.andar]['chefe']} está ao seu alcance [2] — ou deixe o idle cuidar disso [3]."
    flag = ANDARES[j.andar].get("req_flag")
    if flag and not j.flags.get(flag):
        return f"Para chegar ao chefe falta: {FLAG_TEXTO.get(flag, flag)} [1]."
    return "Deixe o idle rodar [3]: ele luta, compra na Forja e sobe a torre sozinho."

def tela_menu(j):
    info = ANDARES[j.andar]
    vida_c, atq_c = stats_chefe(j)
    req = nivel_requerido(j)
    flag = info.get("req_flag")
    ok = lambda b: f"{GN}✔{RESET}" if b else f"{RD}✘{RESET}"
    cond = f"Nível {req} {ok(j.nivel >= req)}" + (f" · {FLAG_TEXTO.get(flag, flag)} {ok(j.flags.get(flag))}" if flag else "")
    linhas = [
        logo_ascii(),
        secao(grossa=True, cor=YW),
        f" {BOLD}{j.nome}{RESET} · {j.classe} · Nível {BOLD}{j.nivel}{RESET} · {CY}{j.titulo_ativo}{RESET}",
        f" Vida {barra(j.vida, j.vida_max, 18, GN)} {fmt_num(j.vida)}/{fmt_num(j.vida_max)}"
        f"   Mana {barra(j.mana, j.mana_max, 10, MG)} {fmt_num(j.mana)}",
        f" XP   {barra(j.xp, j.xp_max, 18, YW)} {fmt_num(j.xp)}/{fmt_num(j.xp_max)}",
        f" Ouro {YW}{BOLD}{fmt_num(j.ouro)}{RESET}   {MG}✦ {j.fragmentos}{RESET}   Volta {j.ciclo}"
        f"   {DIM}Conquistas {sum(j.conquistas.values())}/{len(CONQUISTAS_DEF)}{RESET}",
        f" Torre {_linha_torre(j)}   {CY}{info['nome']}{RESET}",
        f" Chefe {BOLD}{info['chefe']}{RESET} · {cond} · Poder {_cor_poder(poder_contra(j, vida_c, atq_c))}",
        secao("Jogar"),
        f"  {GN}{BOLD}[3] ▶ MODO IDLE{RESET} {DIM}— o andante luta, compra e sobe sozinho{RESET}",
    ]
    linhas += ["  " + l for l in colunas(["[1] Explorar o andar", "[2] Enfrentar o chefe"])]
    linhas.append(secao("Fortalecer"))
    pontos = f" {YW}({j.pontos_atributo}){RESET}" if j.pontos_atributo else ""
    linhas += ["  " + l for l in colunas([f"[F] Forja {DIM}(ouro){RESET}", f"[A] Altar {DIM}(fragmentos){RESET}",
                                          f"[5] Distribuir pontos{pontos}", "[4] Magia"])]
    linhas.append(secao("Sistema"))
    linhas += ["  " + l for l in colunas(["[6] Status completo", "[7] Salvar", "[8] Carregar", "[9] Sair"])]
    linhas += [secao(grossa=True, cor=YW), f" {YW}💡{RESET} {dica_do_menu(j)}"]
    print("\n".join(linhas))

def resumo_idle(res):
    minutos = max(1 / 60, (time.time() - res["inicio"]) / 60)
    print(secao("IDLE PAUSADO", YW, grossa=True))
    print(f" {res['ticks']} passos em {int(minutos)}min · {res['batalhas']} batalhas · {res['chefes']} chefe(s) · {res['compras']} compra(s)")
    print(f" {YW}+{fmt_num(res['xp_ganho'])} XP{RESET} · {YW}+{fmt_num(res['ouro_ganho'])} ouro{RESET}")
    if res.get("destaque"):
        print(f" {BOLD}★ {res['destaque']}{RESET}")
    print(secao())

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
            resp = input(f" Continuar? [S/n] {DIM}(N = novo personagem, substitui o auto save){RESET} ").strip().upper()
            if resp == "N":
                j = None
            elif mostrar_offline(j, ultimo):
                pausa(" ENTER para continuar...")
        except Exception as e:
            print(f" {RD}[⚠️ AUTO SAVE ILEGÍVEL]{RESET} {e} — criando personagem novo.")
            j = None
    if j is None:
        j = criar_personagem()
    if iniciar_idle:
        res = auto_play(j)
        limpar(); resumo_idle(res); pausa(" ENTER para ir ao menu...")
    while True:
        novidades = checar_conquistas(j)
        auto_salvar(j)
        if novidades:
            for linha in novidades:
                print(" " + linha)
            pausa(" ENTER...")
        limpar()
        tela_menu(j)
        op = input(" Escolha: ").strip().upper()
        if op == "1": cena_explorar(j)
        elif op == "2": cena_chefe(j)
        elif op == "3":
            res = auto_play(j)
            limpar(); resumo_idle(res); pausa(" ENTER...")
        elif op == "4":
            print(" Feitiços:", ", ".join(j.feiticos_aprendidos))
            nome = input(" Feitiço (ou 0): ").strip()
            if nome != "0": j.usar_magia(nome)
            pausa()
        elif op == "5": j.distribuir_pontos(); pausa()
        elif op == "F": tela_forja(j)
        elif op == "A": tela_altar(j)
        elif op == "6":
            limpar(); mostrar_status(j); pausa(" ENTER...")
        elif op == "7": salvar_man(j); pausa()
        elif op == "8":
            if carregar_man(j): pausa()
        elif op == "9":
            salvar_man(j)
            print(" Salvo. O andante descansa — e o progresso offline continua contando. Até a próxima!")
            break

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
