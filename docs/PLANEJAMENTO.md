# PLANEJAMENTO.md — Expansão do Andante (v3)

> Proposta de 2026-10-19. Nada aqui é canon nem está implementado: é o mapa do que construir, em que ordem e como cada sistema se liga aos outros. Itens marcados com 💡 são sugestão de lore e precisam de aprovação antes de virar canon (ver `narrativa-andante/references/lore.md`).

## 0. Princípios

1. **Tudo destrava aos poucos.** O jogador começa só com a torre e o idle. Cada sistema novo aparece no menu como `???` e é revelado num marco (seção 1).
2. **Idle primeiro.** Todo sistema precisa funcionar sozinho no modo idle (auto-equipar, auto-missão, auto-dungeon), e de um jeito um pouco melhor com o jogador olhando (escolhas, rolagens manuais).
3. **Roleplay por consequência.** Recompensas, missões e personagens deixam marcas: flags no save, linhas no Diário, falas de NPC que mudam.
4. **Save continua `.txt` editável.** Cada sistema ganha um bloco `## ...` legível (seção 12).
5. **Sem dinheiro real.** O gacha usa só moeda ganha jogando.

---

## 1. Espinha da progressão: o que destrava e quando

É a peça central. Os outros sistemas ficam pendurados nela.

| Marco | Destrava | Aviso na tela |
|---|---|---|
| Início | Torre (Andares 1-5), idle, Explorar | — |
| Nv 3 | **Forja** (hoje já vem aberta) | "O ferreiro acende a forja pela primeira vez." |
| Primeiro item Raro | **Inventário de equipamento** + raridades | "Algo brilha azul entre os despojos." |
| Vencer o Goblin Sombrio | **Contratos do Porto** (missões diárias) | Quadro de avisos aparece no cais |
| Nv 8 | **Pontos de habilidade** + árvore da classe (ramo 1) | "Você sente o corpo aprender sozinho." |
| Vencer o Guardião Real | **Sino do Porto** (gacha) + 1º companheiro garantido | O sino toca três vezes (fecha o mistério do `FALAS_IDLE`) |
| Nv 12 | **Dungeons** (1ª: Galerias Afogadas) | — |
| Fim da Volta 1 | **Altar** (hoje já vem aberto) + **Mapa aberto** (Arquipélago) | "A torre gira. Lá fora, o mar recua." |
| Nv 20 | Ramo 2 da árvore + 2º espaço de companheiro | — |
| Volta 2 | Dificuldades **Heroica** nas dungeons; **Botas** na Forja | — |
| Nv 30 | **Subclasse** (escolha permanente) | Missão de história da classe |
| Volta 3 | **Torre Infinita** + **Torre Afogada** | — |
| Nv 50 | Ramo 3 da árvore + 3º companheiro | — |
| Nv 60 | **Despertar** (limite de nível sobe; seção 2) | — |
| Volta 5 | **Torre de Vidro** (desafio de regras) | — |

**No menu:** opções bloqueadas aparecem como `[?] ???  (Nv 12)` em cinza. Ver o que falta já dá motivo para continuar.

**Implementação:** um dict `DESBLOQUEIOS = {"contratos": {"flag": "goblin_derrotado"}, "dungeons": {"nivel": 12}, ...}`, uma função `desbloqueado(jogador, chave)` e uma lista `jogador.revelados` salva no `.txt`. Quando um item entra pela primeira vez nessa lista, sai o aviso ★.

---

## 2. Mais níveis: curva em três faixas

Hoje o nível não tem limite e a curva `35 * n^2.7` cresce sem um marco no meio. Proposta:

| Faixa | Níveis | Como se ganha | Recompensa por nível |
|---|---|---|---|
| **Mortal** | 1-60 | XP normal | atributos + 1 ponto de habilidade |
| **Desperto** | 61-120 | XP ×1,5 de exigência; destrava no Nv 60 com a missão "O Segundo Fôlego" | +1 ponto de habilidade a cada 2 níveis + nó de "Despertar" |
| **Maestria** | ∞ (depois do 120) | barra separada; nunca para | +0,5% em um status à escolha (estilo paragon) |

- **Marcos de nível** (10, 20, 30...) dão um baú garantido e uma linha no Diário.
- **Nível de companheiro** e **nível de habilidade** são barras separadas: há sempre alguma subindo.
- Medir o ritmo com `scripts/ritmo.py`. Alvo: Nv 60 em cerca de 10 h de idle e Nv 120 em cerca de 60 h.

