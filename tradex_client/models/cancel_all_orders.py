from ..constants import valid_exchanges

from dataclasses import dataclass, asdict, field
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class CancelAllOrderRequest:
    code: int
    exchange: str
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")

    def get_dict(self):
        return asdict(self)

@dataclass
class CancelAllOrderResponse:
    status: int
    message: str
    
    def get_dict(self):
        return asdict(self)
