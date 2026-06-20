from decimal import Decimal

from src.models import CartItem, Product

DISCOUNT_THRESHOLD_HIGH = Decimal("1000")
DISCOUNT_THRESHOLD_MID = Decimal("500")
DISCOUNT_RATE_HIGH = Decimal("0.80")
DISCOUNT_RATE_MID = Decimal("0.90")


class DiscountCalculator:
    """Calcula descontos progressivos sobre um total de compra.

    Regras vigentes:
        - Acima de R$ 1000: 20% de desconto.
        - Acima de R$ 500: 10% de desconto.
        - Abaixo ou igual a R$ 500: sem desconto.
    """

    def apply(self, total: Decimal) -> Decimal:
        """Aplica o desconto cabível sobre o total informado.

        Args:
            total: Valor bruto do carrinho.

        Returns:
            Valor final após aplicação do desconto.
        """
        if total > DISCOUNT_THRESHOLD_HIGH:
            return total * DISCOUNT_RATE_HIGH
        if total > DISCOUNT_THRESHOLD_MID:
            return total * DISCOUNT_RATE_MID
        return total


class ShoppingCart:
    """Representa o carrinho de compras de um usuário.

    Attributes:
        items: Lista de itens adicionados ao carrinho.
    """

    def __init__(self, discount_calculator: DiscountCalculator | None = None) -> None:
        """Inicializa o carrinho com lista de itens vazia.

        Args:
            discount_calculator: Estratégia de desconto a ser usada.
                Se não informada, usa DiscountCalculator padrão.
        """
        self.items: list[CartItem] = []
        self._discount_calculator = discount_calculator or DiscountCalculator()

    def add_item(self, product: Product, quantity: int) -> None:
        """Adiciona um produto ao carrinho.

        Se o produto já existir, incrementa a quantidade. A quantidade
        informada deve ser maior que zero.

        Args:
            product: Produto a ser adicionado.
            quantity: Quantidade a adicionar. Deve ser > 0.

        Raises:
            ValueError: Se quantity for zero ou negativo.
        """
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return

        self.items.append(CartItem(product=product, quantity=quantity))

    def remove_item(self, product_id: int) -> None:
        """Remove o item correspondente ao product_id do carrinho.

        Não lança exceção se o produto não existir no carrinho.

        Args:
            product_id: Identificador do produto a remover.
        """
        self.items = [item for item in self.items if item.product.id != product_id]

    def calculate_total(self) -> Decimal:
        """Calcula o valor bruto total dos itens no carrinho.

        Returns:
            Soma de (preço × quantidade) de todos os itens.
        """
        return sum(
            (item.product.price * item.quantity for item in self.items),
            Decimal("0"),
        )

    def calculate_total_with_discount(self) -> Decimal:
        """Calcula o valor total após aplicação de desconto progressivo.

        Delega a lógica de desconto ao DiscountCalculator injetado.

        Returns:
            Valor final com desconto aplicado.
        """
        return self._discount_calculator.apply(self.calculate_total())
