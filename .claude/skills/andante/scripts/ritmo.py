#!/usr/bin/env python3
"""Mede o ritmo do modo idle (1 tick = 1 s): quando chega no nível 2/5, no 1º chefe e quanto dura cada volta na torre.

Uso (da raiz do projeto):  python3 .claude/skills/andante/scripts/ritmo.py
Meta de jogo idle: nível 5 em ~2-3 min, 1ª volta ~25-30 min, cada volta ~1,5x a anterior."""
import importlib.util, sys, io, os, random, tempfile
ALVO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "andante.py"))
os.chdir(tempfile.mkdtemp())
def carrega():
    spec=importlib.util.spec_from_file_location("a",ALVO); a=importlib.util.module_from_spec(spec)
    real=sys.stdout; sys.stdout=io.StringIO(); spec.loader.exec_module(a); sys.stdout=real; a.SAVE_AUTO="x.txt"; return a
def fmt(s): return f"{s/60:.1f}m" if s<3600 else f"{s/3600:.1f}h"
def mede(a, classe="Guerreiro", seed=1, limite=60*60*30):
    random.seed(seed); j=a.Jogador("T",classe,1)
    res={"batalhas":0,"chefes":0,"chefes_tentados":0,"itens":0,"ouro_ganho":0,"xp_ganho":0,"eventos":0,"mortes":0,"ticks":0}
    m={}; nv=1; ult=(1,1); niveis=[]
    for t in range(1,limite):
        a.tick_idle(j,res,[])
        if j.nivel!=nv: nv=j.nivel; niveis.append(t); m.setdefault(f"nv{nv}",t)
        if (j.ciclo,j.andar)!=ult:
            ult=(j.ciclo,j.andar)
            if j.andar==2 and j.ciclo==1: m["chefe1"]=t
            if j.andar==1: m[f"volta{j.ciclo-1}"]=t
            if j.ciclo==6: break
    return m, res
if __name__=="__main__":
    a=carrega()
    for classe in ("Guerreiro","Mago","Arqueiro"):
        m,res=mede(a,classe)
        voltas=[m.get(f"volta{i}") for i in range(1,6)]
        dur=[fmt(v-(voltas[i-1] if i else 0)) if v and (i==0 or voltas[i-1]) else "-" for i,v in enumerate(voltas)]
        print(f"{classe:9} nv2 {m.get('nv2','-')}s | nv5 {fmt(m.get('nv5',0))} | chefe1 {m.get('chefe1','-')}s | voltas: {' '.join(dur)} | mortes {res['mortes']}")
