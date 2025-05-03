from ..constants import *

from typing import Optional
from dataclasses import dataclass, asdict, field
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class ModifyOrderRequest:
    book: str
    code: str
    disclosed_qty: int
    exchange: str
    exchange_order_no: str
    gtd: str
    order_flag: int
    price: float
    product: str
    qty_remaining: int
    qty_traded: int
    quantity: int
    sender_order_no: int
    side: str
    trigger_price: float
    validity: str
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
        
        if self.qty_remaining < 0:
            raise ValueError("Quantity remaining must not be less than zero.")
        
        if self.qty_traded < 0:
            raise ValueError("Quantity traded must not be less than zero.")

        if self.trigger_price < 0:
            raise ValueError("Trigger price cannot be negative.")
        
        if self.price < 0:
            raise ValueError("Price cannot be negative.")

    def get_dict(self):
        return asdict(self)

@dataclass
class ModifyOrderData:
    client: str
    exchange_order_no: str
    user_order_no: int
    sender_order_no: int
    
    def get_dict(self):
        return asdict(self)

@dataclass
class ModifyOrderResponse:
    status: int
    message: str
    data: Optional[ModifyOrderData]
    
    def get_dict(self):
        return asdict(self)