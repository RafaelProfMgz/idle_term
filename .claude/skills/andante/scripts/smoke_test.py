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
    a.TECLA_UNICA = False   # menus de uma tecla: nos testes, usa input()
    a.digitar = lambda *args, **kw: None
    a.limpar = lambda: None
    a.pausa = lambda *args, **kw: None

    resultados = {}
    for classe in ("Guerreiro", "Mago", "Arqueiro"):
        j = a.Jogador("Teste", classe, 1)
        resultados[classe] = (j.vida_max, j.mana_max, list(j.feiticos_aprendidos))
        for f in j.feiticos_aprendidos:
            resultados[classe + ":" + f] = j.usar_magia(f)

    # Saves do teste ficam na pasta temporária
    a.SAVE_MANUAL = os.path.abspath("save_idle.txt")
    a.SAVE_AUTO = os.path.abspath("save_auto_idle.txt")

    j = a.Jogador("Idle", "Guerreiro", 1)
    res = a.auto_play(j, passos=30, velocidade=0, desenhar=False)

    # Idle sem parar: deve atravessar os 5 andares e começar a volta 2
    viajante = {}
    for classe in ("Guerreiro", "Mago", "Arqueiro"):
        t = a.Jogador("Torre", classe, 1)
        r = a.auto_play(t, passos=20000, velocidade=0, desenhar=False)
        viajante[classe] = (t.ciclo, t.andar, t.nivel, r["ticks"], r["chefes"])

    j.nivel, j.andar, j.xp = 4, 2, 37
    j.flags["pescador_falado"] = True
    j.adicionar_item("Escama do Dragão", 3)
    a.salvar_man(j)
    j2 = a.Jogador("Load", "Guerreiro", 1)
    carregou = a.carregar_man(j2)
    a.auto_salvar(j)

    # Progresso offline (2h fora)
    off = a.Jogador("Off", "Arqueiro", 1)
    ganho_off = a.progresso_offline(off, 2 * 3600)

    # Chefe do Andar 5 não pode levar a um Andar 6 inexistente
    fim = a.Jogador("Fim", "Guerreiro", 5)
    a.vencer_chefe(fim)
    a.desenhar_torre(fim)

    # Forja, tralhas, Altar e o save desses campos
    fj = a.Jogador("Forja", "Guerreiro", 1); atq0 = fj.atq; fj.ouro = 10**6
    comprou = a.comprar_forja(fj, "arma")
    fj.adicionar_item("Poção de Vida", 50); venda = a.vender_excesso(fj)
    fj.fragmentos = 10; altar_ok = a.comprar_altar(fj, "ancestral")
    fj.auto_compra = False
    a.gravar_save(fj, a.SAVE_AUTO, "t"); f2 = a.Jogador("x", "Mago", 1); a.ler_save(f2, a.SAVE_AUTO)

    # Todas as telas desenham sem erro
    telas_ok = True
    try:
        r0 = a.novo_res(); a.desenhar_idle(fj, r0, ["teste"], 1.0)
        a.tela_menu(fj); a.mostrar_status(fj); a.dica_do_menu(fj)
        builtins.input = lambda *_: "0"; a.tela_forja(fj); a.tela_altar(fj)
        a.mostrar_offline(fj, int(time.time()) - 3 * 3600)
    except Exception:
        import traceback; telas_ok = traceback.format_exc()
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
    checar("idle roda exatamente os passos pedidos (não para sozinho)", res.get("ticks") == 30, str(res))
    for classe, (ciclo, andar, nivel, ticks, chefes) in viajante.items():
        checar(f"idle {classe}: completa a torre e inicia a volta 2", ciclo >= 2,
               f"volta={ciclo} andar={andar} nivel={nivel} chefes={chefes}")
        print(f"         ({classe}: volta {ciclo}, andar {andar}, nível {nivel}, {chefes} chefes em {ticks} ticks)")
    checar("ANDARES tem chefes e recompensas", all("chefe" in v and "recompensa" in v for v in a.ANDARES.values()))
    checar("save manual criado", os.path.exists(a.SAVE_MANUAL))
    checar("save manual carregado (Andar/Nivel/XP)", carregou and (j2.andar, j2.nivel, j2.xp) == (2, 4, 37),
           f"obtido andar={j2.andar} nivel={j2.nivel} xp={j2.xp}")
    checar("save restaura flags e inventário", j2.flags.get("pescador_falado") and j2.inven.get("Escama do Dragão") == 3)
    checar("auto save criado", os.path.exists(a.SAVE_AUTO))
    checar("progresso offline dá XP e ouro", ganho_off is not None and ganho_off["xp"] > 0 and ganho_off["ouro"] > 0, str(ganho_off))
    checar("vencer Andar 5 inicia volta 2 no Andar 1", (fim.ciclo, fim.andar) == (2, 1), f"volta={fim.ciclo} andar={fim.andar}")
    checar("Forja: compra aumenta ATQ", comprou and fj.atq > atq0, f"atq {atq0} -> {fj.atq}")
    checar("tralhas: excesso de poções vira ouro", venda > 0 and fj.inven["Poção de Vida"] == a.LIMITE_ITEM["Poção de Vida"])
    checar("Altar: compra com fragmentos", altar_ok and fj.altar["ancestral"] == 1)
    checar("save guarda Forja/Altar/fragmentos/auto-compra",
           (f2.forja, f2.altar, f2.fragmentos, f2.auto_compra) == (fj.forja, fj.altar, fj.fragmentos, False))
    checar("telas (idle, menu, status, forja, altar, offline) desenham", telas_ok is True, str(telas_ok))

print("\nRESULTADO:", "OK" if not falhas else f"{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
