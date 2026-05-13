"""Serviço de cálculo de preços e descontos.

Responsabilidade única: calcular preços totais com descontos e frete.
Centraliza toda a lógica de precificação em um único lugar.
"""

from typing import List
from decimal import Decimal
from src.models import CartItem
from src.config import DiscountConfig, ShippingConfig


class PricingService:
    """Serviço de precificação com responsabilidade única.

    Calcula totais, aplica descontos e adiciona frete.
    Todas as regras de negócio de preço estão centralizadas aqui.

    Attributes:
        discount_config: Configuração de descontos.
        shipping_config: Configuração de frete.
    """

    def __init__(
        self,
        discount_config: DiscountConfig = None,
        shipping_config: ShippingConfig = None
    ) -> None:
        """Inicializa o serviço com configurações injetadas.

        Args:
            discount_config: Configuração de descontos (usar padrão se None).
            shipping_config: Configuração de frete (usar padrão se None).
        """
        self.discount_config = discount_config or DiscountConfig()
        self.shipping_config = shipping_config or ShippingConfig()

    def calculate_subtotal(self, items: List[CartItem]) -> Decimal:
        """Calcula o subtotal sem frete nem desconto.

        Args:
            items: Lista de itens do carrinho.

        Returns:
            Decimal: Subtotal em reais.

        Example:
            >>> subtotal = service.calculate_subtotal([item1, item2])
            >>> print(f"Subtotal: R$ {subtotal}")
        """
        return sum(
            Decimal(str(item.product.price)) * item.quantity
            for item in items
        )

    def apply_discount(self, subtotal: Decimal, is_vip: bool) -> Decimal:
        """Aplica desconto com base em regras de negócio.

        Regras:
        - Se VIP: aplica desconto VIP (15%)
        - Se subtotal > R$ 1000: aplica 20% de desconto
        - Se subtotal > R$ 500: aplica 10% de desconto
        - Caso contrário: sem desconto

        Args:
            subtotal: Valor antes do desconto.
            is_vip: Se o usuário possui status VIP.

        Returns:
            Decimal: Desconto aplicado (valor a subtrair do subtotal).

        Example:
            >>> discount = service.apply_discount(Decimal("1500"), is_vip=True)
            >>> print(f"Desconto: R$ {discount}")
        """
        if is_vip:
            return subtotal * Decimal(str(self.discount_config.VIP_DISCOUNT))

        if subtotal > 1000:
            return subtotal * Decimal(str(self.discount_config.DISCOUNT_TIER_1000))

        if subtotal > 500:
            return subtotal * Decimal(str(self.discount_config.DISCOUNT_TIER_500))

        return Decimal("0")

    def calculate_final_total(
        self,
        items: List[CartItem],
        is_vip: bool
    ) -> Decimal:
        """Calcula o valor total com frete e desconto.

        Fluxo:
        1. Calcula subtotal (produtos)
        2. Aplica desconto
        3. Adiciona frete

        Args:
            items: Lista de itens do carrinho.
            is_vip: Se o usuário possui status VIP.

        Returns:
            Decimal: Valor total a pagar em reais.

        Example:
            >>> total = service.calculate_final_total([item1, item2], is_vip=True)
            >>> print(f"Total: R$ {total}")
        """
        subtotal = self.calculate_subtotal(items)
        discount = self.apply_discount(subtotal, is_vip)
        after_discount = subtotal - discount

        shipping = Decimal(str(self.shipping_config.SHIPPING_COST))
        final_total = after_discount + shipping

        return final_total
