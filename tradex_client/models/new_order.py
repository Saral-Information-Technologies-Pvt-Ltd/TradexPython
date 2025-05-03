from ..constants import *

from typing import Optional
from dataclasses import dataclass, asdict, field
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class NewOrderRequest:
    algol_id: int
    book: str
    code: str
    disclosed_qty: int
    exchange: str
    gtd: str
    price: float
    product: str
    quantity: int
    sender_order_no: int
    side: str
    trigger_price: float
    validity: str
    order_flag: int
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")
        
        if self.side not in valid_sides:
            raise ValueError(f"Invalid order side: {self.side}. Allowed Sides: {valid_sides}")
        
        if self.product not in valid_products:
            raise ValueError(f"Invalid product: {self.product}. Allowed Products: {valid_products}")
        
        if self.validity not in valid_validity:
            raise ValueError(f"Invalid validity: {self.validity}. Allowed Validity: {valid_validity}")
        
        if self.book not in valid_books:
            raise ValueError(f"Invalid book: {self.book}. Allowed Books: {valid_books}")
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        
        if self.trigger_price < 0:
            raise ValueError("Target trigger price cannot be negative.")

    def get_dict(self):
        return asdict(self)

@dataclass
class NewOrderData:
    user_order_no: str
    sender_order_no: str
    client: str
    
    def get_dict(self):
        return asdict(self)

@dataclass
class NewOrderResponse:
    status: int
    message: str
    data: Optional[NewOrderData]
    
    def get_dict(self):
        return asdict(self)