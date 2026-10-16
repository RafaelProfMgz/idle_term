# Lore do Andante

## Canon (já está no código — não contradizer)

**A torre**: 5 andares; o jogador começa no 1 e sobe derrotando chefes. Cada andar exige nível mínimo e uma flag.

| Andar | Lugar | Chefe | Destrava com | Recompensa |
|---|---|---|---|---|
| 1 | Porto & Floresta | Goblin Sombrio | falar com o Pescador | Crista do Goblin |
| 2 | Castelo do Rei | Guardião Real | pegar a crista (vencer o goblin) | Coroa do Guardião |
| 3 | Caverna do Dragão | Dragão Antigo | portão do castelo aberto | Escama do Dragão |
| 4 | Templo Antigo | Cumulador | ler o Manuscrito Antigo | Relíquia Antiga |
| 5 | Abismo | Rei das Sombras | dragão derrotado | Cristal da Sombra |

**Personagens**
- **Pescador** (Porto): pede ajuda, ativa a missão *"O Mar Escuro"* e entrega **Chave do Castelo** e **Manuscrito Antigo**. Frase atual: *"Se você me ajudar, te darei o caminho."*
- **Guardião** (Castelo): descrito na documentação — aceita suborno com o manuscrito, combate ou deixa passar (diálogo ainda não implementado em `andante.py`; existia em `rpg_full.py`).

**Classes**: Guerreiro, Mago, Arqueiro. **Títulos**: Aventurier, Caçador de Sombras, Guardião do Rei, Matador de Dragões, Lenda do Porto.

**Itens**: Poção de Vida, Crista Azul, Chave do Castelo, Manuscrito Antigo + recompensas dos chefes.

**Feitiços**: Bola de Fogo, Cura, Escudo Arcano, Impulso, Restauração.

**Flags**: `pescador_falado, goblin_derrotado, crista_pegada, portao_aberto, manuscrito_lido, dragao_derrotado, dialogo_positivo_3`.

## Pontas soltas (oportunidades — confirmar com o usuário antes de virar canon)

- O que é *"O Mar Escuro"*? A missão é ativada mas nunca concluída.
- Por que um pescador tem a chave do castelo e um manuscrito antigo?
- `portao_aberto`, `manuscrito_lido` e `dragao_derrotado` não são ativadas em nenhum lugar do `andante.py` — do andar 3 em diante o jogo fica travado. Precisam de cena (Castelo/Guardião, leitura do manuscrito).
- "Cumulador" (chefe do Templo) não tem descrição. Algo que acumula — oferendas? memórias? almas dos que subiram?
- Templo e Abismo não têm NPCs (está nos planos do usuário).
- Crista Azul vs Crista do Goblin: dois itens parecidos; vale explicar a diferença ou unificar.
- O Rei das Sombras tem relação com o Rei do Castelo?

## Ideias de direção (sugestões, não canon)

- A torre é invertida: "subir" andares leva para baixo do mar; o Porto é o único lugar com céu.
- O Pescador perdeu alguém no Mar Escuro e quer que o jogador traga notícia do Abismo — dá peso ao final.
- O Manuscrito é um diário de um andante anterior; cada andar revela uma página (combina com `manuscrito_lido`).
