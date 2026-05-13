"""Serviço de checkout - orquestrador principal.

Coordena os demais serviços (stock, pricing, payment) sem implementar lógica.
Segue o padrão de Orquestração em Camadas.
"""

import logging
from src.models import CheckoutRequest, CheckoutResult
from src.services.stock_service import StockService
from src.services.pricing_service import PricingService
from src.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class CheckoutService:
    """Orquestrador de checkout - coordena serviços especializados.

    Não implementa lógica de negócio diretamente.
    Apenas coordena as chamadas aos serviços injetados.

    Attributes:
        stock_service: Serviço de validação de estoque.
        pricing_service: Serviço de cálculo de preços.
        payment_service: Serviço de processamento de pagamento.
    """

    def __init__(
        self,
        stock_service: StockService,
        pricing_service: PricingService,
        payment_service: PaymentService
    ) -> None:
        """Inicializa o checkout com serviços injetados.

        Args:
            stock_service: Serviço de validação de estoque.
            pricing_service: Serviço de cálculo de preços.
            payment_service: Serviço de processamento de pagamento.
        """
        self.stock = stock_service
        self.pricing = pricing_service
        self.payment = payment_service

    def process(self, request: CheckoutRequest) -> CheckoutResult:
        """Processa um checkout completo orquestrando os serviços.

        Fluxo:
        1. Validar estoque dos itens
        2. Calcular preço total
        3. Processar pagamento
        4. Retornar resultado

        Args:
            request: Requisição de checkout validada pelo Pydantic.

        Returns:
            CheckoutResult: Resultado do checkout (sucesso ou erro).

        Example:
            >>> checkout = CheckoutService(stock, pricing, payment)
            >>> result = checkout.process(request)
            >>> if result.success:
            ...     print(f"Transação: {result.transaction_id}")
            >>> else:
            ...     print(f"Erro: {result.error}")
        """
        logger.info(f"Iniciando checkout para user {request.user_id}")

        # Passo 1: Validar estoque
        logger.debug("Validando estoque...")
        has_stock, stock_error = self.stock.validate_stock(request.cart_items)

        if not has_stock:
            logger.warning(f"Falha de estoque: {stock_error}")
            return CheckoutResult(success=False, error=stock_error)

        # Passo 2: Calcular preço final
        logger.debug("Calculando preço...")
        try:
            total_amount = self.pricing.calculate_final_total(
                request.cart_items,
                request.is_vip
            )
            logger.debug(f"Preço total: R$ {total_amount}")
        except Exception as e:
            error_msg = f"Erro ao calcular preço: {str(e)}"
            logger.exception(error_msg)
            return CheckoutResult(success=False, error=error_msg)

        # Passo 3: Processar pagamento
        logger.debug("Processando pagamento...")
        success, result = self.payment.process_payment(
            user_id=request.user_id,
            amount=float(total_amount)
        )

        if success:
            logger.info(f"Checkout aprovado: {result}")
            return CheckoutResult(
                success=True,
                transaction_id=result
            )
        else:
            logger.warning(f"Pagamento falhou: {result}")
            return CheckoutResult(
                success=False,
                error=result
            )
