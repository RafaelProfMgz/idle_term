# CLAUDE.md — Contexto do Projeto RPG

## Nome
Andante (andante.py)

## Arquivos principais
- `andante.py` (jogo completo)
- `save_idle.txt` (save manual editável)
- `save_auto_idle.txt` (auto-save)
- `andante_gui.py` (versão gráfica em Pyxel, opcional)
- `CLAUDE.md` (este arquivo)
- `docs/DOCUMENTACAO.md` (histórico + planos + problemas conhecidos)
- `docs/SKILLS_TERMINAL_PY.md` (dicas de terminal/python)

## Como rodar
```bash
python3 andante.py
# Windows: python andante.py
```

## Versão gráfica (protótipo, Pyxel)
```bash
python3 -m venv .venv && .venv/bin/pip install pyxel   # uma vez
.venv/bin/python andante_gui.py
```
- `andante_gui.py` importa o `andante.py` como motor e só desenha (mesmo personagem, idle e save)
- Sprites 16×16 escritos no próprio arquivo (`SPRITES`, uma letra por cor em `COR`); fonte pixel em `assets/`
- A versão de terminal continua só com biblioteca padrão; o Pyxel é opcional
- Não rode as duas versões ao mesmo tempo: as duas gravam o `save_auto_idle.txt`

## Sistema de save (.txt Markdown estilo GitHub)
- Editar diretamente: trocar `[ ]` por `[x]` nas flags (`pescador_falado`, `portao_aberto`, etc.)
- Mudar `Andar: 2` e `Nivel: 3` para avançar
- Adicionar itens no bloco `## Inventário` (`- Poção de Vida: 3`)
- Saves ficam sempre ao lado do `andante.py`
- Carregar pela opção `8` no menu
- Também salvos: `Forja: arma=3 ...`, `Altar: ...`, `Fragmentos: N`, `AutoCompra: sim`

## Funcionalidades chave
- Andares 1-5 (Porto, Castelo, Caverna, Templo, Abismo)
- **Jogo idle**: opção 3 roda sem parar (Q sai, +/- velocidade), luta chefes, sobe andares, voltas na torre; progresso offline ao reabrir
- Magia D&D — Mana = 20 + Int×10 + Nível×5 + Andar×3 (+classe); feitiços: Bola de Fogo, Cura, Escudo Arcano, Impulso, Restauração
- Passivas — desbloqueadas por nível/atributos; conquistas (8) e títulos com bônus
- Forja `F` (ouro → melhorias, auto-compra no idle) e Altar `A` (fragmentos dos chefes → bônus permanentes)
- `andante --idle` abre direto no idle
- Explorar (opção 1) — cena do andar atual com diálogos de escolha (Pescador, Guardião, Templo)
- Recompensas de chefe — itens únicos por andar
- Mapa ASCII (torre vertical)
- Causa/Consequência via flags no `.txt`

## Skills do projeto (`.claude/skills/`)
- `andante` — desenvolvimento do jogo (arquitetura, save, regras, `scripts/smoke_test.py`)
- `narrativa-andante` — lore, diálogos, NPCs, missões com causa/consequência
- `terminal-python` — dicas de terminal/Python, testes sem interação, Windows/Linux
- Verificar depois de editar o jogo: `python3 .claude/skills/andante/scripts/smoke_test.py`
- Formato do save: `.claude/skills/andante/references/save.md`

## Instruções para o assistente (eu)
- Quando o usuário pedir algo novo, verificar se é edição de `andante.py` ou criação de doc/skill
- Sempre manter `.txt` editável (não quebrar formato Markdown)
- Se criar novos sistemas, atualizar `docs/DOCUMENTACAO.md`
- Se adicionar skills de terminal/python, atualizar `docs/SKILLS_TERMINAL_PY.md`

## Planos rápidos que o usuário pediu
- Mais passivas/skills → editar `_desbloquear_passivas()`
- Mais andares → editar `ANDARES`
- Exportar save → criar `export_json()`
- Documentação → atualizar `docs/DOCUMENTACAO.md`
