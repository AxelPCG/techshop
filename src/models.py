from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float

class CartItem(BaseModel):
    product: Product
    quantity: int

class UserData(BaseModel):
    id: int
    is_vip: bool = False
