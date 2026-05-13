"""Exemplo de uso dos serviços refatorados.

Este arquivo demonstra como usar a arquitetura corrigida
com separação de responsabilidades e type safety.

DEPRECATED: O arquivo original checkout.py foi refatorado
em serviços especializados (stock, pricing, payment, checkout).
Use este arquivo como referência de como integrar os serviços.
"""

from src.models import CheckoutRequest, CheckoutResult
from src.services.checkout_service import CheckoutService
from src.services.stock_service import StockService
from src.services.pricing_service import PricingService
from src.services.payment_service import PaymentService


def setup_checkout_service(
    warehouse_api,
    payment_gateway
) -> CheckoutService:
    """Configura e retorna o serviço de checkout com todas as dependências.

    Args:
        warehouse_api: Implementação de acesso ao warehouse.
        payment_gateway: Implementação do gateway de pagamento.

    Returns:
        CheckoutService: Serviço pronto para processar checkouts.

    Example:
        >>> warehouse = RealWarehouse()
        >>> gateway = StripeGateway()
        >>> checkout = setup_checkout_service(warehouse, gateway)
        >>> result = checkout.process(request)
    """
    stock_service = StockService(warehouse_api=warehouse_api)
    pricing_service = PricingService()
    payment_service = PaymentService(payment_gateway=payment_gateway)

    return CheckoutService(
        stock_service=stock_service,
        pricing_service=pricing_service,
        payment_service=payment_service
    )


def process_checkout(
    request: CheckoutRequest,
    checkout_service: CheckoutService
) -> CheckoutResult:
    """Processa um checkout usando o serviço refatorado.

    Args:
        request: Requisição de checkout (validada automaticamente).
        checkout_service: Serviço de checkout configurado.

    Returns:
        CheckoutResult: Resultado do checkout.

    Example:
        >>> from src.models import CheckoutRequest, CartItem, Product
        >>> product = Product(id=1, name="Laptop", price=2000.00)
        >>> item = CartItem(product=product, quantity=1)
        >>> request = CheckoutRequest(user_id=123, is_vip=True, cart_items=[item])
        >>> result = process_checkout(request, checkout_service)
        >>> print(f"Sucesso: {result.success}")
    """
    return checkout_service.process(request)
