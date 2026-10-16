# CLAUDE.md — Contexto do Projeto RPG

## Nome
Andante (andante.py)

## Arquivos principais
- `andante.py` (jogo completo)
- `save_idle.txt` (save manual editável)
- `save_auto_idle.txt` (auto-save)
- `CLAUDE.md` (este arquivo)
- `DOCUMENTACAO.md` (histórico + planos)
- `SKILLS_TERMINAL_PY.md` (dicas de terminal/python)

## Como rodar
```bash
python3 andante.py
# Windows: python andante.py
```

## Sistema de save (.txt Markdown estilo GitHub)
- Editar diretamente: trocar `[ ]` por `[x]` nas flags (`pescador_falado`, `portao_aberto`, etc.)
- Mudar `Andar: 2` e `Nivel: 3` para avançar
- Adicionar itens no bloco `Inventário:`
- Carregar pela opção `8` no menu

## Funcionalidades chave
- Andares 1-5 (Porto, Castelo, Caverna, Templo, Abismo)
- Auto Play (Idle) — opção 3 / modo `C` (até chefe)
- Magia D&D — Mana = Int*10; feitiços: Bola de Fogo, Cura, Escudo, Impulso, Restauração
- Passivas — desbloqueadas por nível/atributos
- Recompensas de chefe — itens únicos por andar
- Mapa ASCII (torre vertical)
- Causa/Consequência via flags no `.txt`

## Skills do projeto (`.claude/skills/`)
- `andante` — desenvolvimento do jogo (arquitetura, save, regras, `scripts/smoke_test.py`)
- `narrativa-andante` — lore, diálogos, NPCs, missões com causa/consequência
- `terminal-python` — dicas de terminal/Python, testes sem interação, Windows/Linux
- Verificar depois de editar o jogo: `python3 .claude/skills/andante/scripts/smoke_test.py`
- Atenção: o save real é `Chave:valor` (sem flags/inventário) — ver `.claude/skills/andante/references/save.md`

## Instruções para o assistente (eu)
- Quando o usuário pedir algo novo, verificar se é edição de `andante.py` ou criação de doc/skill
- Sempre manter `.txt` editável (não quebrar formato Markdown)
- Se criar novos sistemas, atualizar `DOCUMENTACAO.md`
- Se adicionar skills de terminal/python, atualizar `SKILLS_TERMINAL_PY.md`

## Planos rápidos que o usuário pediu
- Mais passivas/skills → editar `_desbloquear_passivas()`
- Mais andares → editar `ANDARES`
- Exportar save → criar `export_json()`
- Documentação → atualizar `DOCUMENTACAO.md`
