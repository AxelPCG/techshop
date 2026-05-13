# Shift-Left: 3 Melhorias Necessárias no PR de Checkout

## Conceito: Shift-Left

**Shift-Left** é uma estratégia de qualidade que move as verificações, testes e validações para o **mais cedo possível** no ciclo de desenvolvimento. Em vez de esperar por testes em staging/produção, validamos problemas durante o desenvolvimento local.

```
Abordagem Tradicional:  DEV → CODE REVIEW → TEST → PROD ⚠️ (problemas descobertos tarde)
Shift-Left:            VALIDATION → DEV → CODE REVIEW → TESTS → PROD ✅ (problemas evitados)
```

---

## 🎯 Melhoria #1: Type Safety (Validação em Tempo de Desenvolvimento)

### Problema Identificado

O PR carece completamente de type hints, permitindo erros em runtime:

```python
# ❌ ATUAL - Sem tipos
def processar_tudo(cart_data, u_data):
    if u_data['vip']:  # ← KeyError em runtime se 'vip' não existir
        print("Aplicando desconto VIP")
    temp = res.json()
    if temp['status'] == 'pagamento_aprovado':  # ← Estrutura desconhecida
        pass
```

### Impacto do Shift-Left

Detectar erros **durante o desenvolvimento** com mypy/pyright, não em produção.

### Solução com Shift-Left

#### 1️⃣ **Definir Modelos Pydantic Tipados**

Arquivo: `src/models.py` (expandir)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal

# Modelos de entrada
class CheckoutRequest(BaseModel):
    """Request validado para checkout"""
    user_id: int
    is_vip: bool = False
    cart_items: List['CartItem']
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "is_vip": True,
                "cart_items": [
                    {
                        "product": {"id": 1, "name": "Laptop", "price": 2000.00},
                        "quantity": 1
                    }
                ]
            }
        }

# Modelos de resposta
class PaymentResponse(BaseModel):
    """Response da API de pagamento (tipado)"""
    status: str  # "pagamento_aprovado" | "pagamento_recusado"
    transaction_id: str
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['pagamento_aprovado', 'pagamento_recusado']:
            raise ValueError('Status inválido')
        return v

class CheckoutResult(BaseModel):
    """Resultado final do checkout (tipado)"""
    success: bool
    transaction_id: Optional[str] = None
    error: Optional[str] = None
```

#### 2️⃣ **Implementar Função com Type Hints**

```python
from typing import Union
from src.models import CheckoutRequest, CheckoutResult, PaymentResponse

def processar_checkout(request: CheckoutRequest) -> Union[CheckoutResult, CheckoutResult]:
    """
    Processa checkout com tipos garantidos.
    
    Args:
        request: Requisição validada pelo Pydantic
        
    Returns:
        CheckoutResult: Resultado tipado (sucesso ou erro)
        
    Raises:
        ValueError: Se dados inválidos (capturado pelo type checker)
    """
    # ✅ Type checker garante que request.is_vip existe e é bool
    # ✅ Type checker garante que response tem 'status' como string
    
    if request.is_vip:  # ← MyPy valida que é bool
        discount = 0.15
    else:
        discount = 0.0
    
    response: PaymentResponse = _call_payment_api(request)
    
    # ✅ Type checker garante que response.status é string
    if response.status == 'pagamento_aprovado':
        return CheckoutResult(
            success=True,
            transaction_id=response.transaction_id
        )
    else:
        return CheckoutResult(
            success=False,
            error="Pagamento recusado"
        )
```

#### 3️⃣ **Ativar Type Checking em Pré-Commit**

Arquivo: `.pre-commit-config.yaml` (criar)

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]
        additional_dependencies: [pydantic]
```

**Benefício:** ❌ Erros detectados **antes de fazer commit**, não depois.

---

## 🎯 Melhoria #2: Segurança Crítica (Validação de Secrets em Staging)

### Problema Identificado

Dados sensíveis hardcoded em código:

```python
# ❌ CRÍTICO - Dados sensíveis expostos
"info_cartao": "XXXX-XXXX-XXXX-1234"  # Nunca deve estar em código
```

### Impacto do Shift-Left

Detectar secrets **antes de fazer push**, usando scanner automático.

### Solução com Shift-Left

#### 1️⃣ **Implementar Scanner de Secrets em Pré-Commit**

Arquivo: `.pre-commit-config.yaml` (adicionar ao anterior)

```yaml
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock
```

#### 2️⃣ **Refatorar para Variáveis de Ambiente**

Arquivo: `src/checkout.py` (refatorado)

```python
import os
from pydantic import BaseSettings

# ❌ ANTES (dados sensíveis em código)
def fake_post(url, json):
    dados_pagamento = {
        "info_cartao": "XXXX-XXXX-XXXX-1234"  # ← Exposto
    }

# ✅ DEPOIS (dados em variáveis de ambiente)
class PaymentConfig(BaseSettings):
    """Configuração de pagamento via variáveis de ambiente"""
    PAYMENT_API_URL: str = os.getenv("PAYMENT_API_URL", "")
    PAYMENT_API_KEY: str = os.getenv("PAYMENT_API_KEY", "")  # Nunca em código
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    
    class Config:
        env_file = ".env.local"  # Git-ignored

def processar_pagamento(dados: CheckoutRequest) -> CheckoutResult:
    """Usa credenciais de variáveis de ambiente"""
    config = PaymentConfig()
    
    # ✅ Credenciais não estão em código
    response = requests.post(
        url=config.PAYMENT_API_URL,
        headers={"Authorization": f"Bearer {config.PAYMENT_API_KEY}"},
        json={
            "user_id": dados.user_id,
            "amount": dados.total_amount
            # ❌ NUNCA enviar dados de cartão direto
        }
    )
```

#### 3️⃣ **Configurar Git para Bloquear Secrets**

Arquivo: `.gitignore` (verificar/criar)

```
# ❌ Nunca commitar
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

**Benefício:** ❌ Dados sensíveis **bloqueados antes de push** pela validação automática.

---

## 🎯 Melhoria #3: Validação de Arquitetura (Enforcement de SOLID)

### Problema Identificado

Função gigante viola **Single Responsibility Principle**:

```python
# ❌ 65 linhas fazendo 6 coisas diferentes
def processar_tudo(cart_data, u_data):
    # 1. Validação de estoque
    # 2. Cálculo de preço
    # 3. Aplicação de desconto
    # 4. Chamada de API
    # 5. Tratamento de erro
    # 6. Logging
```

### Impacto do Shift-Left

Validar estrutura arquitetônica **durante revisão de código automática**, não em production.

### Solução com Shift-Left

#### 1️⃣ **Definir Serviços Separados por Responsabilidade**

Arquivo: `src/services/stock_service.py` (criar)

```python
from typing import List
from src.models import CartItem

class StockService:
    """Validação de estoque - responsabilidade única"""
    
    def __init__(self, warehouse_api):
        self.warehouse_api = warehouse_api
    
    def validate_stock(self, items: List[CartItem]) -> tuple[bool, str]:
        """
        Valida se há estoque suficiente.
        
        Returns:
            (bool: tem_estoque, str: mensagem_erro)
        """
        for item in items:
            available = self.warehouse_api.get_stock(item.product.id)
            if available < item.quantity:
                return False, f"Estoque insuficiente para {item.product.name}"
        
        return True, ""
```

Arquivo: `src/services/pricing_service.py` (criar)

```python
from decimal import Decimal
from src.models import CartItem