---

## 3. Recompensas aleatórias com ranks (loot)

### Ranks
| Rank | Cor | Chance base | Afixos | Lore? |
|---|---|---|---|---|
| **F Comum** | branco | 60% | 0 | — |
| **E Incomum** | verde | 25% | 1 | — |
| **D Raro** | azul | 10% | 2 | frase curta |
| **C Épico** | roxo | 4% | 3 | frase + origem |
| **B Lendário** | dourado | 0,9% | 3 + efeito único | história própria |
| **A Mítico** | vermelho piscando | 0,1% (só chefes/dungeon Pesadelo) | 4 + efeito único | entrada no Diário |

A sorte (Forja "Moeda da Sorte", passivas e companheiros) desloca as chances para cima. Há **piedade**: 60 abates sem Épico garantem um Épico.

### Itens gerados para roleplay
Nome = `base + sufixo` + uma **origem** sorteada do andar ou da dungeon:

> **Lâmina do Afogado** [Épico] — +38 ATQ, +5% ouro, +3% crítico
> *"Encontrada presa nas redes do cais. O cabo ainda está molhado."*

- 7 espaços de equipamento: arma, elmo, peito, botas, anel, amuleto, relíquia.
- O idle **equipa sozinho** o que tiver mais Poder. O que sobra vira ouro (venda automática, já existe) ou **Pó de Forja** (nova moeda para rerrolar afixos).
- **Conjuntos** (2/4 peças) por andar ou dungeon: "Vestes do Templo (2): Cura +20%".
- **Itens com memória**: um Lendário guarda quantos chefes matou e ganha +1% a cada 100 (máx. +10%). Isso cria apego ao item.

### Baús
Bronze, Prata, Ouro e Abissal. Caem de marcos, contratos e dungeons. Abrir mostra uma animação curta com o rank "subindo" (F → E → D → ...) antes de parar. É o momento de suspense.

---

## 4. Missões

| Tipo | Quantas | De onde vem | Exemplo |
|---|---|---|---|
| **História** | 1 cadeia por andar ou região | lore principal | "O Mar Escuro" finalmente termina no Abismo |
| **Secundárias de NPC** | 2-3 por região | diálogos com escolha | Padeira: "Leve pão ao Guardião" → amizade ou suborno |
| **Contratos do Porto** | 3 ativos, renovam a cada 4 h | quadro de avisos | "Derrote 40 monstros na Caverna", "Junte 50K de ouro" |
| **Pessoais** | 1 cadeia por companheiro | gacha (seção 6) | destrava o capítulo de lore e a habilidade final |
| **Exploração** | por região do mapa | mapa aberto | "Encontre os 3 faróis apagados" |
| **Desafios** | fixas | conquistas | "Vença um chefe com Poder < 1,2" |

- Formato de dado: `MISSOES = {"id": {"tipo", "req": {...}, "objetivo": {"tipo": "matar", "alvo": "andar:3", "qt": 40}, "recompensa": {...}, "flags_fim": [...], "escolhas": [...]}}`.
- **Escolhas com consequência**: uma missão pode terminar de dois jeitos (flags `padeira_amiga` ou `padeira_traida`), o que muda preços, falas e quais companheiros aparecem no sino.
- No idle, as missões andam sozinhas. Quando chega uma escolha, o idle pausa por 10 s com `[1] [2]` e decide sozinho se ninguém responder (ideia 6 de `suculencias.md`).
- O **Diário de Bordo** (tela nova) lista missões feitas, escolhas tomadas e páginas do Manuscrito. É o "livro" do personagem.

---

## 5. Sistema de recompensa (camada geral)

- **Marcos de nível e de volta**: baús garantidos.
- **Retorno diário**: ao abrir o jogo depois de mais de 8 h, ganha um "Presente do Porto" (escala por sequência de 7 dias, sem punir quem falta: a sequência só pausa).
- **Passe da Torre** (sem pagamento): 30 degraus por temporada de 2 semanas reais. Sobe com XP de temporada ganho no idle e dá conchas, baús e cosméticos (títulos e molduras ASCII).
- **Conquistas**: expandir de 8 para cerca de 40 em categorias (Combate, Coleção, História, Exploração, Excentricidades). Cada uma dá **Pontos de Lenda**, que somados destravam títulos novos.
- **Coleção / Bestiário**: matar 50 de cada monstro revela a descrição dele e dá +1% de dano contra ele.
- **Recordes**: volta mais rápida, maior dano, maior rank encontrado.

