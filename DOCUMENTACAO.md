# DOCUMENTACAO.md — Histórico + Planos do RPG

## Versões
- `jogo_texto.py` — jogo básico de texto (criado inicial)
- `rpg_big.py` — RPG maior com save Markdown (.txt estilo GitHub)
- `rpg_causa_efeito.py` — causa/consequência com flags e missões
- `rpg_full.py` — expansão: classes, atributos, nível, conquistas, títulos, mapa ASCII, diálogos
- `andante.py` — ANDARES + AUTO PLAY + MAGIA + PASSIVAS + MAPA VERTICAL

## O que está implementado (lista completa)
1. **Andares (1-5)**: Porto, Castelo, Caverna, Templo, Abismo — cada um com chefe, requisitos de nível/flag, recompensa de item único
2. **Auto Play (Idle)**: opção 3 no menu; modo `C` para auto até chefe; simula batalhas, itens, ouro, XP, eventos aleatórios, regeneração
3. **Magia D&D**: Mana = Int*10; feitiços: Bola de Fogo, Cura, Escudo Arcano, Impulso, Restauração; pode usar no combate (`M`) ou menu (`4`)
4. **Passivas / Skills**: desbloqueadas por nível/atributos (`_desbloquear_passivas` + `aplicar_passivas`)
5. **Atributos**: Força, Destreza, Inteligência, Vitalidade, Carisma — distribuição de pontos ao subir nível
6. **Nível + XP**: nível 1-99, +2 pontos de atributo por level up
7. **Conquistas**: 8 definidas (`CONQUISTAS_DEF`); desbloqueiam ao completar ações
8. **Títulos com Status**: Aventurier, Caçador de Sombras, Guardião do Rei, Matador de Dragões, Lenda do Porto — bônus `+ATQ / +DEF`
9. **Mapa ASCII maior**: `desenhar_torre()` — torre vertical com 5 andares, status aberto/bloqueado, posição do jogador
10. **Diálogos com Escolhas**: Pescador (Porto) e Guardião (Castelo) — respostas impactam flags, XP, itens
11. **Causa & Consequência**: flags no `.txt` (`pescador_falado`, `goblin_derrotado`, `crista_pegada`, `portao_aberto`, `manuscrito_lido`, `dragao_derrotado`)
12. **Save .txt editável**: `save_idle.txt` / `save_auto_idle.txt` em Markdown (tabelas, checkboxes, seções claras)

## Como funciona o Auto Play / Idle
- Escolha `3` → `C` (até chefe)
- Loop de `20` ciclos: batalha aleatória (XP, ouro, vida), item aleatório, evento (diálogo, ouro), regeneração
- Quando `Nível >= req_nivel` e `Flag` satisfeita → para automaticamente, mostra mensagem para ir ao chefe (`opção 2`)
- Ao derrotar chefe → ganha recompensa (item único), sobe andar (`Andar += 1`)

## Planos futuros (do usuário / sugeridos)
- [ ] Sistema de guildas / clãs (salvar progresso compartilhado)
- [ ] Exportar save para JSON (`export_json()`)
- [ ] Mais passivas (ex: `Invocação Rápida`, `Teleporte Andar`, `Visão Noturna`)
- [ ] Habilidades de classe únicas (Guerreiro: Ataque Duplo; Mago: Bola de Fogo extra; Arqueiro: Impulso)
- [ ] Sistema de mercante / loja no Porto (comprar/ vender itens com ouro)
- [ ] Cadernos de notas do jogador (anotações salvas no `.txt`)
- [ ] Modo automático até finalizar todos os andares (loop infinito até Andar 5)
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
- [ ] Vencer o chefe do Andar 5 leva ao Andar 6 → `KeyError: 6` (menu 2, mapa, Auto Play quebram)
- [ ] Save da opção 6 do Porto grava `Vida: 120/` → carregar dá `ValueError` e o jogo fecha; com esse arquivo o auto-load também falha em silêncio
- [ ] Andar sobe 2× ao vencer chefe pela opção 2 (`combate()` + `cena_chefe()`) — pula o Andar 3
- [ ] `portao_aberto`, `manuscrito_lido`, `dragao_derrotado` nunca são ativadas → trava no Andar 4 (ou 3)
- [ ] O Goblin da Floresta tem o nome do chefe ("Goblin Sombrio") → vencê-lo sobe de andar sem checar requisitos
### Combate / balanceamento
- [ ] Bola de Fogo calcula dano mas não tira vida do inimigo
- [ ] Escudo Arcano, Impulso, Defender e as passivas somam ATQ/DEF de forma permanente (Fortalecimento: 44 → 94 em 10 turnos)
- [ ] Mana nunca regenera (nem ao subir de nível nem no Auto Play)
- [ ] `_recalcular()` apaga a diferença entre classes: as 3 ficam com 165 HP / 34 ATQ / 20 DEF / 128 mana
- [ ] `distribuir_pontos()` não desbloqueia passivas de atributo na hora
- [ ] Passivas "Mestre do Andar" e "Teleporte Andar" não fazem nada
### Save / load
- [ ] Load não restaura flags, inventário, atributos, passivas, `xp_max` nem nome (manual); abre arquivo sem `encoding="utf-8"`
- [ ] Saves usam caminho relativo → rodando `andante` fora da pasta, os saves vão para a pasta atual
- [ ] Save não usa o formato Markdown com checkboxes descrito no CLAUDE.md
### Menores
- [ ] Menu 3 modo `C` ainda limita em 20 passos; `res["xp_ganho"]` soma valor fixo, não o XP real
- [ ] `desenhar_torre()` marca chefes derrotados pelas flags erradas
- [ ] Conquistas "Matador do Chefe"/"Explorador", títulos com bônus e `CONQUISTAS_DEF` (citados na doc) não existem no `andante.py`
- [ ] "Explorar" sempre abre o Porto, qualquer que seja o andar (campo `salas` não é usado)
- [ ] `interface_colors.py` não é usado; `docs/PLANOS_E_HISTORICO.md` é cópia antiga deste arquivo (cita `rpg_idle_andar.py`)
