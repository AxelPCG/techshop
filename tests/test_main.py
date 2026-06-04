import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app, get_cart
from src.models import Product, CartItem, UserData
from src.cart import ShoppingCart

client = TestClient(app)

# Fixtures
@pytest.fixture
def sample_product():
    return Product(id=1, name="Sample Product", price=100.0, category="Electronics")

@pytest.fixture
def sample_cart_item(sample_product):
    return CartItem(product=sample_product, quantity=1)

@pytest.fixture
def mock_cart():
    cart = ShoppingCart()
    # Sobrescreve a dependência do carrinho para usar nosso mock
    app.dependency_overrides[get_cart] = lambda: cart
    return cart

# Testes para a rota /cart/add
def test_add_to_cart_success(mock_cart, sample_cart_item):
    response = client.post("/cart/add", json=sample_cart_item.model_dump())
    assert response.status_code == 200
    assert len(mock_cart.items) == 1
    assert mock_cart.items[0].quantity == 1

# Testes para a rota /cart
def test_get_cart_details_success(mock_cart, sample_cart_item):
    mock_cart.add_item(sample_cart_item.product, sample_cart_item.quantity)
    response = client.get("/cart")
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 100.0
    assert len(data["items"]) == 1

# Testes para a rota /checkout
def test_checkout_empty_cart(mock_cart):
    response = client.post("/checkout", json=UserData(id=1, name="Test", email="a@a.com", is_vip=False).model_dump())
    assert response.status_code == 400
    assert "Carrinho está vazio" in response.json()["detail"]

@patch('src.main.process_checkout')
def test_checkout_success(mock_process_checkout, mock_cart, sample_cart_item):
    # Arrange
    mock_cart.add_item(sample_cart_item.product, 1)
    user_data = UserData(id=1, name="Test User", email="test@user.com", is_vip=False)
    
    # Configura o mock para retornar um resultado de sucesso
    mock_process_checkout.return_value = {"success": True, "payment_details": {"status": "pagamento_aprovado"}}

    # Act
    response = client.post("/checkout", json=user_data.model_dump())

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "Sucesso"
    mock_process_checkout.assert_called_once()
    # Verifica se o carrinho foi limpo
    assert len(mock_cart.items) == 0

@patch('src.main.process_checkout')
def test_checkout_stock_failure(mock_process_checkout, mock_cart, sample_cart_item):
    mock_cart.add_item(sample_cart_item.product, 1)
    user_data = UserData(id=1, name="Test User", email="test@user.com", is_vip=False)
    
    mock_process_checkout.side_effect = ValueError("Estoque insuficiente")

    response = client.post("/checkout", json=user_data.model_dump())

    assert response.status_code == 400
    assert "Estoque insuficiente" in response.json()["detail"]

@patch('src.main.process_checkout')
def test_checkout_payment_failure(mock_process_checkout, mock_cart, sample_cart_item):
    mock_cart.add_item(sample_cart_item.product, 1)
    user_data = UserData(id=1, name="Test User", email="test@user.com", is_vip=False)
    
    mock_process_checkout.side_effect = ConnectionError("Falha no pagamento")

    response = client.post("/checkout", json=user_data.model_dump())

    assert response.status_code == 503
    assert "Falha no pagamento" in response.json()["detail"]

@patch('src.main.process_checkout')
def test_checkout_unexpected_error(mock_process_checkout, mock_cart, sample_cart_item):
    mock_cart.add_item(sample_cart_item.product, 1)
    user_data = UserData(id=1, name="Test User", email="test@user.com", is_vip=False)
    
    mock_process_checkout.side_effect = Exception("Erro inesperado")

    response = client.post("/checkout", json=user_data.model_dump())

    assert response.status_code == 500
    assert "Ocorreu um erro inesperado" in response.json()["detail"]

# Limpa as substituições de dependência após os testes
@pytest.fixture(autouse=True, scope="module")
def cleanup():
    yield
    app.dependency_overrides.clear()
