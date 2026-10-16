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
6. **Nível + XP**: sem limite de nível; XP para o próximo = 100 × nível; XP sobrando passa para o próximo nível; subir de nível restaura vida e mana
7. **Conquistas**: 8 em `CONQUISTAS_DEF` (Primeiro Sangue, Pescador Amigo, Crista Azul, Portão Aberto, Leitor de Manuscritos, Matador de Dragão, Dono do Porto, Diplomata) — dão ouro e XP, ficam salvas para sempre
8. **Títulos com bônus** (`TITULOS_DEF`): Aventurier, Caçador de Sombras, Guardião do Rei, Matador de Dragões, Lenda do Porto — liberados por conquista + nível; o melhor fica ativo sozinho e soma `+ATQ / +DEF`
9. **Mapa ASCII**: `desenhar_torre()` — torre vertical com 5 andares, aberto/bloqueado, chefe derrotado/pendente, posição do jogador
10. **Explorar + Diálogos com Escolhas** (menu 1 mostra a cena do andar atual): Pescador (aceitar ajudar / perguntar da torre), Guardião (mostrar o Manuscrito para passar sem lutar / desafiar), Templo (ler o Manuscrito destrava o Andar 4); Caverna e Abismo têm falas de ambiente
11. **Causa & Consequência**: flags salvas no `.txt` (`pescador_falado`, `goblin_derrotado`, `crista_pegada`, `portao_aberto`, `manuscrito_lido`, `dragao_derrotado`, `dialogo_positivo_3`); chefes ativam as flags do próximo andar (`CHEFE_FLAGS`)
12. **Save .txt editável**: `save_idle.txt` / `save_auto_idle.txt` ao lado do `andante.py` — `Chave: valor`, `## Flags` com `- [x]` e `## Inventário` com `- item: qt`

## Como funciona o Modo Idle (opção 3)
- **Não para sozinho**: roda até você apertar `Q` (ou `Ctrl+C`). `+` / `-` mudam a velocidade (2s → 0.1s por passo).
- Cada passo: regenera vida/mana, distribui pontos de atributo pela classe, e sorteia um evento (batalha, item, ouro, fala do andar, trabalho).
- **Chefe automático**: quando nível e flag do andar batem e a vida está ≥ 80%, luta sozinho. Perdeu → recua e treina mais.
- **História destrava andares**: no idle, o Pescador (Andar 1) e a leitura do Manuscrito (Andar 4) acontecem sozinhos; os outros andares são destravados pela vitória no chefe anterior (`CHEFE_FLAGS`).
- **Voltas na torre**: depois do Rei das Sombras (Andar 5) começa a Volta 2 no Porto — inimigos e recompensas ×1.5 por volta, e cada volta pede +10 níveis.
- **Auto-save** a cada 10 passos e ao sair. **Progresso offline**: ao reabrir, ganha ~30% do que renderia com o jogo aberto (máx. 8h).
- Ritmo: `RITMO_XP = 0.12` → 1ª volta ~15 min, 2ª ~50 min a 1s/passo. Ajuste essa constante para acelerar/desacelerar.
- Linux (termios/select) e Windows (msvcrt) sem instalar nada; cores ANSI ativadas no Windows por `os.system("")`.

## Planos futuros (do usuário / sugeridos)
- [ ] Sistema de guildas / clãs (salvar progresso compartilhado)
- [ ] Exportar save para JSON (`export_json()`)
- [ ] Mais passivas (ex: `Invocação Rápida`, `Teleporte Andar`, `Visão Noturna`)
- [ ] Habilidades de classe únicas (Guerreiro: Ataque Duplo; Mago: Bola de Fogo extra; Arqueiro: Impulso)
- [ ] Sistema de mercante / loja no Porto (comprar/ vender itens com ouro)
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
