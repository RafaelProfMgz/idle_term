# Andante — idle de terminal

Um RPG **idle** que roda no terminal (Linux e Windows, só Python 3.8+, sem instalar nada).
O andante sobe uma torre de 5 andares sozinho: luta, compra melhorias na Forja, enfrenta chefes
e recomeça a torre mais forte. Feche o jogo e o progresso offline continua.

```bash
python3 andante.py          # Windows: python andante.py
python3 andante.py --idle   # abre direto no modo idle
```

- **Idle** (opção 3): `Q` volta ao menu · `+`/`-` velocidade · `A` liga/desliga a auto-compra
- **Forja** (`F`): gaste ouro em ATQ, DEF, Vida, Sorte, XP e Botas
- **Altar** (`A`): fragmentos dos chefes viram bônus permanentes
- Save em `.txt` editável à mão, ao lado do `andante.py`

Documentação: [`docs/DOCUMENTACAO.md`](docs/DOCUMENTACAO.md)
