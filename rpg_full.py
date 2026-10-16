#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPG FULL EXPANSION
- Atributos (Força, Destreza, Inteligência, Vitalidade, Carisma)
- Nível + XP (level up com pontos de atributo)
- Conquistas (achievements) + Títulos com status
- Mapa ASCII no terminal
- Diálogos com escolhas que impactam causa/efeito
- Save estilo GitHub (.txt Markdown) + Auto
- Funciona Windows/Linux sem dependências
"""
import os, sys, time, re, random

SAVE_MANUAL = "save_rpg_full.txt"
SAVE_AUTO = "save_auto_full.txt"

# ---------- Cross-platform ----------
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

# ---------- Conquistas ----------
CONQUISTAS_DEF = {
    "Primeiro Sangue": {"desc":"Derrotou um inimigo pela primeira vez","bonus_ouro":10,"bonus_xp":20,"req_flag":"goblin_derrotado"},
    "Pescador Amigo": {"desc":"Conversa amigável com o pescador","bonus_ouro":15,"bonus_xp":30,"req_flag":"pescador_falado"},
    "Crista Azul": {"desc":"Obteve a Crista do Goblin","bonus_ouro":20,"bonus_xp":25,"req_flag":"crista_pegada"},
    "Portão Aberto": {"desc":"Abriu o Castelo", "bonus_ouro":20,"bonus_xp":30,"req_flag":"portao_aberto"},
    "Leitor de Manuscritos": {"desc":"Leu o Manuscrito Antigo","bonus_ouro":10,"bonus_xp":15,"req_flag":"manuscrito_lido"},
    "Matador de Dragão": {"desc":"Derrotou o Dragão Antigo","bonus_ouro":100,"bonus_xp":100,"req_flag":"dragao_derrotado"},
    "Dono do Porto": {"desc":"Completou todas as missões","bonus_ouro":50,"bonus_xp":50,"req_flags_all":["pescador_falado","dragao_derrotado"]},
    "Diplomata": {"desc":"Fez 3 diálogos positivos","bonus_oro":25,"bonus_xp":25,"req_flag":"dialogo_positivo_3"},
}

class Conquista:
    def __init__(self, nome, info):
        self.nome = nome
        self.desc = info["desc"]
        self.bonus_ouro = info.get("bonus_ouro",0)
        self.bonus_xp = info.get("bonus_xp",0)
        self.concluida = False
        self.req_flag = info.get("req_flag")
        self.req_flags_all = info.get("req_flags_all")

# ---------- Títulos ----------
TITULOS_DEF = [
    {"nome":"Aventurier","req_nivel":1,"status":"Explorador dos mares.","bonus_atq":0,"bonus_def":0},
    {"nome":"Caçador de Sombras","req_nivel":5,"req_flags":["crista_pegada"],"status":"Possui a Crista Azul.","bonus_atq":3,"bonus_def":2},
    {"nome":"Guardião do Rei","req_nivel":8,"req_flags":["portao_aberto"],"status":"Abertura do Castelo conquistada.","bonus_atq":5,"bonus_def":5},
    {"nome":"Matador de Dragões","req_nivel":10,"req_flags":["dragao_derrotado"],"status":"O Dragão caiu.","bonus_atq":8,"bonus_def":8},
    {"nome":"Lenda do Porto","req_nivel":15,"req_flags_all":["dragao_derrotado","pescador_falado"],"status":"Todas as missões completas.","bonus_atq":10,"bonus_def":10},
]

class Titulo:
    def __init__(self, info):
        self.nome = info["nome"]
        self.req_nivel = info.get("req_nivel",99)
        self.req_flags = info.get("req_flags",[])
        self.req_flags_all = info.get("req_flags_all",[])
        self.status = info["status"]
        self.bonus_atq = info.get("bonus_atq",0)
        self.bonus_def = info.get("bonus_def",0)
        self.desbloqueado = False

# ---------- Jogador ----------
class Jogador:
    def __init__(self, nome="Aventurier", classe="Guerreiro"):
        self.nome = nome
        self.classe = classe
        # Atributos (pontos distribuidos)
        self.atributos = {"forca":10,"destreza":10,"inteligencia":10,"vitalidade":10,"carisma":10}
        self.pontos_atributo = 0  # para distribuir
        # Nível / XP
        self.nivel = 1
        self.xp = 0
        self.xp_max = 100
        # Stats derivados (base + atributos) - será recalculado depois de tudo
        self.vida_max = 50 + self.atributos["vitalidade"]*10 + self.nivel*10
        self.vida = self.vida_max
        self.vida_max = self.vida_max
        self.inven = {}
        self.ouro = 0
        # Flags (causa/efeito)
        self.flags = {
            "pescador_falado":False,"goblin_derrotado":False,"crista_pegada":False,
            "portao_aberto":False,"manuscrito_lido":False,"dragao_derrotado":False,
            "dialogo_positivo_3":False,
        }
        self.missao_ativa = None
        self.missao_concluida = False
        self.sala_atual = "Porto"
        # Conquistas
        self.conquistas = {nome: Conquista(nome, info) for nome, info in CONQUISTAS_DEF.items()}
        # Títulos
        self.titulos = [Titulo(t) for t in TITULOS_DEF]
        self.titulo_ativo = "Aventurier"
        # Inventário inicial por classe
        self.adicionar_item("Poção de Vida", 2 if classe=="Mago" else 1 if classe=="Arqueiro" else 1)
        if classe == "Arqueiro": self.ouro += 10
        # Diálogo positivo contador (interno)
        self.dialogo_positivo = 0
        # Finaliza stats
        self.atualizar_titulos()
        self._recalcular_stats()
        self.vida = self.vida_max

    def _recalcular_stats(self):
        a = self.atributos
        # Vida: base 50 + vitalidade*10 + nivel*10
        self.vida_max = 50 + a["vitalidade"]*10 + self.nivel*10
        # Ataque: base 5 + forca*2 + int*0.5 + nivel*2
        self.atq = 5 + a["forca"]*2 + a["inteligencia"]*0.5 + self.nivel*2
        # Defesa: base 3 + destreza*1.5 + nivel
        self.def_ = 3 + a["destreza"]*1.5 + self.nivel
        # Bônus do título ativo
        titulo = next((t for t in self.titulos if t.nome == self.titulo_ativo and t.desbloqueado), None)
        if titulo:
            self.atq += titulo.bonus_atq
            self.def_ += titulo.bonus_def
        # Garantir vida atual não ultrapasse max
        if self.vida > self.vida_max: self.vida = self.vida_max

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
        digitar(f"[⭐ XP] +{qt} XP (Total: {self.xp}/{self.xp_max})")
        if self.xp >= self.xp_max:
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.xp = 0
        self.xp_max = 100 * self.nivel
        self.pontos_atributo += 2  # +2 pontos de atributo ao subir
        digitar(f"[📈 LEVEL UP!] Nível {self.nivel}! Pontos de atributo: +2")
        # Verifica conquistas por nível (não automático, mas pode desbloquear títulos)
        self.atualizar_titulos()

    def distribuir_pontos(self):
        # Menu rápido para distribuir pontos
        if self.pontos_atributo <= 0:
            digitar("Nenhum ponto disponível.")
            return
        digitar(f"Pontos disponíveis: {self.pontos_atributo}")
        while self.pontos_atributo > 0:
            print("Atributos: Força (F), Destreza (D), Int (I), Vitalidade (V), Carisma (C)")
            print(f"Atual: F={self.atributos['forca']} D={self.atributos['destreza']} I={self.atributos['inteligencia']} V={self.atributos['vitalidade']} C={self.atributos['carisma']}")
            a = input("Atributo para +1 (F/D/I/V/C) ou 0 para sair: ").strip().upper()
            if a == "0" or a == "": break
            if a == "F": self.atributos["forca"] += 1
            elif a == "D": self.atributos["destreza"] += 1
            elif a == "I": self.atributos["inteligencia"] += 1
            elif a == "V": self.atributos["vitalidade"] += 1
            elif a == "C": self.atributos["carisma"] += 1
            else: continue
            self.pontos_atributo -= 1
            print(f"Distribuído! Restante: {self.pontos_atributo}")
        self._recalcular_stats()

    def atualizar_titulos(self):
        for t in self.titulos:
            desbloq = True
            if self.nivel < t.req_nivel: desbloq = False
            if t.req_flags:
                for f in t.req_flags:
                    if not self.flags.get(f): desbloq = False
            if t.req_flags_all:
                for f in t.req_flags_all:
                    if not self.flags.get(f): desbloq = False
            if desbloq and not t.desbloqueado:
                t.desbloqueado = True
                digitar(f"[🏆 TÍTULO DESBLOQUEADO] {t.nome}: {t.status}")

    def verificar_conquistas(self, evento):
        # evento pode ser nome da conquista ou flag específica
        for nome, c in self.conquistas.items():
            if c.concluida: continue
            # Verifica por flag específica
            if c.req_flag:
                if self.flags.get(c.req_flag) and evento == c.req_flag:
                    c.concluida = True
                    digitar(f"[🏅 CONQUISTA] {nome}: {c.desc}")
                    self.ouro += c.bonus_ouro
                    self.ganhar_xp(c.bonus_xp)
            # Verifica por flags todas
            if c.req_flags_all:
                if all(self.flags.get(f) for f in c.req_flags_all) and evento == "all":
                    c.concluida = True
                    digitar(f"[🏅 CONQUISTA] {nome}: {c.desc}")
                    self.ouro += c.bonus_ouro
                    self.ganhar_xp(c.bonus_xp)

    def definir_titulo_ativo(self, titulo_nome):
        tit = next((t for t in self.titulos if t.nome == titulo_nome and t.desbloqueado), None)
        if tit:
            self.titulo_ativo = titulo_nome
            self._recalcular_stats()
            digitar(f"Título ativo: {titulo_nome} ({tit.status})")
        else:
            digitar("Título não desbloqueado.")

# ---------- Mapa ASCII ----------
def desenhar_mapa(jogador):
    # Mapa simples com posição atual
    slot = {"Porto":"P","Floresta":"F","Castelo":"C","Caverna":"V","Templo":"T"}
    # Posicionamento aproximado
    mapa = [
        "  +--------+--------+--------+",
        "  |  Porto |Floresta|Castelo |",
        "  +--------+--------+--------+",
        "         |        |         |",
        "         +--Caverna----------+",
    ]
    # Mostrar posição
    pos = jogador.sala_atual
    simbolo = slot.get(pos, "?")
    # Atualiza mapa com [X] na posição atual (simples por texto)
    mapa_texto = "\n".join(mapa)
    # Destaca sala atual
    highlight = {
        "Porto":"[P]", "Floresta":"[F]", "Castelo":"[C]", "Caverna":"[V]"
    }
    digitar("=== 🗺️ MAPA DO REINO ===")
    # Simplificado: lista de salas visitadas
    visitadas = [s for s in ["Porto","Floresta","Castelo","Caverna"] if jogador.flags.get(s.lower().replace("floresta","goblin_derrotado")) or s=="Porto"]
    # Melhor: mostrar diretamente
    print(mapa_texto)
    print()
    print(f"Você está em: [{simbolo}] {pos}")
    print("Salas visitadas/visitáveis:")
    for s in ["Porto","Floresta","Castelo","Caverna"]:
        v = "✅" if (s=="Porto" or (s=="Floresta" and jogador.flags.get("goblin_derrotado")) or (s=="Castelo" and jogador.flags.get("portao_aberto")) or (s=="Caverna" and jogador.flags.get("portao_aberto"))) else "🔒"
        print(f"  {v} {s}")

# ---------- Combate atualizado ----------
def combate(jogador, nome, vida_inimigo, atq_inimigo):
    v_inim = vida_inimigo
    turnos = 0
    while v_inim > 0 and jogador.vida > 0:
        turnos += 1
        limpar()
        digitar(f"⚔️  COMBATE: {nome}")
        digitar(f"Você [{jogador.classe}] Nível {jogador.nivel}: {jogador.vida} HP | Inimigo: {v_inim} HP")
        # Mostrar bônus de título
        if jogador.titulo_ativo:
            tit = next((t for t in jogador.titulos if t.nome == jogador.titulo_ativo), None)
            if tit and tit.desbloqueado:
                digitar(f"Título: {tit.nome} (+{tit.bonus_atq} ATQ / +{tit.bonus_def} DEF)")
        print("[A]tacar  [D]efender  [C]urar (poção)  [I]nventário  [F]ugir  [S]tatus")
        acao = input("Ação: ").strip().upper()
        if acao == "S":
            digitar(f"Atributos: F={jogador.atributos['forca']} D={jogador.atributos['destreza']} I={jogador.atributos['inteligencia']} V={jogador.atributos['vitalidade']} C={jogador.atributos['carisma']}")
            digitar(f"XP: {jogador.xp}/{jogador.xp_max} | Pontos: {jogador.pontos_atributo}")
            pausa()
            continue
        if acao == "A":
            dano = max(3, jogador.atq - 2 + random.randint(-2,2))
            v_inim -= dano
            rec = max(0, atq_inimigo - jogador.def_)
            jogador.vida -= rec
            digitar(f"Você causa {dano} de dano! Inimigo revida {rec}.")
            # Se derrotou
            if v_inim <= 0:
                jogador.ganhar_xp(15)
                # Verifica conquistas por evento de combate
                if evento := ("goblin_derrotado" if nome=="Goblin Sombrio" else ("dragao_derrotado" if "Dragão" in nome else "portao_aberto" if nome=="Guardião Real" else None)):
                    jogador.flags[evento] = True
                    jogador.verificar_conquistas(evento)
        elif acao == "D":
            jogador.def_ += 8
            rec = max(0, atq_inimigo - jogador.def_)
            jogador.vida -= rec
            digitar(f"Defesa reforçada! Sofre {rec}.")
        elif acao == "C":
            if jogador.usar_poção():
                digitar("Poção usada (+HP e regeneração vitalidade).")
            else:
                digitar("Sem poções!")
        elif acao == "I":
            mostrar_inventario(jogador)
            continue
        elif acao == "F":
            digitar("Você foge!")
            if "Goblin" in nome:
                digitar("[⚠️ CONSEQUÊNCIA] O Goblin leva a Crista. Você não abrirá o portão.")
            return False
        else:
            digitar("Ação inválida.")
        pausa()
    if jogador.vida <= 0:
        digitar("GAME OVER.")
        pausa(); return False
    else:
        digitar(f"Vitória! Derrotou {nome}.")
        if nome == "Guardião Real":
            jogador.flags["portao_aberto"] = True
            jogador.verificar_conquistas("portao_aberto")
        elif "Dragão" in nome:
            jogador.flags["dragao_derrotado"] = True
            jogador.verificar_conquistas("dragao_derrotado")
        # Bônus de vitória
        jogador.adicionar_item("Ouro", 10 if "Goblin" not in nome else 5)
        jogador.ganhar_xp(10)
        return True

# ---------- Inventário Visual ----------
def mostrar_inventario(jogador):
    limpar()
    digitar("=== 🎒 INVENTÁRIO ===")
    digitar(f"Classe: {jogador.classe} | Nome: {jogador.nome} | Nível: {jogador.nivel}")
    digitar(f"XP: {jogador.xp}/{jogador.xp_max} | Pontos Attr: {jogador.pontos_atributo} | Ouro: {jogador.ouro}")
    print()
    print("| Item                 | Qtd |")
    print("|----------------------|-----|")
    if jogador.inven:
        for item, qt in sorted(jogador.inven.items()):
            print(f"| {item:<20} | {qt} |")
    else:
        print("| _Vazio_              | - |")
    print()
    # Conquistas visíveis
    digitar("=== 🏅 CONQUISTAS ===")
    for nome, c in sorted(jogador.conquistas.items()):
        status = "✅" if c.concluida else "🔒"
        print(f"{status} {nome}: {c.desc}")
    digitar("=== 🏆 TÍTULOS ===")
    for t in jogador.titulos:
        s = "✅" if t.desbloqueado else "🔒"
        print(f"{s} {t.nome} (Nível {t.req_nivel}) — {t.status}")
    # Título ativo
    print(f"\nTítulo Ativo: [{jogador.titulo_ativo}]")
    # Flags de causa/efeito
    digitar("=== 🏁 FLAGS ===")
    for k,v in sorted(jogador.flags.items()):
        print(f"{'✅' if v else '❌'} {k.replace('_',' ').title()}")
    digitar("=== 🗺️ MAPA ===")
    desenhar_mapa(jogador)
    pausa()

# ---------- Diálogos com Escolhas ----------
def dialogo_porto(jogador):
    limpar()
    digitar("=== 💬 DIÁLOGO — PESCADOR ===")
    digitar('"O mar está escuro, jovem. Há uma maldição sobre a cidade."')
    print("[1] Sou apenas um aventureiro comum.")
    print("[2] Preciso de ajuda para romper a maldição.")
    print("[3] Não tenho tempo para velhos pescadores.")
    es = input("Resposta: ").strip()
    if es == "1":
        digitar('Pescador: "Talvez... mas seja honesto."')
        # Neutro: ganha XP, pescador fala
        jogador.ganhar_xp(5)
        jogador.dialogo_positivo += 1
        # Se já falou antes, não ativa missão; apenas conversa
        if not jogador.flags["pescador_falado"]:
            digitar("Ele te entrega uma Chave do Castelo, mas não a missão completa.")
            jogador.adicionar_item("Chave do Castelo", 1)
        else:
            digitar("Ele te aponta para a floresta.")
    elif es == "2":
        digitar('Pescador: "Então ouça. Há um Manuscrito no cais. E uma Crista perdida. Vá."')
        jogador.flags["pescador_falado"] = True
        jogador.missao_ativa = "O Mar Escuro"
        jogador.adicionar_item("Manuscrito Antigo", 1)
        jogador.adicionar_item("Chave do Castelo", 1)
        jogador.ganhar_xp(15)
        jogador.dialogo_positivo += 1
        jogador.adicionar_item("Poção de Vida", 1)
        digitar("[📜 MISSÃO ATIVADA] 'O Mar Escuro'")
        jogador.verificar_conquistas("pescador_falado")
    elif es == "3":
        digitar('Pescador: "Arrogante... mas a maldição não perdoa ninguém."')
        digitar("[⚠️ CONSEQUÊNCIA] O pescador não te ajuda. Você não recebe a Chave nem a Missão.")
        # Se ainda não falou, bloqueia missão
        if not jogador.flags["pescador_falado"]:
            digitar("Você não poderá acessar o Castelo corretamente sem a Chave do pescador.")
    pausa()

def dialogo_castelo(jogador):
    if not jogador.flags["portao_aberto"]:
        digitar("Não há guardião para dialogar ainda.")
        pausa(); return
    limpar()
    digitar("=== 💬 DIÁLOGO — GUARDIÃO ===")
    if jogador.flags["manuscrito_lido"]:
        digitar('"Ah... você leu o manuscrito. Você sabe o que fazer."')
    else:
        digitar('"Ninguém passa sem a Crista e a Chave, e sem o respeito do Rei."')
    print("[1] Venho por paz, Guardião.")
    print("[2] Sou o escolhido pelo rei.")
    print("[3] Saia da minha frente!")
    es = input("Resposta: ").strip()
    if es == "1":
        digitar("O Guardião assente. Você pode entrar sem combate (se tiver manuscrito).")
        if jogador.flags["manuscrito_lido"]:
            digitar("Com a frase do manuscrito, o Guardião deixa você passar.")
            jogador.ganhar_xp(10)
            jogador.dialogo_positivo += 1
    elif es == "2":
        digitar("O Guardião ri: 'Veremos.' Combate necessário.")
        jogador.ganhar_xp(5)
    elif es == "3":
        digitar("O Guardião fica furioso! Sua defesa é reduzida no combate.")
        jogador.def_ -= 3
        jogador.ganhar_xp(2)
        jogador.dialogo_positivo += 0  # não aumenta
    pausa()

# ---------- Cenas ----------
def cena_porto(jogador):
    limpar()
    digitar("=== PORTO ===")
    digitar("Cidade de pescadores. O ar é salgado.")
    if jogador.flags["pescador_falado"]:
        digitar("O pescador te reconhece. Há uma missão ativa: 'O Mar Escuro'.")
        opcoes = ["1) Ir para Floresta", "2) Diálogo com Pescador", "3) Inventário", "4) Salvar / Menu", "5) Mapa"]
    else:
        opcoes = ["1) Falar com Pescador", "2) Ir para Floresta", "3) Inventário", "4) Salvar / Menu", "5) Mapa"]
    for o in opcoes: print(o)
    es = input("Escolha: ").strip()
    if es == "1":
        if jogador.flags["pescador_falado"]:
            # Se já falou, ir direto (mas pode dialogar novamente pelo op 2)
            jogador.sala_atual = "Floresta"
            cena_floresta(jogador)
        else:
            dialogo_porto(jogador)
            # Se após diálogo ativou missão, ainda pode ir
            jogador.sala_atual = "Porto"
    elif es == "2" and not jogador.flags["pescador_falado"]:
        jogador.sala_atual = "Floresta"
        cena_floresta(jogador)
    elif es == "2" and jogador.flags["pescador_falado"]:
        dialogo_porto(jogador)
    elif es == "3":
        mostrar_inventario(jogador)
    elif es == "4":
        salvar_completo(jogador, SAVE_MANUAL)
        salvar_completo(jogador, SAVE_AUTO, auto=True)
        pausa()
    elif es == "5":
        desenhar_mapa(jogador)
        pausa()
    jogador.sala_atual = "Porto"

def cena_floresta(jogador):
    if jogador.flags["crista_pegada"]:
        limpar()
        digitar("=== FLORESTA ===")
        digitar("A Crista Azul já foi obtida. O Goblin não está.")
        print("[1] Voltar ao Porto\n[2] Ir ao Castelo (se tiver chave)")
        es = input("Escolha: ").strip()
        if es == "2" and jogador.inven.get("Chave do Castelo",0)>0:
            jogador.sala_atual = "Castelo"
            cena_castelo(jogador)
        jogador.sala_atual = "Porto"
        return
    
    limpar()
    digitar("=== FLORESTA SOMBRIA ===")
    if jogador.missao_ativa == "O Mar Escuro":
        digitar("[📜 MISSÃO ATIVA] 'O Mar Escuro'")
    print("[1] Combater Goblin\n[2] Fugir (consequência!)\n[3] Diálogo (se houver)\n[4] Voltar")
    es = input("Escolha: ").strip()
    if es == "1":
        ok = combate(jogador, "Goblin Sombrio", 40, 10)
        if ok:
            jogador.flags["goblin_derrotado"] = True
            jogador.flags["crista_pegada"] = True
            jogador.adicionar_item("Crista Azul", 1)
            jogador.verificar_conquistas("goblin_derrotado")
            digitar("[💎 CONSEQUÊNCIA] Crista obtida! O Castelo poderá ser aberto.")
            pausa()
    elif es == "2":
        digitar("Você foge... O Goblin leva a Crista.")
        digitar("[⚠️ CONSEQUÊNCIA PERMANENTE] Sem Crista, o portão do Castelo NÃO abre.")
        pausa()
    elif es == "3":
        digitar("Não há ninguém para dialogar no meio do mato.")
        pausa()
    jogador.sala_atual = "Porto"

def cena_castelo(jogador):
    limpar()
    digitar("=== CASTELO DO REI ===")
    digitar("Portas de pedra. Há um portão de ferro.")
    tem_chave = jogador.inven.get("Chave do Castelo",0)>0
    tem_crista = jogador.flags["crista_pegada"]
    
    if tem_chave and tem_crista:
        digitar("Com Chave e Crista, o portão se abre.")
    elif tem_chave and not tem_crista:
        digitar("[❌ BLOQUEADO] Você tem a chave, mas falta a Crista Azul (consequência de não derrotar Goblin).")
    elif not tem_chave and tem_crista:
        digitar("Tem a Crista, mas falta a Chave.")
    else:
        digitar("Você não tem Chave nem Crista.")
    
    if tem_chave and tem_crista:
        print("[1] Entrar (combate com Guardião)\n[2] Diálogo com Guardião\n[3] Voltar")
        es = input("Escolha: ").strip()
        if es == "1":
            ok = combate(jogador, "Guardião Real", 60, 12)
            if ok:
                jogador.flags["portao_aberto"] = True
                jogador.adicionar_item("Armadura de Ouro", 1)
                jogador.def_ += 10
                jogador.verificar_conquistas("portao_aberto")
                digitar("[👑 CONSEQUÊNCIA] O Rei abre a Caverna.")
                if jogador.flags["pescador_falado"] and not jogador.flags["dragao_derrotado"]:
                    jogador.missao_ativa = "O Mar Escuro"
                pausa()
        elif es == "2":
            dialogo_castelo(jogador)
            # Se diálogo bom e já leu manuscrito, pode evitar combate? Já tratamos no diálogo.
    else:
        print("[1] Voltar")
        input("Escolha: ")
    jogador.sala_atual = "Porto"

def cena_caverna(jogador):
    limpar()
    digitar("=== CAVERNA DO DRAGÃO ===")
    if not jogador.flags["portao_aberto"]:
        digitar("A neblina bloqueia. Sem passar pelo Castelo, não pode entrar.")
        digitar("[⚠️ CONSEQUÊNCIA] A missão 'O Mar Escuro' exige completar o Castelo primeiro.")
        pausa(); jogador.sala_atual = "Porto"; return
    if jogador.flags["dragao_derrotado"]:
        digitar("A Caverna está vazia. O Dragão foi derrotado.")
        pausa(); jogador.sala_atual = "Porto"; return
    
    digitar("Calor intenso. O Dragão dorme sobre ouro.")
    if jogador.missao_ativa == "O Mar Escuro":
        digitar("[📜 MISSÃO] Derrote o Dragão.")
    print("[1] Combater Dragão\n[2] Voltar")
    es = input("Escolha: ").strip()
    if es == "1":
        if jogador.flags["manuscrito_lido"]:
            digitar("[📖 CONSEQUÊNCIA] A frase do Manuscrito faz o Dragão hesitar!")
            jogador.def_ += 5
        ok = combate(jogador, "Dragão Antigo", 120, 20)
        if ok:
            jogador.flags["dragao_derrotado"] = True
            jogador.missao_concluida = True
            jogador.adicionar_item("Ouro do Dragão", 1)
            jogador.ganhar_xp(100)
            jogador.verificar_conquistas("dragao_derrotado")
            digitar("[👑 VITÓRIA LEGENDÁRIA] O reino está salvo!")
            pausa()
    jogador.sala_atual = "Porto"

# ---------- Save / Load ----------
def salvar_completo(jogador, arquivo=SAVE_MANUAL, auto=False):
    titulo = f"# RPG Full Save - Jogador: {jogador.nome}"
    if auto: titulo += " (AUTO)"
    linhas = [titulo, ""]
    linhas.append("## 📊 Stats + Nível")
    linhas.append("")
    linhas.append("| Atributo | Valor |")
    linhas.append("|----------|-------|")
    linhas.append(f"| Nome     | {jogador.nome} |")
    linhas.append(f"| Classe   | {jogador.classe} |")
    linhas.append(f"| Nível    | {jogador.nivel} |")
    linhas.append(f"| XP       | {jogador.xp} / {jogador.xp_max} |")
    linhas.append(f"| Pontos   | {jogador.pontos_atributo} |")
    linhas.append(f"| Vida     | {jogador.vida} / {jogador.vida_max} |")
    linhas.append(f"| Ataque   | {jogador.atq} |")
    linhas.append(f"| Defesa   | {jogador.def_} |")
    linhas.append(f"| Ouro     | {jogador.ouro} 🪙 |")
    linhas.append("")
    # Atributos
    linhas.append("## 🧬 Atributos")
    linhas.append("")
    for k,v in sorted(jogador.atributos.items()):
        linhas.append(f"- {k.title()}: {v}")
    linhas.append("")
    linhas.append("## 🏁 Missão")
    linhas.append(f"- Ativa: `{jogador.missao_ativa or 'Nenhuma'}`")
    linhas.append(f"- Concluída: {'✅' if jogador.missao_concluida else '❌'}")
    linhas.append("")
    linhas.append("## 🏅 Conquistas")
    for nome,c in sorted(jogador.conquistas.items()):
        linhas.append(f"- [{'x' if c.concluida else ' '}] {nome}: {c.desc}")
    linhas.append("")
    linhas.append("## 🏆 Títulos Disponíveis")
    for t in jogador.titulos:
        s = "✅" if t.desbloqueado else "🔒"
        linhas.append(f"- {s} {t.nome} (Nível {t.req_nivel}) — Status: {t.status}")
    linhas.append(f"- Título Ativo: `{jogador.titulo_ativo}`")
    linhas.append("")
    linhas.append("## 🎒 Inventário")
    if jogador.inven:
        for item, qt in sorted(jogador.inven.items()):
            linhas.append(f"- [x] {item} (x{qt})")
    else:
        linhas.append("_Vazio..._")
    linhas.append("")
    linhas.append("## 🏁 Flags (Causa & Consequência)")
    for k,v in sorted(jogador.flags.items()):
        linhas.append(f"- [{'x' if v else ' '}] `{k}`")
    linhas.append("")
    linhas.append("## 🗺️ Sala Atual")
    linhas.append(jogador.sala_atual)
    linhas.append("")
    linhas.append("---")
    linhas.append("*Arquivo gerado pelo RPG Full. Pode editar diretamente (como README do GitHub).*")
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas)+"\n")
    digitar(f"[💾 SAVE] '{arquivo}' atualizado.")

def carregar_completo(jogador, arquivo=SAVE_MANUAL):
    if not os.path.exists(arquivo): return False
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            texto = f.read()
        # Nome
        m = re.search(r"# RPG Full Save - Jogador: (.+?)(?: \(AUTO\))?", texto)
        if m: jogador.nome = m.group(1).strip()
        # Classe (não salva diretamente, mas pode ser inferido; vamos ignorar para simplificar e usar o atual)
        # Nível
        m = re.search(r"\| Nível\s*\| ([0-9]+) \|", texto)
        if m: jogador.nivel = int(m.group(1))
        # XP
        m = re.search(r"\| XP\s*\| ([0-9]+) / ([0-9]+) \|", texto)
        if m: jogador.xp = int(m.group(1)); jogador.xp_max = int(m.group(2))
        # Pontos
        m = re.search(r"\| Pontos\s*\| ([0-9]+) \|", texto)
        if m: jogador.pontos_atributo = int(m.group(1))
        # Vida
        m = re.search(r"\| Vida\s*\| ([0-9]+) / ([0-9]+) \|", texto)
        if m: jogador.vida = int(m.group(1)); jogador.vida_max = int(m.group(2))
        # Stats
        for estat in ["Ataque","Defesa","Ouro"]:
            p = re.search(rf"\| {estat}\s*\| ([0-9]+).*?\|", texto)
            # simplificado: ignoramos para recalcular depois
        # Atributos
        for attr in ["Força","Destreza","Inteligencia","Vitalidade","Carisma"]:
            pat = re.search(rf"- {attr}: ([0-9]+)", texto)
            if pat:
                k = attr.lower()
                # Mapeamento simples
                mapa = {"força":"forca","destreza":"destreza","inteligencia":"inteligencia","vitalidade":"vitalidade","carisma":"carisma"}
                jogador.atributos[mapa[k]] = int(pat.group(1))
        # Inventário
        jogador.inven = {}
        for item_match in re.finditer(r"- \[x\] (.+?) \(x([0-9]+)\)", texto):
            jogador.inven[item_match.group(1).strip()] = int(item_match.group(2))
        # Missão
        m = re.search(r"- Ativa: `(.+?)`", texto)
        if m: val = m.group(1).strip(); jogador.missao_ativa = val if val != "Nenhuma" else None
        m = re.search(r"- Concluída: (✅|❌)", texto)
        if m: jogador.missao_concluida = (m.group(1)=="✅")
        # Conquistas
        for nome_pronto in jogador.conquistas:
            if re.search(rf"- \[x\] {re.escape(nome_pronto)}", texto):
                jogador.conquistas[nome_pronto].concluida = True
        # Títulos
        for t in jogador.titulos:
            if re.search(rf"- .* {re.escape(t.nome)} .* ✅", texto):
                t.desbloqueado = True
        # Título ativo
        m = re.search(r"- Título Ativo: `(.*?)`", texto)
        if m: jogador.titulo_ativo = m.group(1)
        # Flags
        for flag_match in re.finditer(r"- \[([x ])\] `(.+?)`", texto):
            k = flag_match.group(2).strip()
            v = (flag_match.group(1)=="x")
            if k in jogador.flags: jogador.flags[k] = v
        # Sala atual
        m = re.search(r"## 🗺️ Sala Atual\n(.+?)\n", texto)
        if m: jogador.sala_atual = m.group(1).strip()
        jogador._recalcular_stats()
        # Restaurar vida se necessário (não sobrescrever por padrão; mas garantir)
        digitar(f"[📂 LOAD] '{arquivo}' carregado! Nível {jogador.nivel}")
        return True
    except Exception as e:
        digitar(f"Erro no load: {e}")
        return False

# ---------- Menu ----------
def criar_personagem():
    digitar("=== CRIAR PERSONAGEM ===")
    nome = input("Seu nome: ").strip() or "Aventurier"
    print("[G] Guerreiro (força/defesa)\n[M] Mago (inteligência/ataque)\n[A] Arqueiro (equilibrado/ouro)")
    c = input("Classe: ").strip().upper()
    classe = "Mago" if c=="M" else "Arqueiro" if c=="A" else "Guerreiro"
    j = Jogador(nome, classe)
    digitar(f"Bem-vindo, {nome} ({classe})! Nível {j.nivel}.")
    return j

def menu_principal():
    j = None
    if os.path.exists(SAVE_MANUAL) or os.path.exists(SAVE_AUTO):
        resp = input("Save encontrado. Manual (M), Auto (A) ou Novo (N)? ").strip().upper()
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
        digitar("=== RPG FULL EXPANSION ===")
        digitar(f"{j.nome} | {j.classe} | Nível {j.nivel} | XP {j.xp}/{j.xp_max}")
        digitar(f"Vida {j.vida}/{j.vida_max} | ATQ {j.atq} | DEF {j.def_} | Ouro {j.ouro}")
        digitar(f"Título Ativo: [{j.titulo_ativo}] | Missão: {j.missao_ativa or 'Nenhuma'}")
        print()
        print("[1] Explorar Mundo")
        print("[2] Inventário / Atributos / Mapa")
        print("[3] Distribuir Pontos de Atributo")
        print("[4] Salvar Manual")
        print("[5] Salvar Automático")
        print("[6] Carregar Save")
        print("[7] Sair")
        op = input("Opção: ").strip()
        if op == "1":
            j.sala_atual = "Porto"
            cena_porto(j)
        elif op == "2":
            mostrar_inventario(j)
        elif op == "3":
            j.distribuir_pontos()
            pausa()
        elif op == "4":
            salvar_completo(j, SAVE_MANUAL)
            pausa()
        elif op == "5":
            salvar_completo(j, SAVE_AUTO, auto=True)
            pausa()
        elif op == "6":
            resp = input("Manual (M) / Auto (A)? ").strip().upper()
            arquivo = SAVE_MANUAL if resp=="M" else SAVE_AUTO
            temp = Jogador("Temp")
            if carregar_completo(temp, arquivo):
                j = temp
            pausa()
        elif op == "7":
            salvar_completo(j, SAVE_AUTO, auto=True)
            digitar("Salvo automático. Até a próxima!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\nJogo encerrado.")
