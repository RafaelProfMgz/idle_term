# Formato de save do Andante

Arquivos ficam **sempre ao lado do `andante.py`** (`PASTA_JOGO`), de onde quer que o jogo seja aberto:
- `save_auto_idle.txt` — gravado a cada volta do menu, a cada 10 passos do idle e ao sair do idle
- `save_idle.txt` — save manual (menu 7, menu 9, Porto 6); carregado pelo menu 8

Os dois usam o mesmo formato (`texto_save()`) e o mesmo leitor (`ler_save()`):

```
# Auto Save — Andante
Nome: Hermes
Classe: Guerreiro
Idade: 30
Volta: 1
Andar: 2
Nivel: 4
XP: 37
Vida: 180
Mana: 140
Ouro: 230
Pontos: 0
Atributos: F=12 D=10 I=10 V=12 C=10
Passivas: Regeneração
UltimoAcesso: 1792175855

## Flags
- [x] pescador_falado
- [ ] portao_aberto

## Inventário
- Poção de Vida: 3
- Crista do Goblin: 1
```

## Regras do leitor
- Linha `- [x] nome` / `- [ ] nome` → flag. Linha `- Item: número` → inventário (se houver itens no arquivo, substitui o inventário).
- Demais linhas: `Chave: valor`. `Nivel` e `Nível` são aceitos; `Vida: 120/165` também (pega o número antes da `/`).
- Chave ausente ou valor inválido → mantém o padrão (não quebra o load).
- `Andar` é limitado a 1–5. `Classe` define os feitiços (`FEITICOS_CLASSE`).
- Depois de ler: `xp_max = xp_para_nivel(nivel)`, `_recalcular()`, `_desbloquear_passivas()`, `aplicar_flags_de_progresso()` (quem está no Andar 3 ganha as flags dos chefes 1 e 2).
- `UltimoAcesso` (epoch) alimenta o progresso offline ao reabrir o jogo.

## Ao estender
1. **Adicione** chaves novas em `texto_save()` e um ramo em `ler_save()`; não renomeie as existentes (saves antigos continuam válidos).
2. Sempre `encoding="utf-8"`.
3. Teste: o `scripts/smoke_test.py` faz salvar → carregar e confere flags e inventário.
