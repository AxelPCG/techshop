from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from decimal import Decimal


class Product(BaseModel):
    """Modelo de produto com validação de tipos.

    Attributes:
        id: Identificador único do produto.
        name: Nome do produto.
        price: Preço unitário em reais.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(..., gt=0, description="ID do produto")
    name: str = Field(..., min_length=1, description="Nome do produto")
    price: Decimal = Field(..., gt=0, description="Preço unitário em R$")


class CartItem(BaseModel):
    """Item do carrinho de compras.

    Attributes:
        product: Dados do produto.
        quantity: Quantidade de itens.
    """
    product: Product
    quantity: int = Field(..., gt=0, description="Quantidade de itens")


class CheckoutRequest(BaseModel):
    """Requisição de checkout validada.

    Attributes:
        user_id: Identificador do usuário.
        is_vip: Se o usuário possui status VIP.
        cart_items: Lista de itens do carrinho.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 123,
                "is_vip": True,
                "cart_items": [
                    {
                        "product": {"id": 1, "name": "Laptop", "price": 2000.00},
                        "quantity": 1
                    }
                ]
            }
        }
    )

    user_id: int = Field(..., gt=0, description="ID do usuário")
    is_vip: bool = Field(default=False, description="Status VIP do usuário")
    cart_items: List[CartItem] = Field(..., min_length=1, description="Itens do carrinho")


class PaymentResponse(BaseModel):
    """Resposta da API de pagamento com validação.

    Attributes:
        status: Status do pagamento.
        transaction_id: ID único da transação.
    """
    status: str = Field(..., description="Status do pagamento")
    transaction_id: str = Field(..., description="ID da transação")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Valida que o status está entre os valores permitidos.

        Args:
            v: Valor do status a validar.

        Returns:
            str: Status validado.

        Raises:
            ValueError: Se status não for válido.
        """
        if v not in ['pagamento_aprovado', 'pagamento_recusado']:
            raise ValueError('Status inválido')
        return v


class CheckoutResult(BaseModel):
    """Resultado final do checkout com tipagem garantida.

    Attributes:
        success: Se o checkout foi bem-sucedido.
        transaction_id: ID da transação (se bem-sucedido).
        error: Mensagem de erro (se mal-sucedido).
    """
    success: bool = Field(..., description="Sucesso do checkout")
    transaction_id: Optional[str] = Field(
        default=None,
        description="ID da transação bem-sucedida"
    )
    error: Optional[str] = Field(
        default=None,
        description="Mensagem de erro"
    )

    @field_validator('transaction_id')
    @classmethod
    def validate_transaction(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que transaction_id existe apenas se success=True.

        Args:
            v: Valor do transaction_id.
            info: Contexto de validação com dados do modelo.

        Returns:
            Optional[str]: transaction_id validado.

        Raises:
            ValueError: Se lógica inconsistente.
        """
        success = info.data.get('success')
        if success and not v:
            raise ValueError('transaction_id obrigatório quando success=True')
        if not success and v:
            raise ValueError('transaction_id deve ser None quando success=False')
        return v
