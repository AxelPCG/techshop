"""Testes de arquitetura e compliance com SOLID.

Valida que cada serviço segue o Single Responsibility Principle
e que a arquitetura está correta.
"""

import pytest
from decimal import Decimal
from src.services.stock_service import StockService
from src.services.pricing_service import PricingService
from src.services.payment_service import PaymentService
from src.services.checkout_service import CheckoutService
from src.models import CartItem, Product, CheckoutRequest, CheckoutResult
from src.config import DiscountConfig, ShippingConfig, PaymentConfig


# Mocks para testes
class MockWarehouse:
    """Mock de warehouse para testes."""

    def __init__(self, stock_available: int = 10) -> None:
        """Inicializa com quantidade disponível fixa.

        Args:
            stock_available: Quantidade de estoque disponível.
        """
        self.stock_available = stock_available

    def get_stock(self, product_id: int) -> int:
        """Retorna quantidade fixa de estoque.

        Args:
            product_id: ID do produto (ignorado).

        Returns:
            int: Quantidade disponível.
        """
        return self.stock_available


class MockPaymentGateway:
    """Mock de gateway de pagamento para testes."""

    def __init__(self, approve: bool = True, transaction_id: str = "txn_123") -> None:
        """Inicializa com comportamento controlado.

        Args:
            approve: Se a transação deve ser aprovada.
            transaction_id: ID da transação a retornar.
        """
        self.approve = approve
        self.transaction_id = transaction_id
        self.last_call = None

    def charge(self, user_id: int, amount: float) -> dict:
        """Processa cobrança mockada.

        Args:
            user_id: ID do usuário.
            amount: Valor a cobrar.

        Returns:
            dict: Resposta mockada.
        """
        self.last_call = {"user_id": user_id, "amount": amount}

        if self.approve:
            return {
                "status": "approved",
                "transaction_id": self.transaction_id
            }
        else:
            return {
                "status": "declined",
                "transaction_id": None
            }


# ============================================================================
# Testes de Responsabilidade Única (SRP)
# ============================================================================

class TestStockServiceResponsibility:
    """Valida que StockService tem apenas responsabilidade de estoque."""

    def test_stock_service_has_single_responsibility(self) -> None:
        """Arrange: Criar serviço de estoque."""
        service = StockService(warehouse_api=MockWarehouse())

        # Act & Assert: Verificar que tem método de estoque
        assert hasattr(service, 'validate_stock')

        # Assert: Verificar que NÃO tem métodos de outras responsabilidades
        assert not hasattr(service, 'calculate_total')
        assert not hasattr(service, 'apply_discount')
        assert not hasattr(service, 'process_payment')

    def test_stock_service_validates_insufficient_stock(self) -> None:
        """Arrange: Criar item com quantidade maior que disponível."""
        warehouse = MockWarehouse(stock_available=5)
        service = StockService(warehouse_api=warehouse)

        product = Product(id=1, name="Laptop", price=Decimal("2000.00"))
        item = CartItem(product=product, quantity=10)

        # Act
        has_stock, error = service.validate_stock([item])

        # Assert
        assert not has_stock
        assert "insuficiente" in error.lower()

    def test_stock_service_validates_sufficient_stock(self) -> None:
        """Arrange: Criar item com quantidade menor que disponível."""
        warehouse = MockWarehouse(stock_available=10)
        service = StockService(warehouse_api=warehouse)

        product = Product(id=1, name="Laptop", price=Decimal("2000.00"))
        item = CartItem(product=product, quantity=5)

        # Act
        has_stock, error = service.validate_stock([item])

        # Assert
        assert has_stock
        assert error == ""


class TestPricingServiceResponsibility:
    """Valida que PricingService tem apenas responsabilidade de preço."""

    def test_pricing_service_has_single_responsibility(self) -> None:
        """Arrange: Criar serviço de preço."""
        service = PricingService()

        # Act & Assert: Verificar que tem métodos de preço
        assert hasattr(service, 'calculate_subtotal')
        assert hasattr(service, 'apply_discount')
        assert hasattr(service, 'calculate_final_total')

        # Assert: Verificar que NÃO tem métodos de outras responsabilidades
        assert not hasattr(service, 'validate_stock')
        assert not hasattr(service, 'process_payment')

    def test_pricing_service_calculates_subtotal(self) -> None:
        """Arrange: Criar itens e serviço de preço."""
        service = PricingService()
        product = Product(id=1, name="Laptop", price=Decimal("2000.00"))
        item = CartItem(product=product, quantity=2)

        # Act
        subtotal = service.calculate_subtotal([item])

        # Assert
        assert subtotal == Decimal("4000.00")

    def test_pricing_service_applies_vip_discount(self) -> None:
        """Arrange: Criar serviço e valor para desconto VIP."""
        service = PricingService()
        subtotal = Decimal("1000.00")

        # Act
        discount = service.apply_discount(subtotal, is_vip=True)

        # Assert: VIP deve ter 15% de desconto
        expected = Decimal("1000.00") * Decimal("0.15")
        assert discount == expected


