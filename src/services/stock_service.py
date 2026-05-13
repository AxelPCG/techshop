"""Serviço de validação de estoque.

Responsabilidade única: validar disponibilidade de produtos em estoque.
"""

from typing import List, Tuple, Protocol
from src.models import CartItem


class WarehouseAPI(Protocol):
    """Protocol para API de warehouse (abstração para injeção de dependência).

    Define o contrato que qualquer implementação de warehouse deve seguir.
    """

    def get_stock(self, product_id: int) -> int:
        """Obtém a quantidade em estoque de um produto.

        Args:
            product_id: ID do produto.

        Returns:
            int: Quantidade disponível em estoque.
        """
        ...


class StockService:
    """Serviço de validação de estoque com responsabilidade única.

    Valida se há estoque suficiente para os itens do carrinho.
    Não calcula preços, não processa pagamentos.

    Attributes:
        warehouse_api: Implementação de acesso ao warehouse.
    """

    def __init__(self, warehouse_api: WarehouseAPI) -> None:
        """Inicializa o serviço com a dependência de warehouse.

        Args:
            warehouse_api: Implementação da API de warehouse.
        """
        self.warehouse_api = warehouse_api

    def validate_stock(self, items: List[CartItem]) -> Tuple[bool, str]:
        """Valida se há estoque suficiente para todos os itens.

        Args:
            items: Lista de itens do carrinho a validar.

        Returns:
            Tuple[bool, str]: (tem_estoque, mensagem_erro)
                Se há estoque: (True, "")
                Se falta: (False, "Mensagem de erro descritiva")

        Example:
            >>> service = StockService(warehouse_api=mock_api)
            >>> has_stock, error = service.validate_stock([item1, item2])
            >>> if not has_stock:
            ...     print(f"Erro: {error}")
        """
        for item in items:
            available: int = self.warehouse_api.get_stock(item.product.id)

            if available < item.quantity:
                return (
                    False,
                    f"Estoque insuficiente para '{item.product.name}': "
                    f"disponível {available}, solicitado {item.quantity}"
                )

        return True, ""
