---
name: andante
description: Desenvolvimento do jogo idle de terminal Andante (andante.py) — modo idle contínuo, progresso offline, andares, chefes, voltas na torre, magia (FEITICOS), passivas, combate, classes, save .txt editável e mapa ASCII da torre. Use SEMPRE que o usuário pedir para criar, mudar, corrigir ou balancear qualquer coisa do jogo (ex. "adiciona um andar 6", "cria uma passiva nova", "o auto play não para no chefe", "mexe no save", "nova magia", "loja no Porto"), mesmo que ele não diga "andante". Para textos/diálogos/lore use também narrativa-andante; para comandos de terminal use terminal-python.
---

# Andante — desenvolvimento do jogo

Andante é um **jogo idle de terminal** em **um único arquivo** (`andante.py`, ~950 linhas, só biblioteca padrão) que roda em Linux e Windows. O usuário joga pelo comando global `andante` (`~/.local/bin/andante` → `python3 /home/angel/Documentos/terminal/andante.py`).

## Antes de editar

1. Leia a parte do `andante.py` que vai mudar — o código muda com frequência e a documentação às vezes está atrasada em relação a ele. Se doc e código discordarem, **o código vale**; avise o usuário sobre a divergência.
2. Consulte `references/arquitetura.md` para saber onde cada sistema mora (funções, dicts, fórmulas).
3. Se a mudança envolve save, leia `references/save.md`.

## Como fazer mudanças comuns

| Pedido | Onde mexer | Cuidados |
|---|---|---|
| Novo andar | `ANDARES` + `CHEFE_FLAGS` + `MONSTROS` + `FALAS_IDLE` + `vencer_chefe()` (`n < 5`) + `desenhar_torre()` + `ler_save()` (`min(5, ...)`) | O número 5 está fixo em vários lugares — `grep -n "5" andante.py` |
| Nova passiva | `_desbloquear_passivas()` (condição) + `PASSIVAS_BONUS` (ATQ/DEF fixo) ou `aplicar_passivas()` (efeito por turno) | Verifique se o nome já existe antes de duplicar |
| Novo feitiço | `FEITICOS` + ramo `elif nome ==` em `usar_magia()` + `feiticos_aprendidos` da classe | Custo de mana deve caber em `mana_max` do nível 1 |
| Nova flag de causa/consequência | `self.flags` no `__init__` + onde ela vira `True` (`CHEFE_FLAGS` ou `HISTORIA`) + `req_flag` se travar andar | Se travar andar, o idle precisa conseguir ativá-la sozinho |
| Ritmo do idle | `xp_para_nivel()`, `RITMO_XP`, `NIVEIS_POR_VOLTA`, `OFFLINE_EFICIENCIA`, `stats_chefe()`, `Jogador.escala()` | Meça antes/depois com `scripts/ritmo.py`; meta: nível 5 em ~2-3 min, 1ª volta ~25-30 min, cada volta ~1,5× a anterior |
| Nova cena/NPC | `CENAS[andar]` + função `dialogo_*` chamada em `cena_explorar()` | Texto/diálogo: siga a skill `narrativa-andante` |
| Balanceamento | `CLASSES`, `_recalcular()`, `CHEFE_VIDA/ATQ/POR_VOLTA`, `MONSTRO_*`, `FORJA` (custos), `ALTAR`, `TITULOS_DEF` | Rode `scripts/ritmo.py`: as 3 classes devem ter voltas parecidas e poucas derrotas para chefe (sem muralha) |
| Nova melhoria de Forja/Altar | entrada em `FORJA`/`ALTAR` + efeito em `_recalcular()` / `mult_ouro()` / `mult_xp()` / `mult_dano()` | Salva sozinho (`Forja:`/`Altar:` no save) |
| Tela/menu | `secao()`, `colunas()`, `barra()`, `fmt_num()`; nada de emoji dentro de `colunas()` | Telas de menu usam `print` (instantâneo); `digitar()` só para narrativa |
| Conquista/título | `CONQUISTAS_DEF` / `TITULOS_DEF` (salvos automaticamente) | Rode a simulação depois (ver abaixo) |

## Regras do projeto (e por quê)

- **Só biblioteca padrão** (`os, sys, time, re, random`). O jogo é distribuído como um arquivo solto; dependência externa quebraria o `andante` global.
- **Cross-platform**: limpar tela com `os.name == 'nt'`; abrir arquivos com `encoding="utf-8"` (no Windows o padrão não é UTF-8 e os acentos quebram); nada de aspas duplas dentro de f-string com aspas duplas (só funciona no Python 3.12+).
- **Save legível por humanos**: o usuário edita o `.txt` à mão. Nunca troque para JSON/pickle no save principal; um `export_json()` extra é ok.
- **É um jogo idle**: o modo idle (`auto_play`) **nunca para sozinho** — só com `Q`/Ctrl+C. Ele luta chefes, sobe andares e recomeça a torre (voltas) por conta própria. Nada pode exigir input do jogador para o idle progredir.
- **Teclas sem travar** via `LeitorTecla` (msvcrt no Windows, termios+select no Linux). Não use bibliotecas como `keyboard`/`curses` (curses não vem no Windows).
- **Status nunca acumulam**: tudo que é permanente entra em `_recalcular()`; buffs de combate valem só por turnos e zeram ao fim da luta.
- **Recompensa de chefe** vai para o inventário e está declarada em `ANDARES[n]["recompensa"]`.
- Mantenha o estilo do código: nomes em português, `digitar()` para texto narrativo, `print()` para menus, emojis com tag entre colchetes (`[👑 CHEFE DERROTADO!]`).

## Depois de editar — verificar sempre

```bash
python3 -m py_compile andante.py                      # sintaxe
python3 .claude/skills/andante/scripts/smoke_test.py  # cria personagens, roda o idle, magia, save/load sem interação
python3 .claude/skills/andante/scripts/regressao.py  # um teste por bug já corrigido (docs/DOCUMENTACAO.md)
```

O `smoke_test.py` roda em pasta temporária (não toca nos saves do usuário) e desliga as animações. Se você criou um sistema novo, acrescente uma checagem no smoke test; se corrigiu um bug, acrescente um item no `regressao.py` e marque `[x]` no `docs/DOCUMENTACAO.md`.

## Documentação

Ao criar sistema novo: atualize `docs/DOCUMENTACAO.md` (lista "O que está implementado" e marque o item nos "Planos futuros") e, se mudar regras/arquivos, o `CLAUDE.md` da raiz.