class PricingService:
    """Cálculo de preços e descontos - responsabilidade única"""
    
    DISCOUNT_TIERS = {
        1000: 0.20,  # 20% acima de R$ 1000
        500: 0.10,   # 10% acima de R$ 500
    }
    VIP_DISCOUNT = 0.15
    SHIPPING_COST = Decimal('15.50')
    
    def calculate_total(self, items: List[CartItem]) -> Decimal:
        """Calcula total sem desconto"""
        return sum(
            Decimal(str(item.product.price)) * item.quantity 
            for item in items
        )
    
    def apply_discount(self, total: Decimal, is_vip: bool) -> Decimal:
        """
        Aplica desconto baseado em regras de negócio.
        
        Rules:
        - VIP: 15% de desconto
        - Acima de 1000: 20% de desconto
        - Acima de 500: 10% de desconto
        """
        if is_vip:
            return total * Decimal(str(1 - self.VIP_DISCOUNT))
        
        for threshold, discount in sorted(self.DISCOUNT_TIERS.items(), reverse=True):
            if total > threshold:
                return total * Decimal(str(1 - discount))
        
        return total
    
    def calculate_final_total(
        self, 
        items: List[CartItem], 
        is_vip: bool
    ) -> Decimal:
        """Calcula total com frete e desconto"""
        subtotal = self.calculate_total(items)
        discounted = self.apply_discount(subtotal, is_vip)
        return discounted + self.SHIPPING_COST
```

Arquivo: `src/services/payment_service.py` (criar)

```python
from typing import Tuple, Optional
from src.models import CheckoutRequest, CheckoutResult

