from ..constants import valid_exchanges

from dataclasses import dataclass, asdict, field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class CancelOrderRequest:
    code: str
    exchange: str
    exchange_order_no: str
    user_order_no: int
    sender_order_no: int
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")

    def get_dict(self):
        return asdict(self)

@dataclass
class CancelOrderData:
    client: str
    exchange_order_no: int
    user_order_no: int
    sender_order_no: int
    
    def get_dict(self):
        return asdict(self)

@dataclass
class CancelOrderResponse:
    status: str
    message: str
    data: Optional[CancelOrderData]

    def get_dict(self):
        return asdict(self)