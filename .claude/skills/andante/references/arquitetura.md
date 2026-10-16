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

## 3. Modo Idle
- `LeitorTecla` — context manager; `ler()` devolve a tecla ou `None` sem travar (msvcrt / termios+select)
- Constantes: `VELOCIDADES`, `AUTO_SALVAR_A_CADA`, `OFFLINE_MAX_MIN`, `OFFLINE_EFICIENCIA`, `RITMO_XP`, `NIVEIS_POR_VOLTA`; curva de XP em `xp_para_nivel(n)` = 35·n^2,7
- `EVENTOS_AUTO` — `(tipo, peso, objeto)`: Batalha 0.4, Item 0.2, Ouro 0.2, Diálogo 0.1, Trabalho 0.1
- `nivel_requerido(j)` = `req_nivel + 10*(ciclo-1)`; `requisitos_ok(j)`
- `luta_auto(j, vida, atq)` → `(venceu, dano)` — luta sem input, usa Bola de Fogo e poções
- `tick_idle(j, res, log)` — um passo: regen, auto-distribuir pontos, chefe, evento de história, evento aleatório
- `desenhar_idle(...)` — painel redesenhado com `[H[J`
- `auto_play(j, passos=None, velocidade=1.0, desenhar=True)` → `res` (`ticks, batalhas, chefes, chefes_tentados, itens, ouro_ganho, xp_ganho, eventos, mortes`). Testes: `velocidade=0, desenhar=False`.
- `progresso_offline(j, segundos)` → `(minutos, xp, ouro, niveis)` ou `None`

## 4. Magia
- `FEITICOS` — `{nome: {custo_mana, dano|cura|def_bonus|atq_bonus, duracao, mana_regen, desc}}`
- Efeitos aplicados em `Jogador.usar_magia()` por `if/elif` no nome — feitiço novo precisa de ramo novo.

## 5. Classe `Jogador`
- Estado: `nome, classe, idade, ciclo (volta), andar, nivel, xp, xp_max, atributos{forca,destreza,inteligencia,vitalidade,carisma}, pontos_atributo, inven{item:qt}, ouro, flags{}, missao_ativa, sala_atual, mana, mana_max, feiticos_aprendidos, escudo_ativo, impulso_ativo, conquistas, titulo_ativo, passivas[]`
- Feitiços iniciais por classe em `FEITICOS_CLASSE`
- Classes: Guerreiro (120 HP, Bola de Fogo + Escudo Arcano), Mago (80 HP, +30 mana, Bola de Fogo + Cura + Restauração, 2 poções), Arqueiro (100 HP, +10 ouro, Bola de Fogo + Impulso)
- `_recalcular()` — fórmulas:
  - `vida_max = 50 + vit*10 + nivel*10 + andar*5`
  - `atq = 5 + for*2 + int*0.5 + nivel*2 + andar*2`
  - `def_ = 3 + des*1.5 + nivel + andar`
  - `mana_max = 20 + int*10 + nivel*5 + andar*3`
  - + `CLASSES[classe]` (vida/atq/def/mana), + `PASSIVAS_BONUS`, + bônus do título
- `_desbloquear_passivas(silencioso)` — Ataque Duplo (nv5), Esquiva Rápida (nv3 + des15), Regeneração (vit15), Mestre do Andar (nv8), Teleporte Andar (nv10), Visão Noturna (car15), Invocação Rápida (int15), Fortalecimento (for15)
- Bônus de classe em `CLASSES`; bônus fixos de passivas em `PASSIVAS_BONUS`; título ativo em `TITULOS_DEF` — tudo somado em `_recalcular()` (idempotente, não acumula)
- `aplicar_passivas()` — só efeitos por turno (Regeneração, Invocação Rápida)
- `dialogo_bom()` — conta conversas positivas (3 → `dialogo_positivo_3`)
- `usar_magia()` — Bola de Fogo guarda `ultimo_dano` (o combate aplica); Escudo/Impulso só ligam contadores
- `ganhar_xp(qt, silencioso)` sobe vários níveis de uma vez → `subir_nivel()` (xp_max = `xp_para_nivel(nivel)`, +2 pontos, restaura vida/mana)
- `escala()` = 1 + 0.5*(ciclo-1); `aplicar_flags_de_progresso()` marca flags dos chefes já passados
- `usar_poção()`, `adicionar_item()`, `distribuir_pontos()`

## 6. Andares
- `ANDARES = {n: {nome, chefe, req_nivel, req_flag, salas, recompensa}}`
- `CHEFE_FLAGS` (flags ganhas ao vencer cada chefe), `HISTORIA` (eventos que ativam flags no idle), `MONSTROS`, `FALAS_IDLE`
- `stats_chefe(j)` → `(vida, atq)` escalado por `j.escala()`; `vencer_chefe(j)` → recompensa, flags, `andar+1` ou nova volta (Andar 5)

| # | Nome | Chefe | Nível | Flag | Recompensa |
|---|---|---|---|---|---|
| 1 | Porto & Floresta | Goblin Sombrio | 1 | pescador_falado | Crista do Goblin |
| 2 | Castelo do Rei | Guardião Real | 3 | crista_pegada | Coroa do Guardião |
| 3 | Caverna do Dragão | Dragão Antigo | 5 | portao_aberto | Escama do Dragão |
| 4 | Templo Antigo | Cumulador | 7 | manuscrito_lido | Relíquia Antiga |
| 5 | Abismo | Rei das Sombras | 10 | dragao_derrotado | Cristal da Sombra |

- `desenhar_torre(jogador)` — torre vertical 5→1 com status

## 7. Combate
- `combate(jogador, nome, vida_inimigo, atq_inimigo)` → `True` (vitória) / `False` (fuga/derrota). Mana regenera por turno; Escudo/Impulso/Defender valem só no turno.

## 7b. Conquistas / Títulos
- `CONQUISTAS_DEF` (8, por flags ou volta), `TITULOS_DEF` (5, conquista + nível)
- `checar_conquistas(j)` → linhas; chamado no menu e a cada tick do idle; escolhe o melhor título
- Ações: A D C M S I F
- Vencer o chefe do andar atual dentro de `combate()` chama `vencer_chefe()` (único lugar que avança andar).

## 8. Cenas
- `CENAS` — título/descrição/NPC/sala de cada andar; `cena_explorar(jogador)` — menu 1-7 da cena do andar atual
- Diálogos: `dialogo_pescador()` (Andar 1), `dialogo_guardiao()` (Andar 2 — Manuscrito deixa passar sem lutar via `vencer_chefe()`), `ler_manuscrito()` (Andar 4 → `manuscrito_lido`)
- `mostrar_status(jogador)` — status, título, conquistas, inventário e torre
- `cena_chefe(jogador)` — checa requisitos; chefe tem `vida = 40 + andar*30`, `atq = 10 + andar*5`

## 9. Save / Load
`texto_save`, `gravar_save`, `ler_save` (único parser), `auto_salvar`, `salvar_man`, `carregar_man`, `mostrar_offline`. Ver `save.md`.

## 10. Menu
- `menu()` — se há auto save, pergunta "Continuar?" e aplica progresso offline; senão `criar_personagem()`. Loop 1-9, `auto_salvar()` a cada volta.

## Problemas conhecidos
Lista completa e atualizada: seção "Problemas encontrados na revisão" do `docs/DOCUMENTACAO.md`. Ao corrigir um item, marque `[x]` lá.
