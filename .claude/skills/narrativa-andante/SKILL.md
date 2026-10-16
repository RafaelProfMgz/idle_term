---
name: narrativa-andante
description: Escrita narrativa para o RPG Andante — lore da torre e dos 5 andares, NPCs, diálogos com escolhas, missões, descrições de cena, falas de chefe, nomes de itens/feitiços/passivas e eventos do modo idle, sempre ligados a flags de causa/consequência. Use quando o usuário pedir história, diálogo, texto, NPC novo, missão, lore, fala de chefe, descrição de andar, nome de item, evento aleatório ou "deixa o jogo mais imersivo", mesmo que não peça explicitamente "narrativa". Junto com a skill andante quando o texto for entrar no código.
---

# Narrativa do Andante

Andante é sobre **subir**: um viajante chega a um porto de pescadores e descobre uma torre de cinco andares que desce do mar ao abismo — quanto mais alto o andar, mais fundo e escuro o lugar. O nome vem do *andante*, quem anda, e do *andar* da torre.

Antes de escrever, leia `references/lore.md` (o que já é canônico no código e quais pontas estão soltas). Para colocar texto no código, siga `references/padroes-codigo.md`.

## Tom e voz

- **Português do Brasil**, frases curtas. O texto aparece letra a letra (`digitar()`), então cada linha deve caber em ~70 colunas e render uma leitura de 2–4 segundos.
- Melancólico com humor seco: o mundo é sombrio, os personagens não são solenes demais. O Pescador resmunga; o Guardião é formal e cansado.
- Mostre por detalhe concreto (cheiro de sal, corda podre, tocha que treme), não por adjetivo genérico ("lugar misterioso e assustador").
- Narração em 2ª pessoa ("Você sobe a escada..."). NPCs falam entre aspas com o nome antes: `Pescador: "..."`.
- Emojis só nas tags de sistema (`[📜 MISSÃO ATIVADA]`), nunca no meio da prosa.

## Toda escolha precisa de consequência

O coração do jogo é causa → consequência via `jogador.flags`. Ao escrever um diálogo ou evento:

1. Ofereça **2–3 opções** com intenções diferentes (ajudar / negociar / ameaçar, por exemplo), não sinônimos.
2. Cada opção muda algo concreto: uma flag, um item, XP, ouro, ou `dialogo_positivo`.
3. A consequência deve aparecer **depois**, em outro lugar (o NPC lembra, uma porta abre, um chefe menciona o que você fez). Escolha sem eco posterior parece falsa.
4. Liste no fim da entrega: flags novas, onde são ativadas e onde são lidas.

## Formato de entrega

Quando o usuário pedir conteúdo narrativo, entregue:

```
### <Nome da cena / NPC>
Contexto: andar, sala, quando aparece
Texto de abertura (2–4 linhas)
Opções:
  [1] ... → efeito (flag/item/xp)
  [2] ... → efeito
Respostas de cada opção (1–3 linhas cada)
Ecos: onde essa escolha volta a aparecer
Flags/itens novos: ...
```

Se ele pedir para **colocar no jogo**, converta para código seguindo `references/padroes-codigo.md`, carregue a skill `andante` para as regras técnicas e rode o smoke test.

## Consistência

- Não contradiga o canon de `references/lore.md`. Se a ideia nova exige mudar algo canônico, pergunte antes.
- Ao criar lore novo que o usuário aprovar, registre em `references/lore.md` (seção "Canon") para as próximas sessões.
- Nomes: itens com artigo implícito e maiúscula (`Escama do Dragão`), flags em `snake_case` sem acento (`guardiao_subornado`).
