#!/usr/bin/env python3
"""Regressão: um teste por bug já corrigido (lista em docs/DOCUMENTACAO.md).

Uso (da raiz do projeto):  python3 .claude/skills/andante/scripts/regressao.py
Roda em pasta temporária, sem tocar nos saves. Sai com código 1 se algo voltar a quebrar."""
import importlib.util, os, sys, io, time, builtins, random, tempfile
time.sleep = lambda *_: None
ALVO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "andante.py"))
os.chdir(tempfile.mkdtemp())
spec = importlib.util.spec_from_file_location("a", ALVO); a = importlib.util.module_from_spec(spec)
real = sys.stdout; sys.stdout = io.StringIO(); spec.loader.exec_module(a)
a.limpar = lambda: None; a.pausa = lambda *x, **k: None
a.SAVE_MANUAL = os.path.abspath("m.txt"); a.SAVE_AUTO = os.path.abspath("au.txt")
random.seed(3)
R = []
def item(nome, fn):
    fila = []
    def inp(p=""):
        if not fila: raise EOFError(p)
        return fila.pop(0)
    builtins.input = inp
    try:
        ok, det = fn(fila)
    except Exception as e:
        ok, det = False, f"{type(e).__name__}: {e}"
    R.append(("OK  " if ok else "FALHA") + f"  {nome}" + (f"  — {det}" if det else ""))

def andar6(f):
    j = a.Jogador("x", "Guerreiro", 5); j.nivel = 10; j.flags["dragao_derrotado"] = True
    j.atributos["forca"] = 300; j._recalcular(); j.vida = j.vida_max
    f += ["1"] + ["A"] * 40
    a.cena_chefe(j); a.desenhar_torre(j)
    return j.andar in range(1, 6), f"andar={j.andar} volta={j.ciclo}"
item("Andar 5 → não existe Andar 6", andar6)

def save_porto(f):
    j = a.Jogador("x", "Mago", 1); f += ["6"]; a.cena_porto(j) if hasattr(a, "cena_porto") else a.cena_explorar(j)
    k = a.Jogador("y", "Guerreiro", 1); a.carregar_man(k)
    return k.classe == "Mago", ""
item("Save da opção 6 do Porto carrega", save_porto)

def dobro(f):
    j = a.Jogador("x", "Guerreiro", 2); j.nivel = 3; j.flags["crista_pegada"] = True
    j.atributos["forca"] = 300; j._recalcular(); j.vida = j.vida_max
    f += ["1"] + ["A"] * 40; a.cena_chefe(j)
    return j.andar == 3, f"andar={j.andar}"
item("Chefe pelo menu 2 sobe 1 andar só", dobro)

def manual_completo(f):
    """Joga a torre só no modo manual: explorar (diálogos) + chefe."""
    j = a.Jogador("x", "Guerreiro", 1); j.atributos["forca"] = 400; j.atributos["vitalidade"] = 200; j._recalcular(); j.vida = j.vida_max
    explorar = getattr(a, "cena_explorar", None) or a.cena_porto
    for _ in range(5):
        j.nivel = max(j.nivel, a.nivel_requerido(j)); j._recalcular(); j.vida = j.vida_max
        f[:] = ["1", "1", "1"]          # explorar → falar (com escolha 1)
        try: explorar(j)
        except EOFError: pass
        andar = j.andar
        j.nivel = max(j.nivel, a.nivel_requerido(j)); j._recalcular(); j.vida = j.vida_max
        f[:] = ["1"] + ["A"] * 60
        try: a.cena_chefe(j)
        except EOFError: pass
        if j.andar == andar and j.ciclo == 1:
            return False, f"travou no andar {andar}, flags={ {k:v for k,v in j.flags.items() if v} }"
    return j.ciclo == 2, f"volta={j.ciclo} andar={j.andar}"
item("Modo manual atravessa a torre (flags ativáveis)", manual_completo)

def goblin(f):
    j = a.Jogador("x", "Guerreiro", 1); j.atributos["forca"] = 300; j._recalcular()
    f += ["2"] + ["A"] * 20
    (getattr(a, "cena_explorar", None) or a.cena_porto)(j)
    return j.andar == 1, f"andar={j.andar}"
item("Monstro da Floresta não sobe de andar", goblin)

def fogo(f):
    j = a.Jogador("x", "Mago", 1); buf = io.StringIO(); sys.stdout = buf
    f += ["M", "Bola de Fogo", "F"]
    try: a.combate(j, "Alvo", 500, 1)
    finally: sys.stdout = io.StringIO()
    hp = [l for l in buf.getvalue().splitlines() if "Inimigo:" in l]
    return len(hp) >= 2 and hp[0] != hp[1].replace(f"Mana: {j.mana}", "x") and "500 HP" not in hp[1], " | ".join(hp)
item("Bola de Fogo tira vida do inimigo", fogo)

