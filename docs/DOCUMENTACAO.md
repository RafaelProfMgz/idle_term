# DOCUMENTACAO.md — Histórico + Planos do RPG

## Versões
- `andante.py` — **versão atual**: jogo idle de terminal (andares, modo idle contínuo, progresso offline, magia, passivas, conquistas, títulos)
- Versões antigas (`jogo_texto.py`, `rpg_big.py`, `rpg_causa_efeito.py`, `rpg_full.py`, `interface_colors.py`) foram removidas em 2026-10-16 — continuam no histórico do git (commit `7b2f113` e anteriores)

## O que está implementado (lista completa)
1. **Andares (1-5)**: Porto, Castelo, Caverna, Templo, Abismo — cada um com chefe, requisitos de nível/flag, recompensa de item único
2. **Modo Idle**: opção 3 no menu; joga sozinho sem parar — batalhas, chefes, andares, voltas na torre, progresso offline (ver seção abaixo)
3. **Magia D&D**: Mana = 20 + Int×10 + Nível×5 + Andar×3 + bônus da classe; regenera por turno de combate, no idle e ao subir de nível. Feitiços: Bola de Fogo (dano), Cura, Escudo Arcano (+10 DEF por 3 turnos), Impulso (+8 ATQ por 3 turnos), Restauração; no combate (`M`) ou menu (`4`)
4. **Passivas**: desbloqueadas por nível/atributos (também ao distribuir pontos). Bônus fixos: Ataque Duplo +3 ATQ, Esquiva Rápida +2 DEF, Visão Noturna +1 ATQ, Fortalecimento +5 ATQ. Por turno: Regeneração +5 HP, Invocação Rápida +3 mana. Mestre do Andar: +25% XP. Teleporte Andar: no idle enfrenta o chefe com 50% de vida (em vez de 80%)
5. **Atributos e classes**: Força, Destreza, Inteligência, Vitalidade, Carisma (+2 pontos por nível; no idle são distribuídos sozinhos pelo foco da classe). Classes: Guerreiro (+vida/ATQ/DEF), Mago (+40 mana, frágil, 2 poções), Arqueiro (equilibrado, +10 ouro)
6. **Nível + XP**: sem limite de nível; XP para o próximo = 35 × nível^2,7 (`xp_para_nivel()`); XP sobrando passa para o próximo nível; subir de nível restaura vida e mana
7. **Conquistas**: 8 em `CONQUISTAS_DEF` (Primeiro Sangue, Pescador Amigo, Crista Azul, Portão Aberto, Leitor de Manuscritos, Matador de Dragão, Dono do Porto, Diplomata) — dão ouro e XP, ficam salvas para sempre
8. **Títulos com bônus** (`TITULOS_DEF`): Aventurier, Caçador de Sombras, Guardião do Rei, Matador de Dragões, Lenda do Porto — liberados por conquista + nível; o melhor fica ativo sozinho e soma `+ATQ / +DEF`
9. **Mapa ASCII**: `desenhar_torre()` — torre vertical com 5 andares, aberto/bloqueado, chefe derrotado/pendente, posição do jogador
10. **Explorar + Diálogos com Escolhas** (menu 1 mostra a cena do andar atual): Pescador (aceitar ajudar / perguntar da torre), Guardião (mostrar o Manuscrito para passar sem lutar / desafiar), Templo (ler o Manuscrito destrava o Andar 4); Caverna e Abismo têm falas de ambiente
11. **Causa & Consequência**: flags salvas no `.txt` (`pescador_falado`, `goblin_derrotado`, `crista_pegada`, `portao_aberto`, `manuscrito_lido`, `dragao_derrotado`, `dialogo_positivo_3`); chefes ativam as flags do próximo andar (`CHEFE_FLAGS`)
12. **Save .txt editável**: `save_idle.txt` / `save_auto_idle.txt` ao lado do `andante.py` — `Chave: valor`, `## Flags` com `- [x]` e `## Inventário` com `- item: qt`
13. **Forja do Porto** (menu `F`): 6 melhorias pagas com ouro — Lâmina (+8% ATQ e magia), Armadura (+8% DEF), Amuleto (+10% Vida), Moeda da Sorte (+10% ouro), Diário (+6% XP), Botas Ligeiras (+4% de chance de ação extra por passo, máx 15). Custo cresce ~1,3–1,5× por nível. **Auto-compra** no idle (tecla `A` no idle ou `T` na Forja) compra sempre a mais barata.
14. **Altar dos Fragmentos** (menu `A`, prestígio): cada chefe dá 1 fragmento, o Rei das Sombras dá 3. Bênçãos permanentes: Força Ancestral (+10% ATQ/DEF), Ganância (+20% ouro), Sabedoria (+15% XP), Eco do Andante (+10% offline e +1h). Sem auto-compra: é a decisão do jogador. Saves antigos recebem os fragmentos dos chefes já vencidos.
15. **Tralhas viram ouro**: limite de 10 poções e 1 de cada crista/manuscrito/chave/troféu; o excesso é vendido sozinho.
16. **Poder** (menu, idle e tela do chefe): quantas vezes você aguenta mais que o chefe (>1 = deve vencer). Perdeu? O idle treina 30 passos e tenta de novo.
17. **Texto vivo**: 8 falas por andar (`FALAS_IDLE`), trabalho próprio de cada andar (`TRABALHOS`), 8 encontros raros com recompensa (`ENCONTROS`).
18. **Interface**: logo em blocos, seções que se ajustam à largura do terminal, barras, números curtos (12,3K · 4,5M), menu em duas colunas com dica do que fazer, painel do idle com torre, "rumo ao chefe", destaque ★ e ouro/XP por minuto.
19. **`andante --idle`** abre direto no modo idle.

