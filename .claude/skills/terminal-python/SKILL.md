---
name: terminal-python
description: Boas práticas de Python e de terminal (Linux zsh / Windows) para este projeto — testar scripts interativos sem travar, simular input, checar sintaxe, inspecionar/editar saves .txt, cores ANSI, compatibilidade Windows, instalar o comando global e organizar código Python de jogo de terminal. Use quando o usuário pedir dica de terminal ou Python, pedir para rodar/testar/automatizar o jogo, refatorar código Python, perguntar sobre cores, encoding, input(), argparse, pathlib, ou "como faço X no terminal", mesmo sem citar esta skill.
---

# Terminal & Python — guia do projeto

Ambiente do usuário: Linux com **zsh**, Python 3 (`python3`); o jogo também precisa rodar no Windows (`python`). Projeto em `/home/angel/Documentos/terminal`.

## Testar programas interativos sem travar

Programas com `input()` param esperando teclado. Para testar de forma automática:

```bash
python3 -m py_compile andante.py                      # 1º: só sintaxe, rápido
printf 'Hero\nG\n20\n9\n' | timeout 10 python3 andante.py   # respostas em sequência
python3 .claude/skills/andante/scripts/smoke_test.py  # teste completo sem interação
```

- Sempre use `timeout` ao alimentar input: se as respostas acabarem, `input()` levanta `EOFError` ou o loop gira para sempre.
- `animar_batalha()`/`digitar()` usam `time.sleep`; em testes, faça monkeypatch (`time.sleep = lambda *_: None`), como o smoke test faz.
- Para testar uma função isolada: `python3 -c "import andante as a; j=a.Jogador('T','Mago'); print(j.mana_max)"` (rodar na pasta do projeto).

## Ler tecla sem travar (idle) — Linux e Windows, sem dependências

O jogo já tem `LeitorTecla` no `andante.py`. Padrão usado:
- Windows: `msvcrt.kbhit()` + `msvcrt.getwch()`
- Linux: `tty.setcbreak()` + `select.select([sys.stdin], [], [], 0)`; **restaure** o terminal com `termios.tcsetattr` num `finally`/`__exit__`, senão o terminal do usuário fica sem eco.
- Sem TTY (input por pipe/teste): não ler teclas; o loop é parado por `passos` ou Ctrl+C.
- Para testar o modo idle de verdade, use um pseudo-terminal (`pty.fork()` no Linux) e mande teclas com `os.write(fd, b"q")`.

## Escrever Python neste projeto

- **Só biblioteca padrão.** Útil: `pathlib`, `re`, `random.choices(weights=)`, `dataclasses`, `json` (para export), `argparse` (para flags como `--auto`), `shutil.get_terminal_size()`.
- **Encoding**: `open(arq, "w", encoding="utf-8")` sempre — Windows usa cp1252 por padrão e corrompe acentos/emojis.
- **Limpar tela**: `os.system('cls' if os.name == 'nt' else 'clear')`. Alternativa sem subprocesso: `print("\033[2J\033[H", end="")`.
- **Cores ANSI** funcionam no zsh e no Windows Terminal; no `cmd.exe` antigo, chame `os.system("")` uma vez no início para habilitar.
- **Caminho do save**: fixo ao lado do script (`PASTA_JOGO = os.path.dirname(os.path.abspath(__file__))`) — funciona com o comando global `andante` de qualquer pasta.
- **f-strings**: não repita o mesmo tipo de aspas dentro de `{}` (`f"{d['x']}"` ok; `f"{d["x"]}"` só no Python 3.12+ e quebra no Windows com Python mais antigo).
- `except:` sem tipo engole `KeyboardInterrupt`; prefira `except Exception:`.
- Converter input numérico com segurança: `int(s) if s.isdigit() else padrao`.

## Inspecionar e editar saves

```bash
cat save_idle.txt
grep -n "^Nivel:" save_idle.txt
sed -i 's/^Nivel:.*/Nivel:5/' save_idle.txt   # editar sem abrir editor
diff save_idle.txt save_auto_idle.txt
```

Formato do save: ver `.claude/skills/andante/references/save.md`.

## Comando global `andante`

Já existe `~/.local/bin/andante`:
```bash
#!/bin/bash
exec python3 /home/angel/Documentos/terminal/andante.py "$@"
```
Se mover o projeto, atualize esse caminho. `~/.local/bin` precisa estar no `PATH` (`echo $PATH`). Após criar, `chmod +x ~/.local/bin/andante` e, no zsh, `rehash`.

## Mais dicas

Atalhos de terminal, comandos de arquivo e truques Python: `references/dicas.md`. Quando aprender uma dica nova útil ao usuário, adicione lá **e** em `docs/SKILLS_TERMINAL_PY.md` (o usuário lê esse arquivo).

## Segurança

Nada de `rm -rf` com caminhos absolutos ou curingas em scripts automáticos; para limpar cache use `find . -name __pycache__ -type d -prune -exec rm -r {} +` dentro do projeto.
