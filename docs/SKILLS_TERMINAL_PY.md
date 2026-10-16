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