## Como funciona o Modo Idle (opção 3)
- **Não para sozinho**: roda até você apertar `Q` (ou `Ctrl+C`). `+` / `-` mudam a velocidade (2s → 0.1s por passo).
- Cada passo: regenera vida/mana, distribui pontos de atributo pela classe, e sorteia um evento (batalha, item, ouro, fala do andar, trabalho).
- **Chefe automático**: quando nível e flag do andar batem e a vida está ≥ 80%, luta sozinho. Perdeu → recua e treina mais.
- **História destrava andares**: no idle, o Pescador (Andar 1) e a leitura do Manuscrito (Andar 4) acontecem sozinhos; os outros andares são destravados pela vitória no chefe anterior (`CHEFE_FLAGS`).
- **Voltas na torre**: depois do Rei das Sombras (Andar 5) começa a Volta 2 no Porto — inimigos e recompensas ×1.5 por volta, e cada volta pede +4 níveis (`NIVEIS_POR_VOLTA`).
- **Auto-save** a cada 10 passos e ao sair. **Progresso offline**: ao reabrir, ganha 50% do que renderia com o jogo aberto (`OFFLINE_EFICIENCIA`, máx. 12h).
- **Ritmo** (a 1s/passo, com auto-compra e um jogador que usa o Altar): nível 5 em ~3,5min; voltas na torre de ~20min, 21min, 28min, 32min, 42min; de vez em quando um chefe vence e o idle volta a treinar. Botões de ajuste: `RITMO_XP`, `xp_para_nivel()`, `NIVEIS_POR_VOLTA`, `CHEFE_VIDA/ATQ/POR_VOLTA`, custos da `FORJA`. Meça com `python3 .claude/skills/andante/scripts/ritmo.py`.
- Teclas no idle: `Q` menu · `+`/`-` velocidade · `A` liga/desliga auto-compra.
- Linux (termios/select) e Windows (msvcrt) sem instalar nada; cores ANSI ativadas no Windows por `os.system("")`.

