# Code Review — cart.py & models.py

## Falhas corrigidas

### Segurança
- `price` e `quantity` agora rejeitam valores `<= 0` via `field_validator` do Pydantic
- Guarda explícita em `add_item` impede quantidade inválida antes de acessar a lista

### Tipagem
- `float` → `Decimal` em `Product.price` (precisão financeira)
- `List[T]` → `list[T]` nativo (Python 3.12+)
- Retornos `-> None` explícitos em `add_item` e `remove_item`
- `calculate_total` e `calculate_total_with_discount` retornam `Decimal`

### Estrutura (SOLID)
- `DiscountCalculator` extraído de `ShoppingCart` (SRP): regras de desconto isoladas e injetáveis
- Magic numbers (`500`, `1000`, `0.80`, `0.90`) substituídos por constantes nomeadas

## Shift Left — documentado no PRD

| ID | Prática |
|---|---|
| SL-001 | `mypy --strict` obrigatório no CI, bloqueia merge |
| SL-002 | Cobertura mínima 80% nos módulos de domínio, padrão AAA |
| SL-003 | Validação de contrato Pydantic na borda antes de integrações externas |

## Arquivos alterados

- `src/models.py` — validadores, `Decimal`, `frozen=True`
- `src/cart.py` — `DiscountCalculator`, constantes, tipagem corrigida
- `docs/PRD.md` — seção Shift Left adicionada
