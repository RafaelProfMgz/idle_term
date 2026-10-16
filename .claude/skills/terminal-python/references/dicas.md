# Dicas de Terminal & Python (referência)

## Atalhos do terminal (zsh / bash)
- `Ctrl+R` busca no histórico · `Ctrl+C` interrompe · `Ctrl+Z` suspende (`fg` volta) · `Ctrl+L` limpa
- `Ctrl+A` / `Ctrl+E` início/fim da linha · `Ctrl+W` apaga palavra · `!!` repete último comando

## Arquivos
- `ls -la` — lista com detalhes
- `grep -rin "texto" .` — busca recursiva, ignora maiúsculas, mostra linha
- `find . -name "*.py" -type f` — acha arquivos Python
- `wc -l andante.py` — conta linhas
- `tar -czvf backup.tar.gz pasta/` / `tar -xzvf backup.tar.gz` — compacta / extrai
- `cp andante.py andante.bak.py` — backup rápido antes de mexer
- `chmod +x script.py` — torna executável (precisa do `#!/usr/bin/env python3`)

## Rodar e testar
- `python3 -m py_compile arq.py` — checa sintaxe sem rodar
- `timeout 10 comando` — mata após 10 s
- `printf 'a\nb\n' | python3 script.py` — input automático
- `python3 -i andante.py` — roda e cai no REPL (Ctrl+C no menu, depois inspecione variáveis)
- `python3 -m timeit -s "import andante" "andante.Jogador()"` — mede velocidade
- `python3 -m pdb andante.py` — depurador (`n` próxima, `s` entra, `p var` mostra)

## Python — padrões úteis
- List comprehension: `[x*2 for x in range(10) if x > 3]`
- Dict com padrão: `inven[item] = inven.get(item, 0) + 1`
- Escolha ponderada: `random.choices(lista, weights=[...], k=1)[0]`
- Context manager: `with open("f", encoding="utf-8") as f:`
- Regex no save: `re.search(r"^Nivel:(\d+)", texto, re.M)`
- f-string com largura: `f"{nome:<12}|{vida:>4}"` (alinha colunas no terminal)
- Impressão caractere a caractere: `sys.stdout.write(ch); sys.stdout.flush()`
- Reescrever a mesma linha: `print(f"\r{texto}", end="", flush=True)`
- Tamanho do terminal: `shutil.get_terminal_size().columns`
- Caminho ao lado do script: `Path(__file__).with_name("save_idle.txt")`
- Cross-platform clear: `os.system('cls' if os.name == 'nt' else 'clear')`

## Windows
- Rodar: `python andante.py` (ou `py andante.py`)
- Cores no cmd antigo: `os.system("")` no início do programa
- Encoding: sempre `encoding="utf-8"` em `open()`; no console, `chcp 65001` para emojis