## Plano v2 — idle completo + interface nova (2026-10-16)
Baseado na análise de 1h de idle simulado (130 mil de ouro sem uso, 0 mortes, 477 poções acumuladas, falas repetidas, log dominado por "ouro").
- [x] **Forja do Porto** (gasto de ouro): Lâmina (+ATQ%), Armadura (+DEF%), Amuleto (+Vida%), Moeda da Sorte (+ouro%), Diário (+XP%), Botas Ligeiras (chance de ação extra por passo); custo cresce a cada nível; auto-compra no idle (liga/desliga)
- [x] **Tralhas viram ouro**: limite por item (poções 10, cristas/manuscritos/chaves/troféus 1); excesso é vendido sozinho
- [x] **Altar dos Fragmentos** (prestígio): chefes dão fragmentos (Rei das Sombras dá mais); bônus permanentes escolhidos pelo jogador (sem auto-compra = decisão)
- [x] **Combate que importa**: chefes mais fortes; indicador de "Poder" (você × chefe); perder faz farmar/comprar e tentar de novo
- [x] **Texto vivo**: 8 falas por andar, trabalho próprio de cada andar, encontros aleatórios com recompensa
- [x] **Painel do idle novo**: seções, torre em linha, barra "rumo ao chefe", destaque ★ para eventos grandes, ouro/XP por minuto, números curtos (12,3K)
- [x] **Menu principal novo**: logo em blocos, cartão do personagem com barras, opções em duas colunas, dica do que fazer
- [x] **Qualidade de vida**: `andante --idle` abre direto no idle; telas de menu instantâneas (máquina de escrever só na narrativa); resumo offline em quadro

## Versão gráfica em Pyxel — protótipo (2026-10-19)
O usuário pediu "uma biblioteca visual bonita, com sprites, que pareça um joguinho leve de verdade". Escolhemos o Pyxel (motor retrô; também roda no navegador, para um dia ir ao site).
- [x] `andante_gui.py`: janela 320×240 (escala 3); o `andante.py` é o motor (o `tick_idle` roda no ritmo da velocidade escolhida)
- [x] Cenário próprio de cada andar (cais e mar, muralha com estandartes, caverna com lava, templo com velas, abismo com estrelas e névoa)
- [x] Sprites: Guerreiro, Mago, Arqueiro, um monstro por andar, chefe (o monstro do andar com outras cores, em tamanho maior), baú, companheiros do grupo (cor do elemento)
- [x] Animações a partir do que o idle fez: avanço e golpe, inimigo piscando, partículas, "+XP / +ouro" subindo, baú com o rank do item, "NOVO NÍVEL", transição de andar, escolhas de missão com [1]/[2]
- [x] HUD (vida, XP, ouro, volta, torre em miniatura, chefe, Poder), barra "rumo ao chefe", contrato, log colorido
- [x] Lê o mesmo save e aplica o progresso offline; salva a cada 10 s e ao sair ([Q]/[ESC])
- [ ] Ainda não: menus (Forja, Habilidades, Sino...), sons, levar ao site (`pyxel package` + `pyxel app2html`)

## Interface para 80×24 (2026-10-19)
O usuário achou a interface "impossível de usar". Com o terminal dele (80×24), o menu tinha 30 linhas, o idle 25 (e as linhas do log passavam de 80 colunas, então a tela rolava e piscava a cada redesenho), Habilidades 40 e Status 49.
- [x] Toda tela cabe na altura do terminal (`altura_tela()`); linhas longas são cortadas com `cortar()` (conta emoji como 2 colunas), nunca quebram
- [x] Menus de **uma tecla** (`ler_tecla()`: sem ENTER, ESC = voltar, setas = W/A/S/D; Windows via msvcrt); `TECLA_UNICA = False` volta ao `input()`
- [x] Menu principal com 18-22 linhas: **ENTER inicia o idle**; opções em 4 colunas; sistemas trancados numa linha "Em breve"; "Novidades" dentro do menu (sem pausas de ENTER)
- [x] Painel do idle se adapta à altura (o log usa o que sobra), cursor escondido, redesenho sem limpar a tela (`\033[K`)
- [x] Habilidades em abas por ramo (nós `a`-`h`), Grupo com ficha por companheiro, item de equipamento em tela própria, Status/Recordes/Diário/Missões paginados (`paginar()`)
- [x] Combate: uma tecla por turno (sem ENTER extra), barras de vida e o resultado do último turno na tela
- [x] Indicador de Poder conta habilidades ativas, grupo, lentidão, esquiva e efeitos contra chefe (antes mostrava 0,7× em luta que vencia 40/40)

