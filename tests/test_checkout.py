import pytest
from unittest.mock import MagicMock, patch
from src.checkout import (
    StockValidator,
    ShippingService,
    DiscountService,
    FakePaymentAPI,
    PaymentService,
    process_checkout,
)
from src.models import Product, CartItem, UserData

# Fixtures
@pytest.fixture
def sample_product():
    return Product(id=1, name="Sample Product", price=100.0, category="Electronics")

@pytest.fixture
def sample_cart_item(sample_product):
    return CartItem(product=sample_product, quantity=2)

@pytest.fixture
def vip_user():
    return UserData(id=1, name="VIP User", email="vip@test.com", is_vip=True)

@pytest.fixture
def regular_user():
    return UserData(id=2, name="Regular User", email="regular@test.com", is_vip=False)

# Testes para StockValidator
def test_stock_validator_success(sample_cart_item):
    validator = StockValidator()
    assert validator.validate([sample_cart_item]) is True

def test_stock_validator_insufficient_stock(sample_cart_item):
    validator = StockValidator()
    sample_cart_item.quantity = 11 # mock_stock is 10
    with pytest.raises(ValueError, match="Estoque insuficiente para Sample Product"):
        validator.validate([sample_cart_item])

# Testes para ShippingService
def test_shipping_service_calculate():
    service = ShippingService()
    assert service.calculate([]) == 15.50

# Testes para DiscountService
def test_discount_service_over_1000(regular_user):
    service = DiscountService()
    assert service.calculate(1200.0, regular_user) == 1200.0 * 0.80

def test_discount_service_over_500(regular_user):
    service = DiscountService()
    assert service.calculate(600.0, regular_user) == 600.0 * 0.90

def test_discount_service_vip_user(vip_user):
    service = DiscountService()
    assert service.calculate(400.0, vip_user) == 400.0 * 0.85

def test_discount_service_no_discount(regular_user):
    service = DiscountService()
    assert service.calculate(400.0, regular_user) == 400.0

# Testes para FakePaymentAPI e PaymentService
def test_fake_payment_api_charge_success():
    api = FakePaymentAPI()
    result = api.charge(100.0, 1)
    assert result["status"] == "pagamento_aprovado"

def test_fake_payment_api_charge_failure():
    api = FakePaymentAPI()
    with pytest.raises(ConnectionError):
        api.charge(10000.0, 1)

def test_payment_service_process():
    mock_api = MagicMock()
    mock_api.charge.return_value = {"status": "success"}
    service = PaymentService(payment_api=mock_api)
    user = UserData(id=1, name="Test", email="test@test.com", is_vip=False)
    result = service.process(user, 150.0)
    mock_api.charge.assert_called_once_with(amount=150.0, user_id=1)
    assert result == {"status": "success"}

# Testes para o orquestrador process_checkout
def test_process_checkout_success(sample_cart_item, regular_user):
    # Mocks para os serviços
    stock_validator = MagicMock()
    shipping_service = MagicMock()
    discount_service = MagicMock()
    payment_service = MagicMock()

    # Configuração dos retornos dos mocks
    stock_validator.validate.return_value = True
    shipping_service.calculate.return_value = 15.50
    # subtotal (200) + shipping (15.50) = 215.50
    discount_service.calculate.return_value = 215.50 # Sem desconto
    payment_service.process.return_value = {"status": "pagamento_aprovado"}

    result = process_checkout(
        cart_items=[sample_cart_item],
        user_data=regular_user,
        stock_validator=stock_validator,
        shipping_service=shipping_service,
        discount_service=discount_service,
        payment_service=payment_service,
    )

    # Asserts
    stock_validator.validate.assert_called_once()
    shipping_service.calculate.assert_called_once()
    discount_service.calculate.assert_called_once()
    payment_service.process.assert_called_once()
    assert result["success"] is True
    assert result["payment_details"]["status"] == "pagamento_aprovado"

def test_process_checkout_stock_failure(sample_cart_item, regular_user):
    stock_validator = MagicMock()
    stock_validator.validate.side_effect = ValueError("Estoque insuficiente")
    
    shipping_service = MagicMock()
    discount_service = MagicMock()
    payment_service = MagicMock()

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        process_checkout(
            cart_items=[sample_cart_item],
            user_data=regular_user,
            stock_validator=stock_validator,
            shipping_service=shipping_service,
            discount_service=discount_service,
            payment_service=payment_service,
        )

def test_process_checkout_payment_failure(sample_cart_item, regular_user):
    stock_validator = MagicMock()
    shipping_service = MagicMock()
    discount_service = MagicMock()
    payment_service = MagicMock()

    stock_validator.validate.return_value = True
    shipping_service.calculate.return_value = 15.50
    discount_service.calculate.return_value = 215.50
    payment_service.process.side_effect = ConnectionError("Falha no pagamento")

    with pytest.raises(ConnectionError, match="Falha no pagamento"):
        process_checkout(
            cart_items=[sample_cart_item],
            user_data=regular_user,
            stock_validator=stock_validator,
            shipping_service=shipping_service,
            discount_service=discount_service,
            payment_service=payment_service,
        )
