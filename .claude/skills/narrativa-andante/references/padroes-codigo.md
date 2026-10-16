# Como colocar narrativa no andante.py

## Diálogo com escolha (modelo)

Siga o estilo de `dialogo_guardiao()` / `dialogo_pescador()` (chamados por `cena_explorar()`): `digitar()` para fala/narração, `print()` para opções, `input().strip()` para a escolha, flag checada para não repetir recompensa.

```python
def dialogo_guardiao(jogador):
    limpar()
    digitar("=== PORTÃO DO CASTELO ===")
    digitar("Um homem de armadura enferrujada bloqueia a ponte levadiça.")
    digitar('Guardião: "Ninguém passa sem ordem do Rei. E o Rei não dá ordens há anos."')
    if jogador.flags.get("portao_aberto"):
        digitar('Guardião: "Você de novo. Passe, antes que eu mude de ideia."')
        pausa(); return
    print("[1] Mostrar o Manuscrito Antigo")
    print("[2] Desafiar o Guardião")
    print("[3] Ir embora")
    es = input("Escolha: ").strip()
    if es == "1" and jogador.inven.get("Manuscrito Antigo", 0) > 0:
        digitar("Ele lê em silêncio. A mão que segura a lança treme.")
        digitar('Guardião: "Essa letra... é do Rei. Vá."')
        jogador.flags["portao_aberto"] = True
        jogador.flags["manuscrito_lido"] = True
        jogador.dialogo_positivo += 1
        jogador.ganhar_xp(15)
        digitar("[🚪 PORTÃO ABERTO] O caminho para a Caverna está livre.")
    elif es == "2":
        if combate(jogador, "Guardião Real", 60, 12):
            jogador.flags["portao_aberto"] = True
    pausa()
```

## Checklist

- [ ] Fala com `digitar()`, opções com `print("[n] ...")`
- [ ] Linhas ≤ ~70 colunas
- [ ] Recompensa protegida por flag (não dá para farmar repetindo o diálogo)
- [ ] Flag nova adicionada em `self.flags` no `Jogador.__init__`
- [ ] Diálogo ligado a `cena_explorar()` (por andar) e descrição em `CENAS`
- [ ] Escolha positiva chama `jogador.dialogo_bom()` (conta para a conquista Diplomata)
- [ ] Se a flag destrava andar, conferir `ANDARES[n]["req_flag"]`
- [ ] Precisa acontecer no modo idle também? Flag que trava andar → `HISTORIA` (o idle ativa sozinho); fala de ambiente → `FALAS_IDLE[andar]`
- [ ] Rodar `python3 .claude/skills/andante/scripts/smoke_test.py`
- [ ] Registrar lore aprovada em `references/lore.md`

## Eventos curtos do modo idle

Onde ficam: `FALAS_IDLE[andar]` (8 por andar, ambiente), `TRABALHOS[andar]` (1 por andar), `ENCONTROS` (raros, com `ouro`/`xp` por andar ou `cura` em % da vida). Comece cada linha com um emoji e mantenha ≤ 70 colunas — o painel mostra 7 linhas.

O modo idle mostra uma linha por evento (painel com os 8 últimos). Escreva variações em lista e sorteie com `random.choice`, para o idle não ficar repetitivo:

```python
FALAS_PORTO = [
    "Um gato rouba um peixe da sua bolsa. Você deixa.",
    "O sino do porto toca três vezes. Ninguém sabe por quê.",
]
```
