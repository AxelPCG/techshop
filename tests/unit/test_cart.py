from decimal import Decimal

import pytest

from src.cart import DiscountCalculator, ShoppingCart
from src.models import Product


def make_product(id: int = 1, price: str = "100.00", name: str = "Produto") -> Product:
    return Product(id=id, name=name, price=Decimal(price))


class TestShoppingCartAddItem:
    def test_add_new_item(self):
        # Arrange
        cart = ShoppingCart()
        product = make_product()

        # Act
        cart.add_item(product, quantity=2)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 2

    def test_add_existing_item_increments_quantity(self):
        # Arrange
        cart = ShoppingCart()
        product = make_product()
        cart.add_item(product, quantity=1)

        # Act
        cart.add_item(product, quantity=3)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 4

    def test_add_different_products(self):
        # Arrange
        cart = ShoppingCart()
        product_a = make_product(id=1)
        product_b = make_product(id=2)

        # Act
        cart.add_item(product_a, quantity=1)
        cart.add_item(product_b, quantity=1)

        # Assert
        assert len(cart.items) == 2

    def test_add_item_zero_quantity_raises(self):
        # Arrange
        cart = ShoppingCart()
        product = make_product()

        # Act / Assert
        with pytest.raises(ValueError, match="quantity must be greater than zero"):
            cart.add_item(product, quantity=0)

    def test_add_item_negative_quantity_raises(self):
        # Arrange
        cart = ShoppingCart()
        product = make_product()

        # Act / Assert
        with pytest.raises(ValueError, match="quantity must be greater than zero"):
            cart.add_item(product, quantity=-1)


class TestShoppingCartRemoveItem:
    def test_remove_existing_item(self):
        # Arrange
        cart = ShoppingCart()
        product = make_product(id=1)
        cart.add_item(product, quantity=1)

        # Act
        cart.remove_item(product_id=1)

        # Assert
        assert len(cart.items) == 0

    def test_remove_nonexistent_item_does_not_raise(self):
        # Arrange
        cart = ShoppingCart()

        # Act / Assert
        cart.remove_item(product_id=999)
        assert len(cart.items) == 0

    def test_remove_only_target_item(self):
        # Arrange
        cart = ShoppingCart()
        cart.add_item(make_product(id=1), quantity=1)
        cart.add_item(make_product(id=2), quantity=1)

        # Act
        cart.remove_item(product_id=1)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].product.id == 2


class TestShoppingCartCalculateTotal:
    def test_total_empty_cart(self):
        # Arrange
        cart = ShoppingCart()

        # Act
        total = cart.calculate_total()

        # Assert
        assert total == Decimal("0")

    def test_total_single_item(self):
        # Arrange
        cart = ShoppingCart()
        cart.add_item(make_product(price="50.00"), quantity=3)

        # Act
        total = cart.calculate_total()

        # Assert
        assert total == Decimal("150.00")

    def test_total_multiple_items(self):
        # Arrange
        cart = ShoppingCart()
        cart.add_item(make_product(id=1, price="100.00"), quantity=2)
        cart.add_item(make_product(id=2, price="50.00"), quantity=4)

        # Act
        total = cart.calculate_total()

        # Assert
        assert total == Decimal("400.00")


class TestDiscountCalculator:
    def test_no_discount_below_500(self):
        # Arrange
        calc = DiscountCalculator()

        # Act
        result = calc.apply(Decimal("499.99"))

        # Assert
        assert result == Decimal("499.99")

    def test_10_percent_discount_above_500(self):
        # Arrange
        calc = DiscountCalculator()

        # Act
        result = calc.apply(Decimal("600.00"))

        # Assert
        assert result == Decimal("540.00")

    def test_20_percent_discount_above_1000(self):
        # Arrange
        calc = DiscountCalculator()

        # Act
        result = calc.apply(Decimal("1200.00"))

        # Assert
        assert result == Decimal("960.00")

    def test_boundary_exactly_500_no_discount(self):
        # Arrange
        calc = DiscountCalculator()

        # Act
        result = calc.apply(Decimal("500.00"))

        # Assert
        assert result == Decimal("500.00")

    def test_boundary_exactly_1000_mid_discount(self):
        # Arrange
        calc = DiscountCalculator()

        # Act
        result = calc.apply(Decimal("1000.00"))

        # Assert
        assert result == Decimal("900.00")
