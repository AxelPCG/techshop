# checkout.py - Refatorado

from typing import List, Dict, Any
from .models import CartItem, UserData

# --- Protocolos para Injeção de Dependência ---

class StockValidatorProtocol:
    def validate(self, items: List[CartItem]) -> bool: ...

class ShippingServiceProtocol:
    def calculate(self, items: List[CartItem]) -> float: ...

class DiscountServiceProtocol:
    def calculate(self, total_value: float, user: UserData) -> float: ...

class PaymentServiceProtocol:
    def process(self, user: UserData, final_amount: float) -> Dict[str, Any]: ...

# --- Implementações Concretas dos Serviços ---

class StockValidator:
    """Valida o estoque dos itens (implementação mock)."""
    def validate(self, items: List[CartItem]) -> bool:
        print("--- Validando estoque... ---")
        for item in items:
            # Lógica de estoque mockada
            mock_stock = 10
            if item.quantity > mock_stock:
                print(f"ERRO: Estoque insuficiente para o produto {item.product.id}.")
                raise ValueError(f"Estoque insuficiente para {item.product.name}")
        print("--- Estoque OK. ---")
        return True

class ShippingService:
    """Calcula o frete (valor fixo para este exemplo)."""
    _SHIPPING_FEE = 15.50

    def calculate(self, items: List[CartItem]) -> float:
        print(f"--- Calculando frete fixo de R$ {self._SHIPPING_FEE}... ---")
        return self._SHIPPING_FEE

class DiscountService:
    """Calcula descontos com base no valor total e no tipo de usuário."""
    def calculate(self, total_value: float, user: UserData) -> float:
        print("--- Calculando descontos... ---")
        if total_value > 1000:
            print("--- Aplicando desconto de 20% (compras > R$ 1000) ---")
            return total_value * 0.80
        if total_value > 500:
            print("--- Aplicando desconto de 10% (compras > R$ 500) ---")
            return total_value * 0.90
        if user.is_vip:
            print("--- Aplicando desconto de 15% (usuário VIP) ---")
            return total_value * 0.85
        return total_value

class FakePaymentAPI:
    """Simula uma API de pagamento externa."""
    def charge(self, amount: float, user_id: int) -> Dict[str, Any]:
        print(f"--- Processando pagamento de R$ {amount:.2f} para o usuário {user_id}... ---")
        if 0 < amount < 9999:
            print("--- Pagamento APROVADO (simulado) ---")
            return {"status": "pagamento_aprovado", "transaction_id": "xyz123abc"}
        else:
            print("--- Pagamento RECUSADO (simulado) ---")
            raise ConnectionError("Falha ao processar pagamento: valor inválido.")

class PaymentService:
    """Serviço que interage com a API de pagamento."""
    def __init__(self, payment_api: FakePaymentAPI):
        self.payment_api = payment_api

    def process(self, user: UserData, final_amount: float) -> Dict[str, Any]:
        return self.payment_api.charge(amount=final_amount, user_id=user.id)

# --- Orquestrador do Checkout ---

def process_checkout(
    cart_items: List[CartItem],
    user_data: UserData,
    stock_validator: StockValidatorProtocol,
    shipping_service: ShippingServiceProtocol,
    discount_service: DiscountServiceProtocol,
    payment_service: PaymentServiceProtocol,
) -> Dict[str, Any]:
    """
    Orquestra o processo de checkout utilizando injeção de dependência.
    """
    print("--- Iniciando processo de checkout refatorado ---")
    
    # 1. Validar estoque
    stock_validator.validate(cart_items)

    # 2. Calcular total inicial
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    print(f"Subtotal: R$ {subtotal:.2f}")

    # 3. Calcular frete
    shipping_cost = shipping_service.calculate(cart_items)
    total_with_shipping = subtotal + shipping_cost
    print(f"Total com frete: R$ {total_with_shipping:.2f}")

    # 4. Aplicar descontos
    final_amount = discount_service.calculate(total_with_shipping, user_data)
    print(f"Valor final após descontos: R$ {final_amount:.2f}")

    # 5. Processar pagamento
    payment_result = payment_service.process(user_data, round(final_amount, 2))

    print(f"--- Checkout finalizado! Resultado: {payment_result} ---")
    return {"success": True, "payment_details": payment_result}