---

## 6. Gacha de personagens: o Sino do Porto

### Mecânica
- **Moeda:** **Conchas do Mar Escuro**, de missões, conquistas, chefes, Passe e retorno diário. Nunca compradas.
- **Tocar o sino:** 1× = 10 conchas, 10× = 90 conchas (com 1 ★4+ garantido).
- **Raridades:** ★3 (85%), ★4 (13%), ★5 (2%). **Piedade** em 60 toques para ★4 e 90 para ★5. O contador fica salvo no `.txt`.
- **Banner em destaque** muda a cada volta. Isso reaproveita a mecânica de voltas que já existe.
- **Repetidos** viram **Memórias** (até 5 por personagem). Cada Memória destrava um **capítulo de lore** e um bônus. A coleção é contada como história, não só como número.

### Ficha de um companheiro
```
Nome · Rank ★ · Função (Tanque/Dano/Suporte/Coleta) · Elemento
Passiva de grupo · Habilidade ativa (cooldown em turnos) · Afinidade (0-10)
Lore: 5 capítulos (1 inicial + 1 por Memória)
Missão pessoal (afinidade 5) → destrava a habilidade final
Falas próprias no idle
```
- **Grupo:** até 3 companheiros (os espaços destravam pela seção 1). Eles agem no combate automático e dão passivas.
- **Afinidade** sobe ao lutar junto e ao dar presentes (itens de loot). Em 10, revela o último segredo.

### Elenco inicial sugerido 💡 (ligado aos fios soltos do lore)
| ★ | Nome | Função | Gancho de lore |
|---|---|---|---|
| ★5 | **Maré**, a filha do Pescador | Suporte/Água | Sumiu no Mar Escuro; é o porquê de o Pescador ter a chave. Fecha a missão "O Mar Escuro". |
| ★5 | **O Primeiro Andante** | Dano/Sombra | Autor do Manuscrito. Cada Memória é uma página que faltava. |
| ★5 | **Rei sem Coroa** | Tanque/Luz | O Rei do Castelo antes de virar (ou não) o Rei das Sombras. |
| ★4 | **Brasa**, filhote de dragão | Dano/Fogo | Sobreviveu ao Dragão Antigo; cresce com a afinidade. |
| ★4 | **Irmã Vela**, acólita cega | Cura/Luz | Reza nomes que nunca ouviu, inclusive o seu. |
| ★4 | **Ferreiro Osso** | Coleta/Terra | O ferreiro da Forja: "Ouro primeiro, conversa depois." Desconto na Forja. |
| ★4 | **Corvo** | Sorte | Trazia moedas antigas: +chance de rank. |
| ★3 | **Padeira Lua** | Cura | O pão que "ninguém sabe como chegou". |
| ★3 | **Três Ossos** (os esqueletos dos dados) | Sorte/Ouro | Contam como um só; apostam sua recompensa (×0 a ×3). |
| ★3 | **Mercador Troco** | Ouro | Erra o troco a seu favor. Sempre. |
| ★3 | **Soldado Fantasma** | Tanque | Ainda espera ordens do Rei. |
| ★3 | **Kobold Mineiro** | Coleta | Acha Pó de Forja nas dungeons. |

---

## 7. Habilidades mais detalhadas

### Árvore por classe: 3 ramos × 8 nós
| Classe | Ramo 1 | Ramo 2 | Ramo 3 |
|---|---|---|---|
| Guerreiro | **Muralha** (DEF, contra-ataque) | **Fúria** (dano crescente com vida baixa) | **Comando** (fortalece companheiros) |
| Mago | **Chama** (Bola de Fogo em cadeia, queimadura) | **Maré** (gelo/água, lentidão) | **Arcano** (mana, escudos) |
| Arqueiro | **Precisão** (crítico) | **Rastro** (ouro/loot, armadilhas) | **Vento** (ações extras, esquiva) |

