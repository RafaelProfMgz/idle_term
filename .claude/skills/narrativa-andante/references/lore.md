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
- **Guardião** (Castelo): "Ninguém passa sem ordem do Rei. E o Rei não dá ordens há anos." Reconhece a letra do Rei no Manuscrito e deixa passar sem lutar; ou é desafiado (é o chefe Guardião Real).
- **Pescador** também responde sobre a torre: "Dizem que quem sobe a torre desce ao fundo do mar. Eu só sei que ninguém voltou."
- **Manuscrito** (Templo): a tinta reaparece à luz das velas; é um mapa da escada até o Cumulador.
- **Voltas**: depois do Rei das Sombras "a torre gira" e o andante recomeça no Porto, mais forte (Volta 2, 3...).

**Classes**: Guerreiro, Mago, Arqueiro. **Títulos**: Aventurier, Caçador de Sombras, Guardião do Rei, Matador de Dragões, Lenda do Porto.

**Itens**: Poção de Vida, Crista Azul, Chave do Castelo, Manuscrito Antigo + recompensas dos chefes.

**Lugares/pessoas novos (v2)**: o **ferreiro** da Forja do Porto ("Ouro primeiro, conversa depois."), o **Altar dos Fragmentos** (fragmentos da torre caem dos chefes), encontros: mercador ambulante, viajante ferido, corvo, três esqueletos jogando dados, a padeira do porto.

**Feitiços**: Bola de Fogo, Cura, Escudo Arcano, Impulso, Restauração.

**Flags**: `pescador_falado, goblin_derrotado, crista_pegada, portao_aberto, manuscrito_lido, dragao_derrotado, dialogo_positivo_3`.

## Pontas soltas (oportunidades — confirmar com o usuário antes de virar canon)

- O que é *"O Mar Escuro"*? A missão é ativada mas nunca concluída.
- Por que um pescador tem a chave do castelo e um manuscrito antigo?
- Por que a torre "gira" depois do Rei das Sombras? (mecânica de voltas existe, falta explicação)
- "Cumulador" (chefe do Templo) não tem descrição. Algo que acumula — oferendas? memórias? almas dos que subiram?
- Caverna, Templo e Abismo não têm NPCs com escolha — só ações/falas de ambiente (está nos planos do usuário).
- Crista Azul vs Crista do Goblin: dois itens parecidos; vale explicar a diferença ou unificar.
- O Rei das Sombras tem relação com o Rei do Castelo?

## Ideias de direção (sugestões, não canon)

- A torre é invertida: "subir" andares leva para baixo do mar; o Porto é o único lugar com céu.
- O Pescador perdeu alguém no Mar Escuro e quer que o jogador traga notícia do Abismo — dá peso ao final.
- O Manuscrito é um diário de um andante anterior; cada andar revela uma página (combina com `manuscrito_lido`).