class TestPaymentServiceResponsibility:
    """Valida que PaymentService tem apenas responsabilidade de pagamento."""

    def test_payment_service_has_single_responsibility(self) -> None:
        """Arrange: Criar serviço de pagamento."""
        gateway = MockPaymentGateway()
        service = PaymentService(payment_gateway=gateway)

        # Act & Assert: Verificar que tem método de pagamento
        assert hasattr(service, 'process_payment')

        # Assert: Verificar que NÃO tem métodos de outras responsabilidades
        assert not hasattr(service, 'calculate_total')
        assert not hasattr(service, 'validate_stock')

    def test_payment_service_processes_successful_payment(self) -> None:
        """Arrange: Criar gateway aprovador e serviço."""
        gateway = MockPaymentGateway(approve=True, transaction_id="txn_456")
        service = PaymentService(payment_gateway=gateway)

        # Act
        success, result = service.process_payment(user_id=123, amount=150.00)

        # Assert
        assert success
        assert result == "txn_456"

    def test_payment_service_processes_declined_payment(self) -> None:
        """Arrange: Criar gateway que recusa e serviço."""
        gateway = MockPaymentGateway(approve=False)
        service = PaymentService(payment_gateway=gateway)

        # Act
        success, result = service.process_payment(user_id=123, amount=150.00)

        # Assert
        assert not success
        assert "recusado" in result.lower()


# ============================================================================
# Testes de Orquestração
# ============================================================================

class TestCheckoutServiceOrchestration:
    """Valida que CheckoutService orquestra os serviços corretamente."""

    def test_checkout_service_is_orchestrator(self) -> None:
        """Arrange: Criar orquestrador com serviços injetados."""
        stock = StockService(warehouse_api=MockWarehouse())
        pricing = PricingService()
        payment = PaymentService(payment_gateway=MockPaymentGateway())

        checkout = CheckoutService(
            stock_service=stock,
            pricing_service=pricing,
            payment_service=payment
        )

        # Act & Assert: Verificar que tem referências aos serviços
        assert checkout.stock is not None
        assert checkout.pricing is not None
        assert checkout.payment is not None

    def test_checkout_processes_complete_flow_success(self) -> None:
        """Arrange: Criar checkout com mocks que aprovam tudo."""
        stock = StockService(warehouse_api=MockWarehouse(stock_available=10))
        pricing = PricingService()
        payment = PaymentService(
            payment_gateway=MockPaymentGateway(approve=True, transaction_id="txn_789")
        )
        checkout = CheckoutService(
            stock_service=stock,
            pricing_service=pricing,
            payment_service=payment
        )

        product = Product(id=1, name="Laptop", price=Decimal("500.00"))
        item = CartItem(product=product, quantity=2)
        request = CheckoutRequest(user_id=123, is_vip=False, cart_items=[item])

        # Act
        result = checkout.process(request)

        # Assert
        assert isinstance(result, CheckoutResult)
        assert result.success
        assert result.transaction_id == "txn_789"
        assert result.error is None

    def test_checkout_fails_on_insufficient_stock(self) -> None:
        """Arrange: Criar checkout com estoque insuficiente."""
        stock = StockService(warehouse_api=MockWarehouse(stock_available=1))
        pricing = PricingService()
        payment = PaymentService(payment_gateway=MockPaymentGateway())

        checkout = CheckoutService(
            stock_service=stock,
            pricing_service=pricing,
            payment_service=payment
        )

        product = Product(id=1, name="Laptop", price=Decimal("500.00"))
        item = CartItem(product=product, quantity=10)
        request = CheckoutRequest(user_id=123, is_vip=False, cart_items=[item])

        # Act
        result = checkout.process(request)

        # Assert
        assert not result.success
        assert result.error is not None
        assert "insuficiente" in result.error.lower()
        assert result.transaction_id is None

    def test_checkout_fails_on_payment_declined(self) -> None:
        """Arrange: Criar checkout com pagamento recusado."""
        stock = StockService(warehouse_api=MockWarehouse(stock_available=10))
        pricing = PricingService()
        payment = PaymentService(payment_gateway=MockPaymentGateway(approve=False))

        checkout = CheckoutService(
            stock_service=stock,
            pricing_service=pricing,
            payment_service=payment
        )

        product = Product(id=1, name="Laptop", price=Decimal("500.00"))
        item = CartItem(product=product, quantity=1)
        request = CheckoutRequest(user_id=123, is_vip=False, cart_items=[item])

        # Act
        result = checkout.process(request)

        # Assert
        assert not result.success
        assert result.error is not None
        assert result.transaction_id is None


# ============================================================================
# Testes de Injeção de Dependência
# ============================================================================

class TestDependencyInjection:
    """Valida que os serviços usam injeção de dependência corretamente."""

    def test_services_accept_injected_dependencies(self) -> None:
        """Arrange & Act: Criar serviços com deps customizadas."""
        custom_warehouse = MockWarehouse(stock_available=999)
        custom_gateway = MockPaymentGateway(approve=True)

        stock = StockService(warehouse_api=custom_warehouse)
        payment = PaymentService(payment_gateway=custom_gateway)

        # Assert: Verificar que aceitam injeção
        assert stock.warehouse_api is custom_warehouse
        assert payment.payment_gateway is custom_gateway

    def test_services_use_injected_configs(self) -> None:
        """Arrange: Criar config customizada."""
        custom_config = DiscountConfig(
            DISCOUNT_TIER_1000=0.25,
            DISCOUNT_TIER_500=0.15,
            VIP_DISCOUNT=0.20
        )

        pricing = PricingService(discount_config=custom_config)

        # Act & Assert
        assert pricing.discount_config.DISCOUNT_TIER_1000 == 0.25
        assert pricing.discount_config.VIP_DISCOUNT == 0.20