- **Pontos de habilidade:** 1 por nível (seção 2). **Reset** custa ouro, ou é grátis uma vez por volta.
- **Nós passivos** (+% simples) e **nós-chave** (mudam a regra: "Bola de Fogo ricocheteia em 2 alvos").
- **Habilidades ativas** com **cooldown em turnos** e **rank I-V**, que sobem com o uso (habilidade usada 500× vira rank II). Substituem a lógica atual de `FEITICOS`, que é só custo de mana.
- **Subclasse no Nv 30** (missão própria): Guerreiro → *Paladino do Cais* / *Berserker*; Mago → *Maremante* / *Necromante das Velas*; Arqueiro → *Batedor* / *Atirador do Farol*.
- **Elementos:** Fogo, Água, Terra, Luz e Sombra, com fraquezas por monstro e chefe (ex.: Dragão resiste a Fogo, fraco a Água). Isso dá motivo para trocar de companheiro e de equipamento.
- **Sinergias:** companheiro + nó-chave ("Brasa + ramo Chama = queimadura dupla").
- No idle, o jogador define uma **rotação** (ordem de prioridade das ativas), salva no `.txt`.

---

## 8. Dungeons

Instâncias fora da torre: N salas em sequência, eventos entre as salas e chefe no fim.

| Dungeon | Req | Salas | Tema / loot |
|---|---|---|---|
| Galerias Afogadas | Nv 12 | 6 | Água; conjunto "Do Afogado" |
| Cripta do Quartel | Guardião Real | 8 | Fantasmas; anéis |
| Forja Esquecida | Nv 25 | 8 | Fogo; Pó de Forja em dobro |
| Biblioteca Submersa | Volta 2 | 10 | Luz/Sombra; páginas do Manuscrito |
| Ninho de Brasa | missão da Brasa | 10 | só abre com a Brasa no grupo |
| Coração do Abismo | Volta 3 | 12 | Mítico possível |

- **Dificuldades:** Normal / Heroica (Volta 2) / Pesadelo (Volta 4). Cada uma dá +1 rank de loot.
- **Tochas** (energia): 1 entrada por tocha, recarga de 1 a cada 30 min, inclusive offline. Isso impede farmar sem parar e dá motivo para voltar ao jogo.
- **Modificadores semanais**: "Sem cura", "Inimigos explodem ao morrer", "+100% ouro".
- **Salas especiais**: baú trancado (arriscar), altar (trocar vida por buff), NPC preso (missão secundária).
- No idle, a opção "Auto-dungeon" gasta as tochas sozinha quando o Poder for maior que 1,3.

---

## 9. Torres diferentes

| Torre | Destrava | Regra própria | Recompensa |
|---|---|---|---|
| **Torre do Andante** (atual) | início | voltas cada vez mais difíceis | progresso principal, fragmentos |
| **Torre Infinita** | Volta 3 | andares gerados a partir do 6 ("Andar 17: Biblioteca Submersa"), sem fim | recorde pessoal, conchas a cada 10 andares |
| **Torre Afogada** 💡 | Volta 3 | é **descida**: cada andar tira 5% da vida máxima até o fim | loot Água, Memória da Maré |
| **Torre de Vidro** | Volta 5 | cada andar tem uma **regra** ("só magia", "um golpe só", "sem companheiros") | títulos raros, nós de habilidade extras |
| **Torre do Tempo** | Nv 60 | muda toda semana (bioma + chefe + modificador) | cosméticos e Passe |

Implementação: generalizar `ANDARES` para `TORRES = {"andante": {...andares...}, "infinita": {"gerador": gerar_andar}, ...}` e guardar `jogador.torre_atual`. O idle continua rodando na torre escolhida.

---

## 10. Mapa aberto: o Arquipélago do Mar Escuro

O Porto deixa de ser só o Andar 1 e vira o **centro de um mapa** que se revela aos poucos.

```
        ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
      ~  ▓▓▓  Ilha do Farol  ? ? ? ~
     ~   ▓F▓       (Nv 20)  ? ? ?  ~
     ~    │                         ~
     ~  ┌─┴──┐   ≈≈≈≈   ┌────┐       ~
     ~  │ ⌂P │───≈≈≈≈───│ ♜T │ Torre ~
     ~  └─┬──┘  Baía    └────┘       ~
     ~    │   Brumosa                ~
     ~  ▒▒▒▒▒ Mata Velha  ░░░ ? ? ?  ~
     ~  ▒ D ▒  (Nv 12)    ░ Pântano  ~
      ~ ▒▒▒▒▒             ░ (missão) ~
        ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
  ⌂ vila  ♜ torre  D dungeon  F farol  ? névoa (não explorado)
```

