"""Configurações de aplicação com variáveis de ambiente.

Este módulo gerencia todas as configurações da aplicação usando Pydantic BaseSettings,
garantindo que dados sensíveis nunca estejam hardcoded no código.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class PaymentConfig(BaseSettings):
    """Configuração de pagamento via variáveis de ambiente.

    Nunca adicionar dados sensíveis diretamente nesta classe.
    Usar variáveis de ambiente ou arquivo .env.local (Git-ignored).

    Attributes:
        PAYMENT_API_URL: URL da API de pagamento.
        PAYMENT_API_KEY: Chave de autenticação da API.
        ENCRYPTION_KEY: Chave para criptografia de dados.
        MAX_TRANSACTION_AMOUNT: Valor máximo de transação permitido.
    """
    model_config = ConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    PAYMENT_API_URL: str = "https://api.pagamento.exemplo.local"
    PAYMENT_API_KEY: str = "default_test_key"
    ENCRYPTION_KEY: Optional[str] = None
    MAX_TRANSACTION_AMOUNT: float = 99999.99


class ShippingConfig(BaseSettings):
    """Configuração de frete.

    Attributes:
        SHIPPING_COST: Custo padrão de frete em reais.
        SHIPPING_COST_INTERNATIONAL: Custo de frete internacional.
    """
    model_config = ConfigDict(
        env_file=".env.local",
        case_sensitive=True
    )

    SHIPPING_COST: float = 15.50
    SHIPPING_COST_INTERNATIONAL: float = 50.00


class DiscountConfig(BaseSettings):
    """Configuração de descontos.

    Attributes:
        DISCOUNT_TIER_1000: Percentual de desconto acima de R$ 1000.
        DISCOUNT_TIER_500: Percentual de desconto acima de R$ 500.
        VIP_DISCOUNT: Desconto para usuários VIP.
    """
    model_config = ConfigDict(
        env_file=".env.local",
        case_sensitive=True
    )

    DISCOUNT_TIER_1000: float = 0.20  # 20%
    DISCOUNT_TIER_500: float = 0.10   # 10%
    VIP_DISCOUNT: float = 0.15         # 15%


class AppConfig(BaseSettings):
    """Configuração geral da aplicação.

    Attributes:
        DEBUG: Modo debug ativado.
        LOG_LEVEL: Nível de logging.
        STOCK_VALIDATION_ENABLED: Se validação de estoque está ativa.
    """
    model_config = ConfigDict(
        env_file=".env.local",
        case_sensitive=True
    )

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    STOCK_VALIDATION_ENABLED: bool = True
