#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andante · versão gráfica (Pyxel) — PROTÓTIPO

Usa o andante.py como motor: o mesmo personagem, o mesmo idle, os mesmos sistemas
e o mesmo save (save_auto_idle.txt). Esta janela só desenha: cenário do andar,
herói, monstro, chefe, grupo, barras e o log do idle.

Rodar:
    .venv/bin/python andante_gui.py         (precisa de: pip install pyxel)

Teclas: [ESPAÇO] pausa · [+]/[-] velocidade · [1]/[2] responder escolha · [Q]/[ESC] salvar e sair

Os sprites são pixel art escrita aqui mesmo (SPRITES), 16×16, uma letra por cor (COR).
Fonte: PixelMplus10 (assets/, licença M+ FONT LICENSE: livre para usar e distribuir).
"""
import math, os, random, sys, time
try:
    import pyxel
except ImportError:
    # Aberto com o python3 do sistema? Se o .venv do projeto existe, reabre por ele.
    _pasta = os.path.dirname(os.path.abspath(__file__))
    _venv = os.path.join(_pasta, ".venv", "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")
    if os.path.exists(_venv) and os.path.abspath(sys.executable) != os.path.abspath(_venv):
        os.execv(_venv, [_venv, os.path.abspath(__file__)] + sys.argv[1:])
    sys.exit("A versão gráfica precisa do Pyxel:\n  python3 -m venv .venv && .venv/bin/pip install pyxel\n"
             "  .venv/bin/python andante_gui.py\n(a versão de terminal continua sendo: python3 andante.py)")
import andante as A

LARG, ALT = 320, 240
FPS = 30
CHAO = 142                     # y dos pés de quem está em cena
FONTE = os.path.join(A.PASTA_JOGO, "assets", "PixelMplus10-Regular.ttf")
VELOCIDADES = [1.0, 0.5, 0.25, 0.1]   # segundos por passo do idle
NA_WEB = sys.platform == "emscripten"   # rodando no navegador (site: public/pixel/)
PREFIXO_WEB = "andante:"                # mesma chave de localStorage do terminal do site (src/lib/saves.ts)

# Paleta padrão do Pyxel: 0 preto (transparente nos sprites) 1 marinho 2 roxo 3 verde 4 marrom
# 5 azul-escuro 6 azul-claro 7 branco 8 vermelho 9 laranja 10 amarelo 11 lima 12 azul 13 cinza 14 rosa 15 pele
COR = {".": 0, "k": 1, "p": 2, "g": 3, "n": 4, "d": 5, "c": 6, "w": 7, "r": 8, "o": 9, "y": 10,
       "l": 11, "b": 12, "m": 13, "i": 14, "s": 15}

SPRITES = {
    "Guerreiro": [
        "................", "......kkkk......", ".....kmmmmk.....", "....kmmwwmmk....",
        "....kmkkkkmk....", "....kksssskk....", ".....ksksk......", ".....kssssk.....",
        "...kk.kkkk..ww..", "..kbbkrrrrk.wm..", "..kbbkrrrrrkmk..", "..kbbkrrrrk.yk..",
        "...kk.knnk......", "......kmmk......", ".....kmk.kmk....", ".....kk...kk...."],
    "Mago": [
        "........k.......", ".......kpk......", "......kppk......", ".....kpppk......",
        "....kppyppk..oo.", "...kkkkkkkkk.oo.", ".....kssssk..nn.", ".....ksksk...n..",
        ".....kssssk..n..", "....kbbbbbbk.n..", "...kbbbybbbbkn..", "...kbbbbbbbbkn..",
        "...kbbbbbbbbkn..", "...kbbbbbbbbkn..", "...kkkkkkkkkkn..", "................"],
    "Arqueiro": [
        "................", "......kkkk......", ".....kggggk.....", "....kggggggk..n.",
        "....kgssssgk...n", "....kkskskkk...n", ".....kssssk....n", "......kkkk.....n",
        "....kgnnnngk..kn", "...kgnnnnnnkkkkn", "...kgnnnnnngk..n", "....kgnnnngk...n",
        ".....knnnnk...n.", ".....kmk.kmk....", ".....kmk.kmk....", ".....kk...kk...."],
    1: [  # goblin
        "................", "................", "..kk........kk..", "..kllk.kkk.kllk.",
        "...kllklllkllk..", "....kllllllllk..", "....klrlllrllk..", "....kllllllllk..",
        ".....kllwwllk...", "......kkkkkk....", ".....knnnnnnk...", "....knnnnnnnnk..",
        "....kl.nnnn.lk..", ".....knnnnnnk...", ".....klk..klk...", ".....kk....kk..."],
    2: [  # armadura vazia
        "................", "......kkkk......", ".....kmmmmk.....", "....kmmmmmmk....",
        "....kmkkkkmk....", "....kmkckckk....", "....kmmmmmmk....", "...kkmmmmmmkk...",
        "..kmmkmmmmkmmk..", "..kmmkmmmmkmmk..", "..kmmkmrrmkmmk..", "...kkkmmmmkkk...",
        ".....kmmmmk.....", ".....kmkkmk.....", "....kmmk.kmmk...", "....kkk...kkk..."],
    3: [  # filhote de dragão
        "................", ".........kkk....", "........krrrk...", ".......krrwrrk..",
        "..k....krrrrrrk.", ".kok..krrrkkkk..", ".koook.krrk.....", "..kooookrrrk....",
        "...kooorrrrrk...", "....krrryyyrrk..", "....krryyyyyrk..", "...krrryyyyrrk..",
        "..krr.krrrrrk...", ".kr...krk.krk...", "......kk...kk...", "................"],
    4: [  # acólito cego
        "................", "......kkkk......", ".....kwwwwk.....", "....kwwwwwwk....",
        "....kwkkkkwk....", "....kksmmskk....", ".....kssssk.....", "....kwwwwwwk....",
        "...kwwwiiwwwk...", "...kwwwiiwwwk...", "..kswwwwwwwwsk..", "...kwwwwwwwwk...",
        "...kwwwwwwwwk...", "...kwwwwwwwwk...", "..kwwwwwwwwwwk..", "..kkkkkkkkkkkk.."],
    5: [  # olho sem fundo
        "................", ".....kkkkkk.....", "...kkppppppkk...", "..kppppppppppk..",
        ".kppwwwwwwwwppk.", ".kpwwwccccwwwpk.", "kppwwcckkccwwppk", "kppwwckkkkcwwppk",
        "kppwwckkkkcwwppk", "kppwwcckkccwwppk", ".kpwwwccccwwwpk.", ".kppwwwwwwwwppk.",
        "..kppppppppppk..", "...kkppppppkk...", "....kp.kk.pk....", "....k..kk..k...."],
    "bau": [
        "................", "................", "................", "..kkkkkkkkkkkk..",
        ".knnnnnnnnnnnnk.", ".knoooooooooonk.", ".kyyyyyyyyyyyyk.", ".knnnnnkknnnnnk.",
        ".knnnnkyykknnnk.", ".knnnnnkknnnnnk.", ".knnnnnnnnnnnnk.", ".kyyyyyyyyyyyyk.",
        ".kkkkkkkkkkkkkk.", "................", "................", "................"],
    "aliado": [   # silhueta dos companheiros (recolorida pelo elemento)
        "................", "................", "......kkkk......", ".....kbbbbk.....",
        ".....kbsbsk.....", ".....kbbbbk.....", "......kkkk......", ".....kbbbbk.....",
        "....kbbbbbbk....", "....kbbbbbbk....", ".....kbbbbk.....", ".....kbkkbk.....",
        ".....kk..kk.....", "................", "................", "................"],
}
ORDEM = list(SPRITES)
COR_ELEMENTO = {"Água": 12, "Fogo": 8, "Terra": 4, "Luz": 10, "Sombra": 2}
# troca de cor que transforma o monstro do andar no chefe do andar
PAL_CHEFE = {1: [(11, 8), (3, 2)], 2: [(13, 2), (6, 8)], 3: [(8, 2), (9, 8), (10, 9)],
             4: [(7, 10), (14, 8)], 5: [(2, 8), (6, 10)]}
COR_RANK = [7, 11, 12, 14, 10, 8]
SIMBOLOS = set(" .,:;!?()[]{}+-/*%'\"<>=_#&@·×→…|✔✘★")


def limpo(texto):
    """Texto do motor (com cores ANSI e emoji) → só o que a fonte pixel desenha."""
    s = "".join(c for c in A.visivel(texto) if c.isalnum() or c in SIMBOLOS)
    return " ".join(s.split())


def cor_da_linha(linha):
    t = A.visivel(linha)
    for marca, cor in (("👑", 10), ("💀", 8), ("🌟", 10), ("LEVEL", 10), ("✨", 14), ("💠", 12), ("📜", 9),
                       ("📋", 9), ("🔨", 13), ("💰", 10), ("⚔", 7), ("🏆", 10), ("🎁", 11), ("🌀", 6)):
        if marca in t:
            return cor
    return 13


def preparar_web():
    """No navegador: o save vem do localStorage (o mesmo do terminal do site) e cada gravação volta para lá."""
    import js
    for caminho in (A.SAVE_AUTO, A.SAVE_MANUAL):
        try:
            texto = js.localStorage.getItem(PREFIXO_WEB + os.path.basename(caminho))
        except Exception:
            texto = None
        if texto:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
    gravar_original = A.gravar_save

    def gravar_save(jogador, caminho, titulo):
        gravar_original(jogador, caminho, titulo)
        try:
            with open(caminho, encoding="utf-8") as f:
                js.localStorage.setItem(PREFIXO_WEB + os.path.basename(caminho), f.read())
        except Exception:
            pass   # modo privado / armazenamento bloqueado: o jogo segue sem salvar
    A.gravar_save = gravar_save


class Andante:
    def __init__(self):
        pyxel.init(LARG, ALT, title="Andante", fps=FPS, quit_key=pyxel.KEY_NONE, display_scale=3)
        for i, nome in enumerate(ORDEM):
            pyxel.images[0].set(i * 16, 0, ["".join(f"{COR[c]:x}" for c in linha.ljust(16, ".")[:16]) for linha in SPRITES[nome]])
        self.fonte = pyxel.Font(FONTE, 10)
        A.digitar = lambda *a, **k: None
        A.limpar = lambda: None
        if NA_WEB:
            preparar_web()
        self.j, self.banner = self._carregar()
        self.banner_ate = FPS * 6
        self.j.idle_interativo = True
        self.res = A.novo_res()
        self.log = ["O andante segue sozinho. [ESPAÇO] pausa, [Q] salva e sai."]
        self.vel = 0
        self.pausado = False
        self.prox_passo = 0
        self.anim = {"ataque": 0, "dano_monstro": 0, "dano_heroi": 0, "chefe": 0, "vitoria_chefe": 0,
                     "nivel": 0, "bau": 0, "fade": 0}
        self.rank_bau = 0
        self.flutuantes = []      # [x, y, texto, cor, vida]
        self.particulas = []      # [x, y, vx, vy, cor, vida]
        self.monstro = 1
        self.nome_monstro = ""
        random.seed()
        self.estrelas = [(random.randrange(LARG), random.randrange(36, CHAO), random.randrange(60)) for _ in range(60)]
        pyxel.run(self.update, self.draw)

    # ---------- motor ----------
    def _carregar(self):
        if os.path.exists(A.SAVE_AUTO):
            j = A.Jogador("Temp", "Guerreiro", 1)
            ultimo = A.ler_save(j, A.SAVE_AUTO)
            r = A.progresso_offline(j, time.time() - ultimo) if ultimo else None
            if r:
                return j, f"Fora por {r['minutos'] // 60}h{r['minutos'] % 60:02d}: +{A.fmt_num(r['xp'])} XP, +{A.fmt_num(r['ouro'])} ouro"
            return j, f"Bem-vindo de volta, {j.nome}."
        return A.Jogador("Andante", "Guerreiro", 1), "Um novo andante chega ao Porto."

    def _salvar_e_sair(self):
        A.auto_salvar(self.j)
        if NA_WEB:   # no site não existe "fechar": só salva e avisa
            self.banner, self.banner_ate = "Progresso salvo neste navegador.", pyxel.frame_count + FPS * 2
            return
        self.j.idle_interativo = False
        pyxel.quit()

    def _passo(self):
        j, r = self.j, self.res
        antes = dict(batalhas=r["batalhas"], mortes=r["mortes"], chefes=r["chefes"], tentados=r["chefes_tentados"],
                     xp=r["xp_ganho"], ouro=r["ouro_ganho"], nivel=j.nivel, andar=j.andar, itens=j.stats.get("item", 0))
        ultimo = self.log[-1] if self.log else None
        A.tick_idle(j, r, self.log)
        idx = next((i for i in range(len(self.log) - 1, -1, -1) if self.log[i] is ultimo), -1)
        novas = self.log[idx + 1:]
        # o que aconteceu vira animação
        if r["chefes_tentados"] > antes["tentados"]:
            self.anim["chefe"] = 40
            self.monstro = antes["andar"]
            self.nome_monstro = A.ANDARES[antes["andar"]]["chefe"]
            if r["chefes"] > antes["chefes"]:
                self.anim["vitoria_chefe"] = 45
                self._explosao(244, CHAO - 32, 10, 40)
                self._flutua(244, CHAO - 84, "CHEFE DERROTADO!", 10)
            else:
                self.anim["dano_heroi"] = 12
                self._flutua(80, CHAO - 48, "derrota...", 8)
        elif r["batalhas"] > antes["batalhas"]:
            self.monstro = j.andar
            for linha in novas:
                t = limpo(linha)
                if " vencido" in t or "te derrubou" in t:
                    self.nome_monstro = t.split(" vencido")[0].split(" te derrubou")[0]
            self.anim["ataque"] = 10
            if r["mortes"] > antes["mortes"]:
                self.anim["dano_heroi"] = 12
            else:
                self.anim["dano_monstro"] = 10
                self._explosao(240, CHAO - 16, 7, 8)
                if r["xp_ganho"] > antes["xp"]:
                    self._flutua(240, CHAO - 86, f"+{A.fmt_num(r['xp_ganho'] - antes['xp'])} XP", 10)
                if r["ouro_ganho"] > antes["ouro"]:
                    self._flutua(240, CHAO - 76, f"+{A.fmt_num(r['ouro_ganho'] - antes['ouro'])} ouro", 9)
        if j.nivel > antes["nivel"]:
            self.anim["nivel"] = 45
            self._explosao(84, CHAO - 24, 10, 24)
        if j.stats.get("item", 0) > antes["itens"]:
            self.anim["bau"] = 40
            self.rank_bau = 0
            for linha in novas:
                for i, rank in enumerate(A.RANKS):
                    if f"[{rank['letra']} {rank['nome']}]" in A.visivel(linha):
                        self.rank_bau = i
        if j.andar != antes["andar"]:
            self.anim["fade"] = 20

    def _flutua(self, x, y, texto, cor):
        """Texto que sobe e some. Um novo substitui o anterior do mesmo lugar (no modo rápido não empilha)."""
        self.flutuantes = [f for f in self.flutuantes if (f[0], f[5]) != (x, y)]
        self.flutuantes.append([x, y, texto, cor, 36, y])

    def _explosao(self, x, y, cor, n):
        for _ in range(n):
            ang, v = random.uniform(0, math.tau), random.uniform(0.6, 2.4)
            self.particulas.append([x, y, math.cos(ang) * v, math.sin(ang) * v - 1, cor, random.randint(12, 26)])

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self._salvar_e_sair()
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.pausado = not self.pausado
        if pyxel.btnp(pyxel.KEY_EQUALS) or pyxel.btnp(pyxel.KEY_KP_PLUS) or pyxel.btnp(pyxel.KEY_RIGHT):
            self.vel = min(len(VELOCIDADES) - 1, self.vel + 1)
        if pyxel.btnp(pyxel.KEY_MINUS) or pyxel.btnp(pyxel.KEY_KP_MINUS) or pyxel.btnp(pyxel.KEY_LEFT):
            self.vel = max(0, self.vel - 1)
        if self.j.escolha_pendente:
            for n, tecla in enumerate((pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3)):
                if pyxel.btnp(tecla):
                    A.resolver_escolha(self.j, n)
        if not self.pausado and pyxel.frame_count >= self.prox_passo:
            self._passo()
            self.prox_passo = pyxel.frame_count + max(1, int(FPS * VELOCIDADES[self.vel]))
            if pyxel.frame_count % (FPS * 10) < 1:
                A.auto_salvar(self.j)
        for k in self.anim:
            self.anim[k] = max(0, self.anim[k] - 1)
        for f in self.flutuantes:
            f[1] -= 0.6; f[4] -= 1
        self.flutuantes = [f for f in self.flutuantes if f[4] > 0]
        for p in self.particulas:
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.12; p[5] -= 1
        self.particulas = [p for p in self.particulas if p[5] > 0]

    # ---------- desenho ----------
    def texto(self, x, y, s, cor, sombra=True):
        s = limpo(s)
        if sombra:
            pyxel.text(x + 1, y + 1, s, 0, self.fonte)
        pyxel.text(x, y, s, cor, self.fonte)

    def caber(self, s, largura):
        s = limpo(s)
        while s and self.fonte.text_width(s) > largura:
            s = s[:-2] + "…"
        return s

    def sprite(self, nome, x, y, escala=2, virar=False, trocas=(), branco=False):
        u = ORDEM.index(nome) * 16
        for a, b in trocas:
            pyxel.pal(a, b)
        if branco:
            for c in range(1, 16):
                pyxel.pal(c, 7)
        pyxel.blt(x - 8, y - 8, 0, u, 0, -16 if virar else 16, 16, 0, scale=escala)
        pyxel.pal()

    def barra(self, x, y, w, frac, cor, fundo=1):
        frac = max(0.0, min(1.0, frac))
        pyxel.rect(x, y, w, 4, fundo)
        pyxel.rect(x, y, int(w * frac), 4, cor)
        pyxel.rectb(x - 1, y - 1, w + 2, 6, 0)

    def cenario(self, andar):
        f = pyxel.frame_count
        if andar == 1:   # Porto: céu, mar, cais
            pyxel.rect(0, 36, LARG, 70, 6)
            pyxel.circ(270, 58, 10, 10)
            pyxel.rect(300, 46, 10, 60, 13); pyxel.tri(296, 46, 314, 46, 305, 34, 13)   # a torre ao longe
            pyxel.rect(0, 100, LARG, 42, 5)
            for i in range(0, LARG, 16):
                pyxel.line(i + (f // 4) % 16, 108 + (i // 16) % 3 * 8, i + 6 + (f // 4) % 16, 108 + (i // 16) % 3 * 8, 12)
            pyxel.rect(0, CHAO, LARG, 6, 4)
            for i in range(0, LARG, 12):
                pyxel.line(i, CHAO, i, CHAO + 5, 0)
        elif andar == 2:  # Castelo: muralha de pedra e estandartes
            pyxel.rect(0, 36, LARG, CHAO - 36, 1)
            for y in range(36, CHAO, 10):
                for x in range((y // 10) % 2 * 10 - 10, LARG, 20):
                    pyxel.rectb(x, y, 20, 10, 5)
            for x in (40, 160, 280):
                pyxel.rect(x, 44, 14, 34, 8); pyxel.tri(x, 78, x + 14, 78, x + 7, 72, 1)
                pyxel.circ(x + 7, 54, 3, 10)
            pyxel.rect(0, CHAO, LARG, 6, 13)
        elif andar == 3:  # Caverna: pedra, estalactites, lava
            pyxel.rect(0, 36, LARG, CHAO - 36, 0)
            for x in range(0, LARG, 26):
                pyxel.tri(x, 36, x + 18, 36, x + 9, 52 + (x * 7) % 14, 4)
            pyxel.rect(0, CHAO, LARG, 6, 4)
            for x in range(0, LARG, 4):
                altura = 2 + int(1.5 * math.sin((x + f) / 6))
                pyxel.line(x, CHAO + 6, x, CHAO + 6 - altura, 9 if (x // 4 + f // 6) % 3 else 8)
            if f % 6 == 0:
                self.particulas.append([random.randrange(LARG), CHAO, random.uniform(-0.3, 0.3), -1.2, 9, 30])
        elif andar == 4:  # Templo: colunas e velas
            pyxel.rect(0, 36, LARG, CHAO - 36, 2)
            for x in (20, 100, 200, 280):
                pyxel.rect(x, 50, 16, CHAO - 50, 13); pyxel.rect(x + 2, 50, 3, CHAO - 50, 7)
                pyxel.rect(x - 3, 46, 22, 5, 7)
                chama = 10 if (f // 5 + x) % 3 else 9
                pyxel.rect(x + 6, CHAO - 10, 4, 8, 7); pyxel.pset(x + 7, CHAO - 12, chama); pyxel.pset(x + 8, CHAO - 13, chama)
            pyxel.rect(0, CHAO, LARG, 6, 13)
        else:             # Abismo: estrelas no chão, névoa
            pyxel.rect(0, 36, LARG, CHAO - 36, 0)
            for x, y, fase in self.estrelas:
                if (f + fase) % 60 < 40:
                    pyxel.pset(x, y, 7 if (f + fase) % 60 < 20 else 6)
            pyxel.dither(0.35)
            for i in range(5):
                pyxel.circ((i * 80 + f // 3) % (LARG + 60) - 30, CHAO - 6, 26, 2)
            pyxel.dither(1.0)
            for i in range(0, LARG, 24):
                pyxel.rect(i, CHAO, 18, 6, 2)

    def draw(self):
        j = self.j
        pyxel.cls(0)
        self.cenario(j.andar)
        f = pyxel.frame_count
        # grupo atrás do herói
        for n, cid in enumerate(j.grupo[:3]):
            info = A.COMPANHEIROS.get(cid)
            if info:
                cor = COR_ELEMENTO.get(info["elem"], 12)
                self.sprite("aliado", 40 - n * 16, CHAO - 14 + int(math.sin((f + n * 9) / 8) * 1.5), 2, trocas=[(12, cor)])
        # herói
        avanco = int(math.sin(self.anim["ataque"] / 10 * math.pi) * 24) if self.anim["ataque"] else 0
        balanco = int(math.sin(f / 10) * 1.5)
        self.sprite(j.classe if j.classe in SPRITES else "Guerreiro", 84 + avanco, CHAO - 24 + balanco, 3,
                    branco=self.anim["dano_heroi"] % 4 >= 2)
        # monstro ou chefe
        andar_m = self.monstro if self.monstro in SPRITES else 1
        if self.anim["chefe"] or self.anim["vitoria_chefe"]:
            if not (self.anim["vitoria_chefe"] and self.anim["vitoria_chefe"] < 25 and f % 4 < 2):
                tremor = random.randint(-1, 1) if self.anim["dano_monstro"] or self.anim["vitoria_chefe"] else 0
                self.sprite(andar_m, 244 + tremor, CHAO - 32, 4, virar=True, trocas=PAL_CHEFE.get(andar_m, []),
                            branco=self.anim["vitoria_chefe"] % 4 >= 2)
            nome = A.ANDARES[andar_m]["chefe"]
            self.texto(244 - self.fonte.text_width(nome) // 2, CHAO - 74, nome, 8)
        else:
            tremor = random.randint(-2, 2) if self.anim["dano_monstro"] else 0
            self.sprite(andar_m, 240 + tremor, CHAO - 24 + int(math.sin(f / 7) * 2), 3, virar=True,
                        branco=self.anim["dano_monstro"] % 4 >= 2)
            if self.nome_monstro:
                self.texto(240 - self.fonte.text_width(self.nome_monstro) // 2, CHAO - 58, self.nome_monstro, 7)
        # baú quando cai item
        if self.anim["bau"]:
            subida = min(12, (40 - self.anim["bau"]) * 2)
            self.sprite("bau", 160, CHAO - 10 - subida // 2, 1.5)
            r = A.RANKS[self.rank_bau]
            self.texto(160 - self.fonte.text_width(r["nome"]) // 2, CHAO - 40 - subida // 2, r["nome"], COR_RANK[self.rank_bau])
        for p in self.particulas:
            pyxel.pset(p[0], p[1], p[4])
        for x, y, t, cor, vida, _ in self.flutuantes:
            self.texto(int(x - self.fonte.text_width(limpo(t)) / 2), int(y), t, cor)
        if self.anim["nivel"]:
            self.texto(56, CHAO - 74, "NOVO NÍVEL!", 10 if f % 6 < 3 else 9)
        if self.anim["fade"]:
            pyxel.dither(self.anim["fade"] / 20)
            pyxel.rect(0, 36, LARG, CHAO - 30, 0)
            pyxel.dither(1.0)
            self.texto(110, 80, f"Andar {j.andar}: {A.ANDARES[j.andar]['nome']}", 7)
        self.hud()
        self.painel()

    def hud(self):
        j = self.j
        pyxel.rect(0, 0, LARG, 36, 1)
        pyxel.line(0, 35, LARG, 35, 5)
        self.texto(4, 2, f"{j.nome} · {j.classe} · Nv {j.nivel}", 7)
        self.texto(196, 2, j.titulo_ativo, 6)
        self.texto(4, 13, "Vida", 11); self.barra(30, 16, 80, j.vida / max(1, j.vida_max), 11)
        self.texto(116, 13, "XP", 10); self.barra(132, 16, 80, j.xp / max(1, j.xp_max), 10)
        self.texto(218, 13, f"Ouro {A.fmt_num(j.ouro)}", 10)
        self.texto(4, 24, f"Volta {j.ciclo}", 13)
        for i in range(1, 6):    # a torre em miniatura
            cor = 11 if j.andar > i else 10 if j.andar == i else 5
            pyxel.rect(48 + (i - 1) * 12, 26, 9, 6, cor)
        info = A.ANDARES[j.andar]
        poder = A.poder_contra(j, *A.stats_chefe(j))
        cor_p = 11 if poder >= 1.2 else 10 if poder >= 1 else 8
        self.texto(112, 24, self.caber(info["chefe"], 96), 7)
        self.texto(212, 24, f"Poder {poder:.1f}x".replace(".", ","), cor_p)
        self.texto(270, 24, f"Frag {j.fragmentos}", 14)

    def painel(self):
        j = self.j
        y0 = CHAO + 8
        pyxel.rect(0, y0, LARG, ALT - y0, 0)
        pyxel.line(0, y0, LARG, y0, 5)
        rumo = A._rumo_ao_chefe(j)
        self.texto(4, y0 + 3, "Rumo ao chefe", 13); self.barra(76, y0 + 6, 70, rumo, 6)
        abertos = [c for c in j.contratos if not c["feito"]]
        if abertos:
            c = abertos[0]
            self.texto(154, y0 + 3, self.caber(f"Contrato {c['prog']}/{c['qt']} {c['texto']}", 162), 9)
        linhas = [l for l in self.log if limpo(l)][-6:]
        for i, l in enumerate(linhas):
            self.texto(4, y0 + 15 + i * 11, self.caber(l, LARG - 8), cor_da_linha(l), sombra=False)
        if self.banner and pyxel.frame_count < self.banner_ate:
            pyxel.rect(20, 60, LARG - 40, 18, 1); pyxel.rectb(20, 60, LARG - 40, 18, 10)
            self.texto(28, 64, self.caber(self.banner, LARG - 56), 10)
        if j.escolha_pendente and j.escolha_pendente in A.MISSOES:
            m = A.MISSOES[j.escolha_pendente]
            pyxel.rect(12, 44, LARG - 24, 64, 1); pyxel.rectb(12, 44, LARG - 24, 64, 14)
            resta = max(0, int(j.escolha_prazo - time.time()))
            self.texto(18, 48, self.caber(f"{m['nome']} · {resta}s", LARG - 40), 14)
            self.texto(18, 60, self.caber(m["escolha"]["pergunta"], LARG - 40), 7)
            for i, op in enumerate(m["escolha"]["opcoes"]):
                self.texto(18, 74 + i * 11, self.caber(f"[{i + 1}] {op['texto']}", LARG - 40), 10)
        sair = "[Q] salvar" if NA_WEB else "[Q] salvar e sair"
        rodape = f"[ESPAÇO] {'continuar' if self.pausado else 'pausa'}  [+/-] {VELOCIDADES[self.vel]}s  {sair}".replace(".", ",")
        self.texto(4, ALT - 10, rodape, 5, sombra=False)
        if self.pausado:
            self.texto(140, 90, "PAUSADO", 7 if pyxel.frame_count % 20 < 10 else 13)


if __name__ == "__main__":
    Andante()