- **Grade de regiões** com **névoa**: o jogador anda (WASD ou números) e cada casa visitada se revela.
- **Regiões** destravam por **nível** ou **missão**:

| Região | Req | Conteúdo |
|---|---|---|
| Porto & Baía Brumosa | início | Forja, Sino, quadro de contratos |
| Mata Velha | Nv 12 | Galerias Afogadas, recursos |
| Pântano dos Sinos | missão "O sino tocou três vezes" | NPCs, Torre do Tempo |
| Ilha do Farol | Nv 20 + barco (missão do Pescador) | Torre Afogada, Maré |
| Ruínas do Reino | Volta 2 | Cripta, Rei sem Coroa |
| Fossa do Abismo | Volta 3 | Coração do Abismo, Torre Infinita |

- **Pontos de interesse:** vila, dungeon, torre, NPC, recurso coletável (rende no idle), evento aleatório, segredo (só aparece com certo companheiro).
- **Viagem** custa tempo de jogo. No idle, a opção "Explorar o mapa" revela casas sozinha e coleta recursos.
- **Exploração %** por região dá recompensa em 25/50/75/100%.
- É aqui que entram os diálogos novos do Templo e do Abismo, que já estão nos planos.

---

## 11. Arquitetura (antes de crescer)

`andante.py` tem 1.682 linhas e esses sistemas devem triplicar isso. Proposta, mantendo o comando `python3 andante.py`:

```
andante.py            # só inicia o jogo (menu)
andante/
  dados/              # tabelas puras: andares, monstros, itens, companheiros, missões, mapa, falas
  nucleo/jogador.py   # Jogador + _recalcular
  nucleo/combate.py
  sistemas/           # loot, missoes, gacha, habilidades, dungeons, torres, mapa, desbloqueios
  tela/               # desenho do idle, menus, mapa ASCII
  save.py             # texto_save / ler_save por blocos (um por sistema)
```

- Cada sistema expõe `salvar(j) -> linhas` e `carregar(j, bloco)`. Assim o save cresce por blocos sem quebrar o formato.
- O smoke test ganha um caso por sistema. `ritmo.py` mede o balanceamento.
- Dados de lore ficam em `dados/`, para a skill `narrativa-andante` editar sem mexer na lógica.

---

## 12. Save `.txt`: blocos novos (exemplo)

```markdown
## Desbloqueios
- [x] contratos
- [x] gacha
- [ ] dungeons

## Equipamento
- arma: Lâmina do Afogado | Épico | ATQ+38, ouro+5%, crit+3% | abates=212

## Companheiros
- Maré ★5 | Nv 14 | Memórias 1 | Afinidade 6 | grupo
- Brasa ★4 | Nv 20 | Memórias 3 | Afinidade 9 | grupo

## Habilidades
Pontos: 3
- muralha.contra_ataque: 2
Rotação: Bola de Fogo > Escudo Arcano > Impulso

## Missões
- [x] mar_escuro_1 (escolha: contou_a_verdade)
- [ ] contrato: matar andar:3 (27/40)

## Mapa
Revelado: 0-0,0-1,1-1,2-1
Exploração: porto=100, mata_velha=45

## Gacha
Conchas: 140
Piedade4: 12
Piedade5: 47
```

Continua editável à mão: trocar `[ ]` por `[x]` em `## Desbloqueios` já abre o sistema, o que facilita testar.

---

## 13. Roteiro em fases

Cada fase é jogável sozinha e deixa a base pronta para a próxima.

| Fase | Conteúdo | Por que nessa ordem |
|---|---|---|
| **0. Fundação** | separar em módulos (seção 11), `DESBLOQUEIOS` + `???` no menu, save por blocos | sem isso, o resto vira um arquivo de 5 mil linhas |
| **1. Loot com rank + contratos** | seção 3 + Contratos do Porto + baús + Diário | maior ganho de "só mais um pouco"; mexe pouco no balanceamento |
| **2. Habilidades + níveis** | árvores, ativas com cooldown, elementos, faixas de nível, Despertar | dá profundidade ao combate antes de entrar com companheiros |
| **3. Missões de história + gacha** | cadeias por andar, escolhas no idle, Sino do Porto, 12 companheiros, afinidade | precisa do combate da Fase 2 para os companheiros terem papel |
| **4. Mapa aberto + dungeons** | Arquipélago, névoa, regiões, 6 dungeons, tochas | usa missões (Fase 3) para destravar regiões |
| **5. Torres novas + Passe** | Infinita, Afogada, Vidro, Tempo; Passe da Torre; Maestria | endgame: precisa de tudo antes |

