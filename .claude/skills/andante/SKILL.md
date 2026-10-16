---
name: andante
description: Desenvolvimento do RPG de terminal Andante (andante.py) — andares, chefes, Auto Play/idle, magia (FEITICOS), passivas, combate, classes, save .txt editável e mapa ASCII da torre. Use SEMPRE que o usuário pedir para criar, mudar, corrigir ou balancear qualquer coisa do jogo (ex. "adiciona um andar 6", "cria uma passiva nova", "o auto play não para no chefe", "mexe no save", "nova magia", "loja no Porto"), mesmo que ele não diga "andante". Para textos/diálogos/lore use também narrativa-andante; para comandos de terminal use terminal-python.
---

# Andante — desenvolvimento do jogo

Andante é um RPG de texto em **um único arquivo** (`andante.py`, ~700 linhas, só biblioteca padrão) que roda em Linux e Windows. O usuário joga pelo comando global `andante` (`~/.local/bin/andante` → `python3 /home/angel/Documentos/terminal/andante.py`).

## Antes de editar

1. Leia a parte do `andante.py` que vai mudar — o código muda com frequência e a documentação às vezes está atrasada em relação a ele. Se doc e código discordarem, **o código vale**; avise o usuário sobre a divergência.
2. Consulte `references/arquitetura.md` para saber onde cada sistema mora (funções, dicts, fórmulas).
3. Se a mudança envolve save, leia `references/save.md` — o formato real é `Chave:valor`, não o Markdown com checkboxes que o CLAUDE.md descreve.

## Como fazer mudanças comuns

| Pedido | Onde mexer | Cuidados |
|---|---|---|
| Novo andar | `ANDARES` + `desenhar_torre()` (loop `range(5,0,-1)` e `chefe_ok`) + `combate()` (`jogador.andar < 5`) | O número 5 está fixo em vários lugares — procure com `grep -n "5" andante.py` perto de andar |
| Nova passiva | `_desbloquear_passivas()` (condição) + `aplicar_passivas()` (efeito) | Verifique se o nome já existe antes de duplicar |
| Novo feitiço | `FEITICOS` + ramo `elif nome ==` em `usar_magia()` + `feiticos_aprendidos` da classe | Custo de mana deve caber em `mana_max` do nível 1 |
| Nova flag de causa/consequência | `self.flags` no `__init__` + onde ela vira `True` + `req_flag` se travar andar | Flags hoje **não são salvas** — veja `references/save.md` |
| Nova cena/NPC | função `cena_*` no estilo de `cena_porto()` + entrada no menu | Texto/diálogo: siga a skill `narrativa-andante` |
| Balanceamento | `_recalcular()`, `combate()`, `cena_chefe()` (vida/atq do chefe por andar) | Rode a simulação depois (ver abaixo) |

## Regras do projeto (e por quê)

- **Só biblioteca padrão** (`os, sys, time, re, random`). O jogo é distribuído como um arquivo solto; dependência externa quebraria o `andante` global.
- **Cross-platform**: limpar tela com `os.name == 'nt'`; abrir arquivos com `encoding="utf-8"` (no Windows o padrão não é UTF-8 e os acentos quebram).
- **Save legível por humanos**: o usuário edita o `.txt` à mão. Nunca troque para JSON/pickle no save principal; um `export_json()` extra é ok.
- **Auto Play com `ate_chefe`** deve parar assim que `nivel >= req_nivel` e a `req_flag` estiver ativa.
- **Passivas** são aplicadas via `aplicar_passivas()` no início de cada turno de `combate()`.
- **Recompensa de chefe** vai para o inventário e está declarada em `ANDARES[n]["recompensa"]`.
- Mantenha o estilo do código: nomes em português, `digitar()` para texto narrativo, `print()` para menus, emojis com tag entre colchetes (`[👑 CHEFE DERROTADO!]`).

## Depois de editar — verificar sempre

```bash
python3 -m py_compile andante.py                      # sintaxe
python3 .claude/skills/andante/scripts/smoke_test.py  # cria personagens, roda auto play, magia, save/load sem interação
```

O `smoke_test.py` roda em pasta temporária (não toca nos saves do usuário) e desliga as animações. Se você criou um sistema novo, acrescente uma checagem nele.

## Documentação

Ao criar sistema novo: atualize `DOCUMENTACAO.md` (lista "O que está implementado" e marque o item nos "Planos futuros") e, se mudar regras/arquivos, o `CLAUDE.md` da raiz.
