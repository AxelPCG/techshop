"""Serviço de processamento de pagamentos.

Responsabilidade única: processar pagamentos de forma segura.
Nunca armazena dados sensíveis (cartão, CPF, etc).
"""

from typing import Tuple, Optional, Protocol
import logging
from src.models import CheckoutRequest, CheckoutResult
from src.config import PaymentConfig

logger = logging.getLogger(__name__)


class PaymentGateway(Protocol):
    """Protocol para gateway de pagamento (abstração para injeção de dependência).

    Define o contrato que qualquer implementação de payment gateway deve seguir.
    """

    def charge(self, user_id: int, amount: float) -> dict:
        """Processa cobrança no gateway de pagamento.

        Args:
            user_id: ID do usuário.
            amount: Valor a cobrar em reais.

        Returns:
            dict: Resposta com 'status' e 'transaction_id'.
        """
        ...


class PaymentService:
    """Serviço de pagamento com responsabilidade única.

    Processa pagamentos de forma segura sem armazenar dados sensíveis.
    Valida limites de transação conforme configuração.

    Attributes:
        payment_gateway: Implementação do gateway de pagamento.
        config: Configuração de pagamento.
    """

    def __init__(
        self,
        payment_gateway: PaymentGateway,
        config: PaymentConfig = None
    ) -> None:
        """Inicializa o serviço com dependências injetadas.

        Args:
            payment_gateway: Implementação do gateway de pagamento.
            config: Configuração de pagamento (usar padrão se None).
        """
        self.payment_gateway = payment_gateway
        self.config = config or PaymentConfig()

    def _validate_amount(self, amount: float) -> Tuple[bool, Optional[str]]:
        """Valida se o valor está dentro dos limites permitidos.

        Args:
            amount: Valor a validar.

        Returns:
            Tuple[bool, Optional[str]]: (válido, mensagem_erro)

        Raises:
            ValueError: Se valor for inválido (negativo ou zero).
        """
        if amount <= 0:
            return False, "Valor deve ser maior que zero"

        if amount > self.config.MAX_TRANSACTION_AMOUNT:
            return (
                False,
                f"Valor excede limite de R$ {self.config.MAX_TRANSACTION_AMOUNT}"
            )

        return True, None

    def process_payment(
        self,
        user_id: int,
        amount: float
    ) -> Tuple[bool, Optional[str]]:
        """Processa pagamento de forma segura.

        Valida valores antes de enviar para gateway.
        Nunca envia dados sensíveis (cartão, CPF) diretamente.

        Args:
            user_id: ID do usuário.
            amount: Valor a cobrar em reais.

        Returns:
            Tuple[bool, Optional[str]]: (sucesso, transaction_id_ou_erro)
                Se sucesso: (True, transaction_id)
                Se falha: (False, mensagem_erro)

        Example:
            >>> service = PaymentService(gateway=mock_gateway)
            >>> success, result = service.process_payment(user_id=123, amount=150.00)
            >>> if success:
            ...     print(f"Transação: {result}")
            >>> else:
            ...     print(f"Erro: {result}")
        """
        # Validar valor
        valid, error = self._validate_amount(amount)
        if not valid:
            logger.warning(f"Validação falhou para user {user_id}: {error}")
            return False, error

        try:
            logger.info(f"Processando pagamento: user={user_id}, amount={amount}")

            # Chamar gateway (sem dados sensíveis)
            response = self.payment_gateway.charge(
                user_id=user_id,
                amount=amount
            )

            # Validar resposta
            status = response.get("status", "").lower()
            transaction_id = response.get("transaction_id")

            if status == "approved" and transaction_id:
                logger.info(f"Pagamento aprovado: {transaction_id}")
                return True, transaction_id

            if status == "declined":
                error_msg = "Pagamento recusado pela instituição"
                logger.warning(error_msg)
                return False, error_msg

            error_msg = "Resposta inválida do gateway de pagamento"
            logger.error(f"{error_msg}: {response}")
            return False, error_msg

        except Exception as e:
            error_msg = f"Erro ao processar pagamento: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