def buffs(f):
    j = a.Jogador("x", "Guerreiro", 1); atq0, def0 = j.atq, j.def_
    j.usar_magia("Escudo Arcano"); f += ["D", "D", "D", "F"]; a.combate(j, "Alvo", 500, 1)
    k = a.Jogador("y", "Guerreiro", 1); k.atributos["forca"] = 15; k._desbloquear_passivas(); k._recalcular(); base = k.atq
    for _ in range(10): k.aplicar_passivas()
    return (j.atq, j.def_) == (atq0, def0) and k.atq == base, f"escudo/defender def {def0}->{j.def_}; passiva atq {base}->{k.atq}"
item("Buffs/Defender/passivas não acumulam para sempre", buffs)

def mana(f):
    j = a.Jogador("x", "Mago", 1); j.mana = 0
    f += ["D", "D", "D", "F"]; a.combate(j, "Alvo", 500, 1)
    return j.mana > 0, f"mana após 3 turnos: {j.mana}"
item("Mana regenera no combate manual", mana)

def classes(f):
    s = {c: (a.Jogador("x", c, 1).vida_max, a.Jogador("x", c, 1).atq, a.Jogador("x", c, 1).def_, a.Jogador("x", c, 1).mana_max) for c in ("Guerreiro", "Mago", "Arqueiro")}
    return len(set(s.values())) == 3, str(s)
item("Classes têm atributos diferentes", classes)

def distribuir(f):
    j = a.Jogador("x", "Guerreiro", 1); j.atributos["forca"] = 14; j.pontos_atributo = 1
    f += ["F"]; j.distribuir_pontos()
    return "Fortalecimento" in j.passivas, f"passivas={j.passivas}"
item("distribuir_pontos desbloqueia passiva na hora", distribuir)

def mestre_teleporte(f):
    j = a.Jogador("x", "Guerreiro", 1); j.passivas = ["Mestre do Andar"]; base = max(1, a.xp_para_nivel(1) // 4); j.ganhar_xp(base, silencioso=True)
    xp_mestre = j.xp
    k = a.Jogador("y", "Guerreiro", 1); k.passivas = ["Teleporte Andar"]; k.flags["pescador_falado"] = True; k.vida = int(k.vida_max * 0.6)
    k.atributos["forca"] = 300; k._recalcular(); k.vida = int(k.vida_max * 0.6)
    res = {"batalhas":0,"chefes":0,"chefes_tentados":0,"itens":0,"ouro_ganho":0,"xp_ganho":0,"eventos":0,"mortes":0,"ticks":0}
    a.tick_idle(k, res, [])
    return xp_mestre > base and res["chefes_tentados"] == 1, f"xp com Mestre={xp_mestre}; Teleporte enfrentou chefe com 60% vida: {res['chefes_tentados']==1}"
item("Passivas Mestre do Andar / Teleporte Andar têm efeito", mestre_teleporte)

def conquistas(f):
    tem = hasattr(a, "CONQUISTAS_DEF") and hasattr(a, "TITULOS_DEF")
    if not tem: return False, "CONQUISTAS_DEF/TITULOS_DEF não existem"
    j = a.Jogador("x", "Guerreiro", 1)
    a.auto_play(j, passos=4000, velocidade=0, desenhar=False)
    feitas = [c for c, v in j.conquistas.items() if v]
    a.gravar_save(j, a.SAVE_AUTO, "t"); k = a.Jogador("y", "Guerreiro", 1); a.ler_save(k, a.SAVE_AUTO)
    return len(a.CONQUISTAS_DEF) == 8 and len(feitas) >= 5 and k.conquistas == j.conquistas and k.titulo_ativo == j.titulo_ativo, \
        f"{len(feitas)}/8 conquistas, título '{j.titulo_ativo}', save ok={k.conquistas == j.conquistas}"
item("Conquistas (8) e títulos com bônus existem e são salvos", conquistas)

def explorar(f):
    exp = getattr(a, "cena_explorar", None)
    if not exp: return False, "Explorar sempre abre cena_porto"
    j = a.Jogador("x", "Guerreiro", 3); buf = io.StringIO(); sys.stdout = buf
    f += ["0"]
    try: exp(j)
    except EOFError: pass
    finally: sys.stdout = io.StringIO()
    return "CAVERNA" in buf.getvalue().upper(), ""
item("Explorar mostra a cena do andar atual", explorar)

def idle_ok(f):
    res = a.auto_play(a.Jogador("x", "Mago", 1), passos=6000, velocidade=0, desenhar=False)
    return res["chefes"] >= 5 and res["ticks"] == 6000, str({k: res[k] for k in ("ticks", "chefes", "mortes")})
item("Idle: não para sozinho e vence a torre", idle_ok)

sys.stdout = real
print("\n".join(R))
print(f"\n{sum(r.startswith('OK') for r in R)}/{len(R)} OK")