## Planos futuros (do usuário / sugeridos)
- [~] **Expansão v3** (2026-10-19) — fases 0-3 prontas; faltam 4 (mapa/dungeons) e 5 (torres/passe), ver seção 15 do `docs/PLANEJAMENTO.md` — loot com ranks, missões, gacha de companheiros com lore, árvores de habilidade, faixas de nível, dungeons, torres novas, mapa aberto e desbloqueio gradual. Plano completo em `docs/PLANEJAMENTO.md`
- [ ] Sistema de guildas / clãs (salvar progresso compartilhado)
- [ ] Exportar save para JSON (`export_json()`)
- [x] Mais passivas (`Invocação Rápida`, `Teleporte Andar`, `Visão Noturna` já existem e têm efeito)
- [ ] Habilidades de classe únicas (Guerreiro: Ataque Duplo; Mago: Bola de Fogo extra; Arqueiro: Impulso)
- [x] Sistema de mercante / loja no Porto — Forja + venda automática de tralhas
- [ ] Cadernos de notas do jogador (anotações salvas no `.txt`)
- [x] Modo automático até finalizar todos os andares (loop infinito, com voltas na torre)
- [ ] Diálogos com NPCs novos (Templo, Abismo)
- [ ] Sistema de missões secundárias (ex: "Traga 3 Cristas" para recompensa extra)
- [ ] Animação simples do mapa (atualizar posição a cada turno no terminal)

## Skills do Claude (reorganizadas em 2026-10-16)
Estrutura em `.claude/skills/<nome>/SKILL.md` com frontmatter YAML (`name`, `description`) + `references/` + `scripts/`:
- `andante` — guia de desenvolvimento, `references/arquitetura.md`, `references/save.md`, `scripts/smoke_test.py` (teste automático sem interação)
- `narrativa-andante` — tom/voz, diálogos com consequência, `references/lore.md` (canon + pontas soltas), `references/padroes-codigo.md`
- `terminal-python` — testes de scripts interativos, encoding, cores, comando global, `references/dicas.md`

## Problemas encontrados na revisão (2026-10-16, confirmados com playthrough automático)
### Críticos (travam ou quebram o jogo)
- [x] Vencer o chefe do Andar 5 leva ao Andar 6 → `KeyError: 6` (menu 2, mapa, Auto Play quebram)
- [x] Save da opção 6 do Porto grava `Vida: 120/` → carregar dá `ValueError` e o jogo fecha; com esse arquivo o auto-load também falha em silêncio
- [x] Andar sobe 2× ao vencer chefe pela opção 2 (`combate()` + `cena_chefe()`) — pula o Andar 3
- [x] `portao_aberto`, `manuscrito_lido`, `dragao_derrotado` nunca eram ativadas — agora: chefes (`CHEFE_FLAGS`), cena do Templo e evento do idle
- [x] O Goblin da Floresta tem o nome do chefe ("Goblin Sombrio") → vencê-lo sobe de andar sem checar requisitos
### Combate / balanceamento
- [x] Bola de Fogo calcula dano mas não tira vida do inimigo
- [x] Escudo Arcano, Impulso, Defender e as passivas somavam ATQ/DEF de forma permanente (Fortalecimento: 44 → 94 em 10 turnos)
- [x] Mana nunca regenerava (agora: por turno de combate, no idle e ao subir de nível)
- [x] `_recalcular()` apagava a diferença entre classes: as 3 ficam com 165 HP / 34 ATQ / 20 DEF / 128 mana
- [x] `distribuir_pontos()` não desbloqueava passivas de atributo na hora
- [x] Passivas "Mestre do Andar" e "Teleporte Andar" não faziam nada
### Save / load
- [x] Load não restaura flags, inventário, atributos, passivas, `xp_max` nem nome (manual); abre arquivo sem `encoding="utf-8"`
- [x] Saves usam caminho relativo → rodando `andante` fora da pasta, os saves vão para a pasta atual
- [x] Save não usa o formato Markdown com checkboxes descrito no CLAUDE.md
### Menores
- [x] Menu 3 modo `C` ainda limita em 20 passos; `res["xp_ganho"]` soma valor fixo, não o XP real
- [x] `desenhar_torre()` marca chefes derrotados pelas flags erradas
- [x] Conquistas, títulos com bônus e `CONQUISTAS_DEF` (citados na doc) não existiam no `andante.py`
- [x] "Explorar" sempre abria o Porto, qualquer que fosse o andar
- [x] `interface_colors.py` não era usado — removido
- [x] `docs/PLANOS_E_HISTORICO.md` era uma cópia antiga deste arquivo — removido
- [x] (achado no teste) Modo idle perdia teclas apertadas rápido (`sys.stdin.read(1)` + `select`) — agora lê direto do descritor