class PaymentService:
    """Processamento de pagamento - responsabilidade única"""
    
    def __init__(self, payment_gateway, config):
        self.gateway = payment_gateway
        self.config = config
    
    def process_payment(
        self, 
        user_id: int, 
        amount: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Processa pagamento de forma segura.
        
        Returns:
            (bool: sucesso, str: transaction_id ou erro)
        """
        try:
            response = self.gateway.charge(
                user_id=user_id,
                amount=amount,
                # ❌ Nunca enviar dados de cartão direto
            )
            
            if response.status == 'approved':
                return True, response.transaction_id
            else:
                return False, "Pagamento recusado pela instituição"
                
        except Exception as e:
            return False, f"Erro ao processar pagamento: {str(e)}"
```

#### 2️⃣ **Orquestrador Central (CheckoutService)**

Arquivo: `src/services/checkout_service.py` (criar)

```python
from src.models import CheckoutRequest, CheckoutResult
from src.services.stock_service import StockService
from src.services.pricing_service import PricingService
from src.services.payment_service import PaymentService

class CheckoutService:
    """Orquestra o checkout - coordena serviços, não implementa lógica"""
    
    def __init__(
        self,
        stock_service: StockService,
        pricing_service: PricingService,
        payment_service: PaymentService
    ):
        self.stock = stock_service
        self.pricing = pricing_service
        self.payment = payment_service
    
    def process(self, request: CheckoutRequest) -> CheckoutResult:
        """
        Processa checkout orquestrando serviços injetados.
        Cada serviço tem uma responsabilidade.
        """
        # Passo 1: Validar estoque
        has_stock, error = self.stock.validate_stock(request.cart_items)
        if not has_stock:
            return CheckoutResult(success=False, error=error)
        
        # Passo 2: Calcular preço
        total = self.pricing.calculate_final_total(
            request.cart_items,
            request.is_vip
        )
        
        # Passo 3: Processar pagamento
        success, transaction_id_or_error = self.payment.process_payment(
            user_id=request.user_id,
            amount=float(total)
        )
        
        if success:
            return CheckoutResult(
                success=True,
                transaction_id=transaction_id_or_error
            )
        else:
            return CheckoutResult(
                success=False,
                error=transaction_id_or_error
            )
```

#### 3️⃣ **Validação de Arquitetura com Pytest**

Arquivo: `tests/test_architecture.py` (criar)

```python
import pytest
from src.services.checkout_service import CheckoutService
from src.services.stock_service import StockService
from src.services.pricing_service import PricingService
from src.services.payment_service import PaymentService

class TestArchitectureCompliance:
    """Valida que cada serviço segue SRP"""
    
    def test_stock_service_has_single_responsibility(self):
        """StockService deve testar APENAS estoque"""
        service = StockService(warehouse_api=MockWarehouse())
        
        # ✅ Só deveria ter métodos relacionados a estoque
        assert hasattr(service, 'validate_stock')
        assert not hasattr(service, 'calculate_price')
        assert not hasattr(service, 'process_payment')
    
    def test_pricing_service_has_single_responsibility(self):
        """PricingService deve calcular APENAS preços"""
        service = PricingService()
        
        # ✅ Só deveria ter métodos relacionados a pricing
        assert hasattr(service, 'calculate_total')
        assert hasattr(service, 'apply_discount')
        assert not hasattr(service, 'validate_stock')
        assert not hasattr(service, 'process_payment')
    
    def test_payment_service_has_single_responsibility(self):
        """PaymentService deve processar APENAS pagamento"""
        service = PaymentService(gateway=MockGateway(), config={})
        
        # ✅ Só deveria ter métodos relacionados a pagamento
        assert hasattr(service, 'process_payment')
        assert not hasattr(service, 'calculate_price')
        assert not hasattr(service, 'validate_stock')
    
    def test_checkout_service_is_orchestrator(self):
        """CheckoutService não implementa lógica, apenas orquestra"""
        checkout = CheckoutService(
            stock_service=StockService(MockWarehouse()),
            pricing_service=PricingService(),
            payment_service=PaymentService(MockGateway(), {})
        )
        
        # ✅ Deveria injetar dependências, não criá-las
        assert checkout.stock is not None
        assert checkout.pricing is not None
        assert checkout.payment is not None
```

**Benefício:** ❌ Violações de SRP **detectadas em testes automáticos** antes de merge.

---

## 📊 Comparativo: Shift-Left em Ação

| Aspecto | Sem Shift-Left | Com Shift-Left |
|--------|---|---|
| **Detecção de tipo inválido** | Em produção ❌ | Durante dev com mypy ✅ |
| **Descoberta de secrets** | Em log de auditoria de segurança 😱 | Em pré-commit ✅ |
| **Violação de SRP** | Em code review manual 😴 | Em testes automáticos ✅ |
| **Tempo de correção** | Hotfix em produção ⏱️ | Antes de commit 🚀 |
| **Custo** | Alto (incidente de segurança) 💸 | Baixo (feedback automático) ✅ |

---

## ✅ Checklist de Implementação

- [ ] **Melhoria #1 - Type Safety**
  - [ ] Expandir modelos em `src/models.py` com Pydantic
  - [ ] Adicionar type hints em `src/checkout.py`
  - [ ] Configurar `mypy` em `.pre-commit-config.yaml`
  - [ ] Rodar `mypy src/` localmente (validação em dev)

- [ ] **Melhoria #2 - Segurança**
  - [ ] Remover dados sensíveis de `src/checkout.py`
  - [ ] Criar `src/config.py` com `BaseSettings`
  - [ ] Adicionar `detect-secrets` em pré-commit
  - [ ] Criar `.env.example` para documentar variáveis

- [ ] **Melhoria #3 - Arquitetura**
  - [ ] Criar `src/services/stock_service.py`
  - [ ] Criar `src/services/pricing_service.py`
  - [ ] Criar `src/services/payment_service.py`
  - [ ] Criar `src/services/checkout_service.py`
  - [ ] Criar `tests/test_architecture.py`
  - [ ] Rodar testes de arquitetura em CI/CD

---

## 🔗 Referências

- [Shift-Left Security](https://www.devsecops.org/shift-left/)
- [MyPy Static Type Checker](https://www.mypy-lang.org/)
- [Pydantic Data Validation](https://docs.pydantic.dev/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Pre-commit Framework](https://pre-commit.com/)

---

**Documento criado em:** 2026-05-12  
**Responsável:** Arquitetura de Software  
**Status:** Em implementação
