#!/usr/bin/env python3
"""Teste rápido e não-interativo do andante.py.

Uso (da raiz do projeto):
    python3 .claude/skills/andante/scripts/smoke_test.py [caminho/andante.py]

Roda numa pasta temporária (não toca nos saves reais), desliga animações
e responde input() automaticamente. Sai com código 1 se algo falhar.
"""
import importlib.util, os, random, sys, tempfile, time, builtins

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
ALVO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "andante.py"))

falhas = []
def checar(nome, cond, detalhe=""):
    print(("  ok   " if cond else "  FALHA ") + nome + (f" — {detalhe}" if detalhe and not cond else ""))
    if not cond:
        falhas.append(nome)

# Sem animação / sem espera / sem input real
time.sleep = lambda *_: None
builtins.input = lambda *_: "0"
random.seed(42)

os.chdir(tempfile.mkdtemp(prefix="andante_smoke_"))
spec = importlib.util.spec_from_file_location("andante", ALVO)
a = importlib.util.module_from_spec(spec)
saida_real = sys.stdout
sys.stdout = open(os.devnull, "w", encoding="utf-8")
try:
    spec.loader.exec_module(a)
    a.digitar = lambda *args, **kw: None
    a.limpar = lambda: None
    a.pausa = lambda *args, **kw: None

    resultados = {}
    for classe in ("Guerreiro", "Mago", "Arqueiro"):
        j = a.Jogador("Teste", classe, 1)
        resultados[classe] = (j.vida_max, j.mana_max, list(j.feiticos_aprendidos))
        for f in j.feiticos_aprendidos:
            resultados[classe + ":" + f] = j.usar_magia(f)

    j = a.Jogador("Idle", "Guerreiro", 1)
    res = a.auto_play(j, passos=30)
    res_chefe = a.auto_play(a.Jogador("Chefe", "Mago", 1), passos=500, ate_chefe=True)

    j.nivel, j.andar, j.xp = 4, 2, 37
    a.salvar_man(j)
    j2 = a.Jogador("Load", "Guerreiro", 1)
    carregou = a.carregar_man(j2)
    a.auto_salvar(j)
    erro = None
except Exception as e:  # noqa: BLE001
    import traceback; erro = traceback.format_exc()
finally:
    sys.stdout.close(); sys.stdout = saida_real

print(f"Smoke test: {ALVO}")
checar("importa e executa sem exceção", erro is None, erro or "")
if erro is None:
    for classe in ("Guerreiro", "Mago", "Arqueiro"):
        vmax, mmax, feit = resultados[classe]
        checar(f"{classe}: vida/mana positivas", vmax > 0 and mmax > 0)
        for f in feit:
            checar(f"{classe}: lança {f}", resultados[classe + ":" + f] is True)
    checar("auto_play retorna dict com 'batalhas'", isinstance(res, dict) and "batalhas" in res)
    checar("auto_play ate_chefe para nos requisitos", res_chefe.get("parou_chefe") is True)
    checar("ANDARES tem chefes e recompensas", all("chefe" in v and "recompensa" in v for v in a.ANDARES.values()))
    checar("save manual criado", os.path.exists(a.SAVE_MANUAL))
    checar("save manual carregado (Andar/Nivel/XP)", carregou and (j2.andar, j2.nivel, j2.xp) == (2, 4, 37),
           f"obtido andar={j2.andar} nivel={j2.nivel} xp={j2.xp}")
    checar("auto save criado", os.path.exists(a.SAVE_AUTO))

print("\nRESULTADO:", "OK" if not falhas else f"{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
