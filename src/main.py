from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any

from .models import CartItem, UserData, Product
from .cart import ShoppingCart
from .checkout import (
    process_checkout,
    StockValidator,
    ShippingService,
    DiscountService,
    PaymentService,
    FakePaymentAPI,
)

app = FastAPI(
    title="TechShop API",
    description="API para um e-commerce de tecnologia, com gerenciamento de carrinho e checkout.",
    version="1.0.0",
)

# Monta a pasta 'static' para servir arquivos estáticos (nosso frontend)
app.mount("/app", StaticFiles(directory="static", html=True), name="static")

# --- Simulação de um "banco de dados" em memória para o carrinho ---
# Em uma aplicação real, isso seria substituído por um banco de dados (Redis, PostgreSQL, etc.)
shopping_cart_db: Dict[int, ShoppingCart] = {
    1: ShoppingCart() # Carrinho para o usuário com ID 1
}

# --- Injeção de Dependências (FastAPI Depends) ---

def get_cart(user_id: int = 1) -> ShoppingCart:
    """Retorna a instância do carrinho de compras para o usuário."""
    cart = shopping_cart_db.get(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado para o usuário.")
    return cart

# Instâncias dos serviços que serão injetados
stock_validator = StockValidator()
shipping_service = ShippingService()
discount_service = DiscountService()
payment_api = FakePaymentAPI()
payment_service = PaymentService(payment_api=payment_api)


# --- Rotas da API ---

@app.post("/cart/add", response_model=CartItem, tags=["Carrinho"])
def add_to_cart(item: CartItem, cart: ShoppingCart = Depends(get_cart)):
    """
    Adiciona um item ao carrinho de compras do usuário.

    Se o produto já existir no carrinho, a quantidade será somada.
    """
    cart.add_item(item.product, item.quantity)
    return item

@app.get("/cart", tags=["Carrinho"])
def get_cart_details(cart: ShoppingCart = Depends(get_cart)):
    """
    Retorna os detalhes do carrinho de compras do usuário, incluindo
    os itens, o subtotal e o total com descontos aplicados.
    """
    return {
        "items": cart.items,
        "subtotal": cart.calculate_total(),
        "total_with_discount": cart.calculate_total_with_discount(),
    }

@app.post("/checkout", tags=["Checkout"])
def perform_checkout(user_data: UserData, cart: ShoppingCart = Depends(get_cart)):
    """
    Processa o checkout do carrinho de compras.

    Realiza a validação de estoque, cálculo de frete, aplicação de descontos
    e processamento do pagamento.
    """
    if not cart.items:
        raise HTTPException(status_code=400, detail="Carrinho está vazio.")

    try:
        result = process_checkout(
            cart_items=cart.items,
            user_data=user_data,
            stock_validator=stock_validator,
            shipping_service=shipping_service,
            discount_service=discount_service,
            payment_service=payment_service,
        )
        # Limpa o carrinho após checkout bem-sucedido
        cart.items.clear()
        return {"status": "Sucesso", "details": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # Captura genérica para outros erros inesperados
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {e}")