Em cada fase: atualizar `docs/DOCUMENTACAO.md`, a skill `andante` (save.md), rodar `smoke_test.py` e `ritmo.py`.

---

## 14. Decisões em aberto (para o usuário)

1. **Ranks:** letras (F-A) ou nomes (Comum-Mítico)? A proposta usa os dois.
2. **Gacha:** banner rotativo por volta ou sino fixo com todos?
3. **Elenco 💡:** aprovar Maré, Primeiro Andante e Rei sem Coroa como canon? Eles respondem as pontas soltas do lore.
4. **Tochas:** limitar dungeons por energia ou deixar ilimitado?
5. **Mapa:** andar casa a casa (WASD) ou viajar por nós (menu de destinos)?
6. **Arquitetura:** pode separar em pacote `andante/`, ou manter arquivo único?

---

## 15. Estado da implementação (parado em 2026-10-19)

Tudo no `andante.py`, que continua sendo um arquivo único, como exige a skill `andante`. Smoke test, regressão (14/14) e todas as telas passam.

### Decisões tomadas (perguntas da seção 14)
1. Ranks com letra e nome (`[C Épico]`).
2. Sino com destaque ★5 que muda a cada volta (Maré → Primeiro Andante → Rei sem Coroa).
3. Elenco 💡 implementado. A lore nova ainda precisa ir para `narrativa-andante/references/lore.md`.
4. Dungeons limitadas por tochas (ainda não implementado).
5. Mapa casa a casa com névoa (ainda não implementado).
6. Arquivo único, sem pacote: é regra da skill do projeto. Cada sistema se pendura em registros: `GANCHOS_IDLE`, `LINHAS_IDLE_EXTRA`, `DICAS_EXTRA`, `OFFLINE_EXTRA`, `BLOCOS_SAVE` e `CHAVES_SAVE`.

### ✅ Feito
- **Fase 0**: `DESBLOQUEIOS` com `???` no menu (`MENU_OPCOES`/`MENU_SECOES`); `evento()` alimenta contadores, contratos, missões e passe; `avisar()`/`drenar_avisos()`; Diário; save por blocos `##` (`_estado_v3()` zera o estado antes de carregar).
- **Fase 1**: loot F→A com afixos, Lendários e Míticos únicos, conjuntos de 2/4 peças, memória dos itens, auto-equipar, pó de forja (rerrolar e atualizar), piedade de 60 itens; baús com animação; contratos do Porto (3 ativos, renovam a cada 4h); Presente do Porto (a cada 20h, sequência de 7 que só pausa); bestiário; recordes; ~20 conquistas novas com Pontos de Lenda e 2 títulos novos; 1 Baú de Bronze por hora offline.
- **Fase 2**: 3 árvores por classe (3 ramos × 8 nós, liberados no Nv 8, 20 e 50); ativas com recarga e rank I-V por uso; rotação; elementos (`ELEMENTO_ANDAR`); subclasse no Nv 30 (o idle escolhe sozinho no 35); reset grátis 1× por volta; teto de nível 60 → 120 (Despertar) → Maestria; marco de nível a cada 10 (Baú de Ouro); `[H]` no combate manual.
- **Fase 3**: 12 companheiros com 5 capítulos de lore, segredo, falas no idle e missão pessoal; Sino (★4 a cada 10, ★5 em 90; o Corvo vem de graça); grupo de 1 a 3 espaços (atacam, usam ativa, dão passiva, ganham XP e afinidade); presentes com pó; missões: O Mar Escuro (4), O Sino, A Padeira e o Guardião, Páginas do Manuscrito (5), O Segundo Fôlego, 12 laços pessoais. Escolhas: o idle espera 10 s por [1]/[2], senão fica o padrão. Ecos das escolhas no Pescador, no Guardião e no Presente.

