# Arquitetura do andante.py

Mapa do arquivo por seção (procure pelos comentários `# ---------- ... ----------`).

## 1. Interface visual (topo do arquivo)
- Cores ANSI: `BR RD GN YW BL MG CY WT RESET DIM BOLD`
- `logo_ascii()`, `borda_titulo()`, `linha_sep()`, `destaque()`, `dim_texto()`, `info_box()`
- `animar_batalha(jogador, inimigo, delay)` — slider lateral; usa `time.sleep` (lento: ~13×delay)
- `renderizar_personagem(jogador)` — boneco ASCII que muda conforme itens do inventário

## 2. Utilidades
- `limpar()` — `cls`/`clear` conforme `os.name`
- `pausa(msg)` — `input()`
- `digitar(texto, delay=0.012)` — efeito máquina de escrever; use para narrativa

## 3. Auto Play
- `EVENTOS_AUTO` — lista `(tipo, peso, objeto)`: Batalha 0.4, Item 0.2, Ouro 0.2, Diálogo 0.1, Trabalho 0.1
- `auto_play(jogador, passos=25, ate_chefe=False, infinito=False)` → dict `res`
  (`batalhas, itens, ouro_ganho, xp_ganho, eventos, morte, chefe_tentado, parou_chefe`)
- Regenera +2 de vida por passo; se morrer, revive com 50%.
- Observação: no menu, modo `C` usa `passos=20` também — então para em 20 passos mesmo sem chegar ao chefe.

## 4. Magia
- `FEITICOS` — `{nome: {custo_mana, dano|cura|def_bonus|atq_bonus, duracao, mana_regen, desc}}`
- Efeitos aplicados em `Jogador.usar_magia()` por `if/elif` no nome — feitiço novo precisa de ramo novo.

## 5. Classe `Jogador`
- Estado: `nome, classe, idade, andar, nivel, xp, xp_max, atributos{forca,destreza,inteligencia,vitalidade,carisma}, pontos_atributo, inven{item:qt}, ouro, flags{}, missao_ativa, sala_atual, mana, mana_max, feiticos_aprendidos, escudo_ativo, impulso_ativo, conquistas, titulo_ativo, passivas[]`
- Classes: Guerreiro (120 HP, Bola de Fogo + Escudo Arcano), Mago (80 HP, +30 mana, Bola de Fogo + Cura + Restauração, 2 poções), Arqueiro (100 HP, +10 ouro, Bola de Fogo + Impulso)
- `_recalcular()` — fórmulas:
  - `vida_max = 50 + vit*10 + nivel*10 + andar*5`
  - `atq = 5 + for*2 + int*0.5 + nivel*2 + andar*2`
  - `def_ = 3 + des*1.5 + nivel + andar`
  - `mana_max = 20 + int*10 + nivel*5 + andar*3`
  - Atenção: sobrescreve os HP/atq iniciais da classe.
- `_desbloquear_passivas()` — Ataque Duplo (nv5), Esquiva Rápida (nv3 + des15), Regeneração (vit15), Mestre do Andar (nv8), Teleporte Andar (nv10), Visão Noturna (car15), Invocação Rápida (int15), Fortalecimento (for15)
- `aplicar_passivas()` — chamado todo turno de combate. Bônus de atq/def **acumulam** a cada turno (não são resetados).
- `ganhar_xp()` → `subir_nivel()` (xp_max = 100*nivel, +2 pontos)
- `usar_poção()`, `adicionar_item()`, `distribuir_pontos()`

## 6. Andares
- `ANDARES = {n: {nome, chefe, req_nivel, req_flag, salas, recompensa}}`

| # | Nome | Chefe | Nível | Flag | Recompensa |
|---|---|---|---|---|---|
| 1 | Porto & Floresta | Goblin Sombrio | 1 | pescador_falado | Crista do Goblin |
| 2 | Castelo do Rei | Guardião Real | 3 | crista_pegada | Coroa do Guardião |
| 3 | Caverna do Dragão | Dragão Antigo | 5 | portao_aberto | Escama do Dragão |
| 4 | Templo Antigo | Cumulador | 7 | manuscrito_lido | Relíquia Antiga |
| 5 | Abismo | Rei das Sombras | 10 | dragao_derrotado | Cristal da Sombra |

- `desenhar_torre(jogador)` — torre vertical 5→1 com status

## 7. Combate
- `combate(jogador, nome, vida_inimigo, atq_inimigo)` → `True` (vitória) / `False` (fuga/derrota)
- Ações: A D C M S I F
- Vencer o chefe do andar atual dentro de `combate()` já dá a recompensa e faz `andar += 1`; `cena_chefe()` faz `andar += 1` **de novo** — ver "Problemas conhecidos".

## 8. Cenas
- `cena_porto(jogador)` — menu 1-7 (Pescador, Floresta, Auto Play, Magia, Status, Salvar, Voltar)
- `cena_chefe(jogador)` — checa requisitos; chefe tem `vida = 40 + andar*30`, `atq = 10 + andar*5`

## 9. Save / Load
Ver `save.md`.

## 10. Menu
- `menu()` — cria personagem, auto-carrega `save_auto_idle.txt`, oferece save manual, loop 1-9. Chama `auto_salvar()` a cada volta.

## Problemas conhecidos
Lista completa e atualizada: seção "Problemas encontrados na revisão" do `DOCUMENTACAO.md` na raiz. Ao corrigir um item, marque `[x]` lá.
