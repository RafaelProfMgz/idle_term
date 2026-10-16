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
- `random.choices(lista, weights=[...], k=1)` — escolha ponderada (usado no Auto Play)
- `os.system('cls' if os.name == 'nt' else 'clear')` — limpeza cross-platform
- `time.sleep(0.01)` — delay simples para efeito digitação
- `sys.stdout.write(ch); sys.stdout.flush()` — impressão caractere a caractere
- `pathlib.Path` — manipulação de caminhos moderna (funciona Windows/Linux)

## Atalhos do projeto
- Rodar jogo: `python3 andante.py`
- Verificar sintaxe: `python3 -m py_compile andante.py`
- Editar save: `nano save_idle.txt`
- Auto save: `python3 -c "import andante as r; j=r.Jogador(); r.auto_play(j, passos=10)"`
