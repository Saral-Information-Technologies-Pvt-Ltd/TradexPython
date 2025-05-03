from dataclasses import dataclass, field, asdict
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class ExecuteBasketData:
    client: str
    exchange: str
    code: str
    side: str
    quantity: int
    price: float
    book: str
    trigger_price: float
    disclosed_qty: int
    product: str
    validity: str
    gtd: str
    order_flag: int
    sender_order_no: int
    algol_id: int
    
    def get_dict(self):
        return asdict(self)

@dataclass
class ExecuteBasketOrderRequest:
    orders: List[ExecuteBasketData] = field(default_factory=list)
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def get_dict(self):
        return asdict(self)
    
@dataclass
class ExecuteBasketResponse:
    status: int
    message: str
    data: Optional[ExecuteBasketData]
    
    def get_dict(self):
        return asdict(self)

