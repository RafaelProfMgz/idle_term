# SKILLS_TERMINAL_PY.md — Dicas de Terminal & Python

## Terminal (Linux / Windows)
- `Ctrl + R` — busca no histórico de comandos
- `Ctrl + C` — interrompe processo atual
- `Ctrl + Z` — suspende processo (depois `fg` retorna)
- `Ctrl + L` — limpa terminal (como `clear`)
- `ls -la` — lista com detalhes (permissões, tamanho)
- `grep -i -n "texto" arquivo` — busca case-insensitive com número da linha
- `find . -name "*.py" -type f` — procura arquivos Python
- `tar -czvf arquivo.tar.gz pasta/` — compacta (gzip)
- `tar -xzvf arquivo.tar.gz` — descompacta
- `cp arquivo destino/` — copia
- `mv arquivo novo_nome` — renomeia / move
- `chmod +x script.py` — torna executável
- `python3 -m py_compile arquivo.py` — verifica sintaxe sem rodar
- `timeout 10 comando` — mata após 10 segundos
- `echo "texto" | python3 script.py` — passa input automático

## Python — Dicas / Skills úteis
- List comprehension: `[x*2 for x in range(10) if x>3]`
- Generator expression: `(x*2 for x in range(100))`
- Decorador `@staticmethod` / `@classmethod`
- Context manager `with open("f","r") as f:` (fecha automaticamente)
- `try / except / finally`
- `re.search(r"padrão", texto)` para extrair de arquivos `.txt`
- `random.choices(lista, weights=[...], k=1)` — escolha ponderada (usado no modo idle)
- `os.system('cls' if os.name == 'nt' else 'clear')` — limpeza cross-platform
- `time.sleep(0.01)` — delay simples para efeito digitação
- `sys.stdout.write(ch); sys.stdout.flush()` — impressão caractere a caractere
- `pathlib.Path` — manipulação de caminhos moderna (funciona Windows/Linux)

## Atalhos do projeto
- Rodar jogo: `python3 andante.py`
- Verificar sintaxe: `python3 -m py_compile andante.py`
- Editar save: `nano save_idle.txt`
- Testar o jogo inteiro: `python3 .claude/skills/andante/scripts/smoke_test.py`
- Simular 100 passos de idle sem tela: `python3 -c "import andante as a; j=a.Jogador('T','Mago'); print(a.auto_play(j, passos=100, velocidade=0, desenhar=False))"`
- Ler tecla sem travar (Linux): `select.select([fd],[],[],0)` + `os.read(fd, 64)` — não use `sys.stdin.read(1)` (o buffer esconde teclas do select)

## Ler uma tecla sem ENTER (usado no Andante: `ler_tecla()`)
- Linux/macOS: `termios` + `tty.setcbreak(fd)` e `os.read(fd, 8)`; restaure com `termios.tcsetattr(fd, TCSADRAIN, antigo)` num `finally`.
- Setas chegam como sequência (`\x1b[A` cima, `\x1b[B` baixo, `\x1b[C` direita, `\x1b[D` esquerda); ESC sozinho é `\x1b`.
- Windows: `msvcrt.getwch()`; setas vêm como `\xe0` ou `\x00` seguido de `H`/`P`/`M`/`K`.
- Sem terminal (`not sys.stdin.isatty()`, testes com input simulado), caia no `input()`.

## Telas que não "pulam" no terminal
- Uma tela maior que o terminal rola e o redesenho com `\033[H` vira bagunça: limite as linhas a `shutil.get_terminal_size().lines - 1`.
- Uma linha mais larga que o terminal quebra e conta como duas: corte pela largura visível (emoji = 2 colunas, `unicodedata.east_asian_width`).
- Redesenhe com `\033[H` + linhas terminadas em `\033[K` + `\033[J` no fim (não precisa limpar a tela inteira, então não pisca). `\033[?25l` / `\033[?25h` escondem e mostram o cursor.

