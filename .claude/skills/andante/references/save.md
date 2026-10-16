# Formato de save do Andante

## O que o código grava de verdade

`save_idle.txt` (via `salvar_man()`, opções 7/9 do menu):
```
# RPG Idle Save
Nome:Hermes
Classe:Guerreiro
Idade:30
Andar:1
Nivel:1
XP:0
Vida:120
Ouro:0
Mana:125
Atributos:F=10 D=10 I=10 V=10 C=10
```

`save_auto_idle.txt` (via `auto_salvar()`, toda volta do menu): mesmo formato sem `Atributos`, com `Passivas:a,b,c`.

Regras do parser (`carregar_man()` e bloco de auto-load em `menu()`):
- Uma chave por linha, `Chave:valor`, comparação por `linha.startswith("Chave:")`.
- `Nivel` **sem acento**. Valores numéricos precisam ser inteiros puros.
- `carregar_man()` lê só `Andar, Nivel, XP, Vida, Idade`; o auto-load lê também `Nome, Classe, Ouro, Mana`.
- Não são carregados hoje: atributos, passivas, flags, inventário, feitiços.

## O que a documentação promete (e ainda não existe)

`CLAUDE.md`/`DOCUMENTACAO.md` descrevem um save em Markdown com checkboxes (`- [x] pescador_falado`) e bloco `Inventário:`. Se o usuário pedir para "ativar flag no save", explique que isso precisa ser implementado primeiro.

## Como estender sem quebrar saves antigos

1. **Adicione** linhas novas; não renomeie as existentes (saves antigos continuam válidos).
2. Formato sugerido, compatível com o parser linha-a-linha e legível no GitHub:
   ```
   ## Flags
   - [x] pescador_falado
   - [ ] portao_aberto
   ## Inventário
   - Poção de Vida: 2
   ```
   Parse: `re.match(r"- \[( |x)\] (\w+)", linha)` e `re.match(r"- (.+): (\d+)", linha)`.
3. No load, campo ausente = manter o padrão do `Jogador()` (não falhar).
4. Sempre `open(..., encoding="utf-8")` em leitura e escrita.
5. Após load, chamar `_recalcular()` e `_desbloquear_passivas()`.
6. Teste: salvar → editar à mão → carregar → conferir (o `scripts/smoke_test.py` já faz um ciclo salvar/carregar).
