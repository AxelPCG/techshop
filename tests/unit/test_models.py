from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models import CartItem, Product


def make_product(**kwargs) -> Product:
    defaults = {"id": 1, "name": "Teclado", "price": Decimal("100.00")}
    return Product(**{**defaults, **kwargs})


class TestProduct:
    def test_valid_product(self):
        # Arrange / Act
        product = make_product()

        # Assert
        assert product.id == 1
        assert product.name == "Teclado"
        assert product.price == Decimal("100.00")

    def test_price_zero_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError, match="price must be greater than zero"):
            make_product(price=Decimal("0"))

    def test_price_negative_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError, match="price must be greater than zero"):
            make_product(price=Decimal("-10.00"))

    def test_product_is_immutable(self):
        # Arrange
        product = make_product()

        # Act / Assert
        with pytest.raises(ValidationError):
            product.price = Decimal("200.00")


class TestCartItem:
    def test_valid_cart_item(self):
        # Arrange
        product = make_product()

        # Act
        item = CartItem(product=product, quantity=3)

        # Assert
        assert item.quantity == 3

    def test_quantity_zero_raises(self):
        # Arrange
        product = make_product()

        # Act / Assert
        with pytest.raises(ValidationError, match="quantity must be greater than zero"):
            CartItem(product=product, quantity=0)

    def test_quantity_negative_raises(self):
        # Arrange
        product = make_product()

        # Act / Assert
        with pytest.raises(ValidationError, match="quantity must be greater than zero"):
            CartItem(product=product, quantity=-1)
