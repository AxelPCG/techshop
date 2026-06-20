from decimal import Decimal

from src.cart import ShoppingCart
from src.models import Product


def make_product(id: int, price: str, name: str = "Produto") -> Product:
    return Product(id=id, name=name, price=Decimal(price))


class TestCartCheckoutFlow:
    def test_full_purchase_flow_with_discount(self):
        """Fluxo completo: adiciona itens, remove um, aplica desconto."""
        # Arrange
        cart = ShoppingCart()
        notebook = make_product(id=1, price="900.00", name="Notebook")
        mouse = make_product(id=2, price="150.00", name="Mouse")
        teclado = make_product(id=3, price="200.00", name="Teclado")

        # Act
        cart.add_item(notebook, quantity=1)
        cart.add_item(mouse, quantity=2)
        cart.add_item(teclado, quantity=1)
        cart.remove_item(product_id=3)  # remove teclado

        total = cart.calculate_total()
        total_with_discount = cart.calculate_total_with_discount()

        # Assert — notebook(900) + mouse(2×150) = 1200
        assert total == Decimal("1200.00")
        assert total_with_discount == Decimal("960.00")  # 20% off

    def test_add_same_product_multiple_times_accumulates(self):
        """Adicionar o mesmo produto várias vezes acumula a quantidade."""
        # Arrange
        cart = ShoppingCart()
        produto = make_product(id=1, price="100.00")

        # Act
        cart.add_item(produto, quantity=1)
        cart.add_item(produto, quantity=1)
        cart.add_item(produto, quantity=1)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 3
        assert cart.calculate_total() == Decimal("300.00")

    def test_cart_empty_after_removing_all_items(self):
        """Carrinho fica vazio após remoção de todos os itens."""
        # Arrange
        cart = ShoppingCart()
        cart.add_item(make_product(id=1, price="50.00"), quantity=1)
        cart.add_item(make_product(id=2, price="80.00"), quantity=2)

        # Act
        cart.remove_item(product_id=1)
        cart.remove_item(product_id=2)

        # Assert
        assert len(cart.items) == 0
        assert cart.calculate_total() == Decimal("0")
        assert cart.calculate_total_with_discount() == Decimal("0")

    def test_mid_tier_discount_flow(self):
        """Compra entre R$500 e R$1000 recebe 10% de desconto."""
        # Arrange
        cart = ShoppingCart()
        produto = make_product(id=1, price="300.00")

        # Act
        cart.add_item(produto, quantity=2)  # total = 600

        # Assert
        assert cart.calculate_total() == Decimal("600.00")
        assert cart.calculate_total_with_discount() == Decimal("540.00")
