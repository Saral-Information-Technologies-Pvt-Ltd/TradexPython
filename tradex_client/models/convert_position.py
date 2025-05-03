from ..constants import valid_exchanges, valid_products, valid_sides

from dataclasses import dataclass, asdict, field
from typing import Optional, Any
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class ConvertPositionRequest:
    code: str
    exchange: str
    new_product: str
    old_product: str
    qty: int
    side: str
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")
        
        if self.side not in valid_sides:
            raise ValueError(f"Invalid order side: {self.side}. Allowed Sides: {valid_sides}")
        
        if self.old_product not in valid_products:
            raise ValueError(f"Invalid old product: {self.old_product}. Allowed Products: {valid_products}")
        
        if self.new_product not in valid_products:
            raise ValueError(f"Invalid new product: {self.new_product}. Allowed Products: {valid_products}")
        
        if self.qty <= 0:
            raise ValueError("Quantity must be greater than zero.")
    
    def get_dict(self):
        return asdict(self)

@dataclass
class ConvertPositionData:
    status: str
    user_order_no: int
    message: str
    
    def get_dict(self):
        return asdict(self)

@dataclass
class ConvertPositionResponse:
    status: int
    message: str
    data: Optional[Any]
    
    def get_dict(self):
        return asdict(self)