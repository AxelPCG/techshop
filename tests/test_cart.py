import pytest
from src.models import Product
from src.cart import ShoppingCart

# Arrange: Fixtures para produtos
@pytest.fixture
def product_1():
    """Retorna um produto de exemplo com preço 10.00."""
    return Product(id=1, name="Test Product 1", price=10.00, category="Test")

@pytest.fixture
def product_2():
    """Retorna um produto de exemplo com preço 50.00."""
    return Product(id=2, name="Test Product 2", price=50.00, category="Test")

@pytest.fixture
def product_expensive():
    """Retorna um produto caro para testar descontos."""
    return Product(id=3, name="Expensive Product", price=600.00, category="Test")

@pytest.fixture
def product_very_expensive():
    """Retorna um produto muito caro para testar descontos."""
    return Product(id=4, name="Very Expensive Product", price=1100.00, category="Test")


# --- Testes para a classe ShoppingCart ---

def test_add_new_item_to_cart():
    """
    Testa se um novo item é adicionado corretamente ao carrinho.
    """
    # Arrange
    cart = ShoppingCart()
    product = Product(id=1, name="Test", price=10.0, category="Test")
    quantity = 2

    # Act
    cart.add_item(product, quantity)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].product == product
    assert cart.items[0].quantity == quantity

def test_add_existing_item_to_cart():
    """
    Testa se a quantidade de um item existente é atualizada corretamente.
    """
    # Arrange
    cart = ShoppingCart()
    product = Product(id=1, name="Test", price=10.0, category="Test")
    cart.add_item(product, 2)

    # Act
    cart.add_item(product, 3)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5

def test_remove_item_from_cart(product_1):
    """
    Testa se um item é removido corretamente do carrinho.
    """
    # Arrange
    cart = ShoppingCart()
    cart.add_item(product_1, 1)

    # Act
    cart.remove_item(product_1.id)

    # Assert
    assert len(cart.items) == 0

def test_calculate_total_empty_cart():
    """
    Testa o cálculo do total para um carrinho vazio (caso de borda).
    """
    # Arrange
    cart = ShoppingCart()

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 0

def test_calculate_total_with_items(product_1, product_2):
    """
    Testa o cálculo do total para um carrinho com múltiplos itens.
    """
    # Arrange
    cart = ShoppingCart()
    cart.add_item(product_1, 5)  # 5 * 10.00 = 50.00
    cart.add_item(product_2, 2)  # 2 * 50.00 = 100.00

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 150.00

def test_discount_no_discount_below_threshold(product_1):
    """
    Testa se nenhum desconto é aplicado para totais abaixo de 500.
    """
    # Arrange
    cart = ShoppingCart()
    cart.add_item(product_1, 49) # Total = 490.00

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == 490.00

def test_discount_exact_threshold_500(product_1):
    """
    Testa o cálculo do desconto no limiar exato de 500 (caso de borda).
    """
    # Arrange
    cart = ShoppingCart()
    cart.add_item(product_1, 50) # Total = 500.00

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == 500.00 # Sem desconto

def test_discount_10_percent_just_above_500(product_expensive):
    """
    Testa o desconto de 10% para um total ligeiramente acima de 500.
    """
    # Arrange
    cart = ShoppingCart()
    cart.add_item(product_expensive, 1) # Total = 600.00

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == 600.00 * 0.90

def test_discount_20_percent_just_above_1000(product_very_expensive):
    """
    Testa o desconto de 20% para um total ligeiramente acima de 1000.
    """
    # Arrange
    cart = ShoppingCart()
    cart.add_item(product_very_expensive, 1) # Total = 1100.00

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == 1100.00 * 0.80

def test_discount_empty_cart(product_1):
    """
    Testa o cálculo de desconto para um carrinho vazio (caso de borda).
    """
    # Arrange
    cart = ShoppingCart()

    # Act
    total_with_discount = cart.calculate_total_with_discount()

    # Assert
    assert total_with_discount == 0
