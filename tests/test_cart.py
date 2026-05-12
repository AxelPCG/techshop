from __future__ import annotations

import pytest

from src.cart import ShoppingCart
from src.models import Product


@pytest.fixture()
def cart() -> ShoppingCart:
    """Create a fresh shopping cart for each test."""
    return ShoppingCart()


def test_add_item_appends_new_item(cart: ShoppingCart) -> None:
    """Add a new product to an empty cart creates a new line item."""
    # Arrange
    product = Product(id=1, name="Mouse", price=100.0)

    # Act
    cart.add_item(product=product, quantity=2)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].product.id == 1
    assert cart.items[0].quantity == 2


def test_add_item_sums_quantity_when_same_product_id(cart: ShoppingCart) -> None:
    """Adding the same product twice sums quantities instead of duplicating items."""
    # Arrange
    product = Product(id=1, name="Mouse", price=100.0)
    cart.add_item(product=product, quantity=2)

    # Act
    cart.add_item(product=product, quantity=3)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].product.id == 1
    assert cart.items[0].quantity == 5


def test_remove_item_removes_matching_product(cart: ShoppingCart) -> None:
    """Removing an existing product id drops it from the cart."""
    # Arrange
    product_1 = Product(id=1, name="Mouse", price=100.0)
    product_2 = Product(id=2, name="Keyboard", price=200.0)
    cart.add_item(product=product_1, quantity=1)
    cart.add_item(product=product_2, quantity=1)

    # Act
    cart.remove_item(product_id=1)

    # Assert
    assert [item.product.id for item in cart.items] == [2]


def test_remove_item_nonexistent_product_keeps_cart_unchanged(cart: ShoppingCart) -> None:
    """Removing a product id that is not in the cart keeps current items intact."""
    # Arrange
    product = Product(id=1, name="Mouse", price=100.0)
    cart.add_item(product=product, quantity=1)

    # Act
    cart.remove_item(product_id=999)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].product.id == 1
    assert cart.items[0].quantity == 1


def test_calculate_total_returns_sum_of_price_times_quantity(cart: ShoppingCart) -> None:
    """Total equals the sum of each item price multiplied by its quantity."""
    # Arrange
    product_1 = Product(id=1, name="Mouse", price=100.0)
    product_2 = Product(id=2, name="Keyboard", price=200.0)
    cart.add_item(product=product_1, quantity=2)
    cart.add_item(product=product_2, quantity=1)

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == pytest.approx(400.0)


def test_calculate_total_empty_cart_is_zero(cart: ShoppingCart) -> None:
    """An empty cart total is zero."""
    # Arrange
    # (cart fixture provides an empty cart)

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 0.0


def test_calculate_total_with_discount_above_500_applies_10_percent(cart: ShoppingCart) -> None:
    """Totals above 500 receive a 10% discount."""
    # Arrange
    product = Product(id=1, name="Monitor", price=600.0)
    cart.add_item(product=product, quantity=1)

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == pytest.approx(540.0)


def test_calculate_total_with_discount_above_1000_applies_20_percent(cart: ShoppingCart) -> None:
    """Totals above 1000 receive a 20% discount."""
    # Arrange
    product = Product(id=1, name="Laptop", price=1200.0)
    cart.add_item(product=product, quantity=1)

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == pytest.approx(960.0)


def test_calculate_total_with_discount_exactly_500_has_no_discount(cart: ShoppingCart) -> None:
    """A total exactly at 500 does not receive a discount (threshold is strictly greater)."""
    # Arrange
    product = Product(id=1, name="Headphones", price=250.0)
    cart.add_item(product=product, quantity=2)

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == pytest.approx(500.0)


def test_calculate_total_with_discount_exactly_1000_applies_10_percent(cart: ShoppingCart) -> None:
    """A total exactly at 1000 receives 10% (20% requires strictly greater than 1000)."""
    # Arrange
    product = Product(id=1, name="Gaming Chair", price=500.0)
    cart.add_item(product=product, quantity=2)

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == pytest.approx(900.0)