### ⏳ Falta
- **Fase 4: mapa aberto e dungeons.** Hoje `tela_mapa` e `tela_dungeons` mostram "Em breve" (stubs `_em_breve` perto do fim do arquivo).
  - Mapa já desenhado e validado (36×13; letra = região; minúscula = rota de barco/ponte):
    ```
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ~~RRRRRR~~~~~~~~~~~~~~~~~~~~~~FFFF~~
    ~RRRRRRRR~~~~~~~~~~~~~~~~~~~~FFFFFF~
    ~RRRRRRRRR~~~~~~~~~~~~~~~~~~~FFFFFF~
    ~~RRRRRRRRV~~~~~~~~~~~~~~~~~~~FFFF~~
    ~~~~RRRVVVVPPPPPP~~~~~~~~~~~~~~ff~~~
    ~~~VVVVVVVVPPPPPPPff~~~~~~~~~~ff~~~~
    ~~VVVVVVVVPPPPPPPPPfffffffffffff~~~~
    ~~~VVVVVVVPPPPPPPPP~~~~~~~~~~~~~~~~~
    ~~~~VVVVVSSSPPPPPP~~~~XXXXXX~~~~~~~~
    ~~~~~~SSSSSSSSPPPPx~~XXXXXXXX~~~~~~~
    ~~~~~~~SSSSSSSSSS~xxxxXXXXXXX~~~~~~~
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ```
    Regiões: P Porto (início) · V Mata Velha (Nv 12) · S Pântano dos Sinos (marca `sino_tres`) · F Ilha do Farol (Nv 20 + marca `barco`) · R Ruínas do Reino (Volta 3) · X Fossa do Abismo (Volta 4).
    Pontos de interesse (x,y): Porto (13,7) · Torre (16,5) · dungeons: Galerias (12,9), Cripta (5,3), Forja Esquecida (6,6), Biblioteca (8,11), Ninho (3,1), Coração (25,10) · torres: Infinita (27,11), Afogada (32,2), Vidro (10,10), Tempo (7,4) · faróis (31,3) (33,1) (26,7) · recursos (+2% ouro/XP) (4,8) (15,8) (12,11) (2,2) (30,4) (23,9) · NPCs (9,7) (15,10) (27,9) · segredos com companheiro: Corvo (14,11), Brasa (8,2), Maré (34,2).
  - Falta escrever: névoa (`mapa_visto`), movimento por `input` (wasd), encontros (10%), % explorado por região (prêmios em 25/50/75/100), exploração no idle, missão "Os Três Faróis" (evento `farol`), bloco `## Mapa` no save.
  - Dungeons: 6 (`galerias, cripta, forja, biblioteca, ninho, coracao`); dificuldades Normal, Heroica (desbloqueio `heroica`) e Pesadelo (`pesadelo`); tochas (5 no máximo, +1 a cada 30 min, inclusive offline via `OFFLINE_EXTRA`); salas especiais (baú trancado, altar, prisioneiro, fonte); modificador semanal; auto-dungeon no idle quando o Poder for ≥ 1,3.
  - **Ao terminar:** voltar a gerar os contratos `dungeon` e `casa` em `gerar_contrato()` (há um `TODO`). A missão `mar_escuro_4` ("O Barco") depende do evento `casa`.
- **Fase 5: torres novas e Passe.** `tela_torres` e `tela_passe` são stubs; `ganhar_passe()` é um gancho vazio. Falta Torre Infinita, Afogada, de Vidro e do Tempo (`j.torre_ativa`, o idle roda na torre escolhida), Passe da Torre (30 degraus, temporada de 14 dias) e molduras cosméticas.
- **Balanceamento:** com as fases 1-3 as voltas ficaram ~10-25% mais rápidas (`ritmo.py`). O ouro sobra muito (100K+ parado). Revisar no fim.
- **Docs:** atualizar a skill `andante` (`references/save.md` com os blocos novos, `arquitetura.md`), a lore em `narrativa-andante/references/lore.md` e incluir checagens v3 no `smoke_test.py`.

### Diferenças em relação ao plano acima
- Piedade do Sino: ★4 a cada **10** toques (não 60); ★5 em 90.
- Piedade de loot conta **itens** (60), não abates.
- O Presente do Porto vale a cada **20h** (não 8h).
- Ruínas do Reino na **Volta 3** e Fossa na **Volta 4** (o mapa abre na Volta 2).
- Os `Baús` também viraram desbloqueio (no primeiro baú).
- Nomes de afixos e efeitos: ver `AFIXOS`, `EFEITO_NOME`, `LENDARIOS`, `MITICOS`.
