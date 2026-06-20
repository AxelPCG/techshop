from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class Product(BaseModel):
    """Representa um produto disponível na loja.

    Attributes:
        id: Identificador único do produto.
        name: Nome do produto.
        price: Preço unitário em reais. Deve ser maior que zero.
    """

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    price: Decimal

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, value: Decimal) -> Decimal:
        """Garante que o preço seja estritamente positivo.

        Args:
            value: Valor do preço a ser validado.

        Returns:
            O valor validado.

        Raises:
            ValueError: Se o preço for zero ou negativo.
        """
        if value <= Decimal("0"):
            raise ValueError("price must be greater than zero")
        return value


class CartItem(BaseModel):
    """Representa um item dentro do carrinho de compras.

    Attributes:
        product: Produto associado ao item.
        quantity: Quantidade do produto. Deve ser maior que zero.
    """

    product: Product
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, value: int) -> int:
        """Garante que a quantidade seja estritamente positiva.

        Args:
            value: Valor da quantidade a ser validado.

        Returns:
            O valor validado.

        Raises:
            ValueError: Se a quantidade for zero ou negativa.
        """
        if value <= 0:
            raise ValueError("quantity must be greater than zero")
        return value
