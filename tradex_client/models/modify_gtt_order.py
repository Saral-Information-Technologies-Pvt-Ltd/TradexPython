from ..constants import valid_exchanges, valid_sides, valid_products

from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class ModifyGTTOrderRequest:
    gtt_order_no: int
    exchange: str
    code: str
    side: str
    product: str
    qty: int
    price_condition: str
    main_trigger_price: float
    main_order_price: str
    main_state: str
    stop_state: str
    stop_trigger_price: float
    stop_order_price: str
    trail_gap: float
    target_state: str
    target_trigger_price: float
    target_order_price: str
    sender_order_no: int
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")
        
        if self.side not in valid_sides:
            raise ValueError(f"Invalid order side: {self.side}. Allowed Sides: {valid_sides}")
        
        if self.product not in valid_products:
            raise ValueError(f"Invalid product: {self.product}. Allowed Products: {valid_products}")
       
        if self.qty < 0:
            raise ValueError("Quantity must not be less than zero.")
        
        if self.main_trigger_price < 0:
            raise ValueError("Main trigger price must not be less than zero.")
        
        if self.stop_trigger_price < 0:
            raise ValueError("Stop trigger price must not be less than zero.")
        
        if self.target_trigger_price < 0:
            raise ValueError("Target trigger price cannot be negative.")

    def get_dict(self):
        return asdict(self)


@dataclass
class ModifyGTTOrderData:
    client: str
    modified_by: str
    created_by: str
    exchange: str
    code: str
    symbol: str
    series: str
    strike: str
    option_type: str
    side: str
    product: str
    qty: int
    main_trigger_price: float
    main_order_price: str
    main_state: str
    price_condition: str
    stop_state: str
    stop_trigger_price: float
    stop_order_price: str
    trail_gap: float
    target_state: str
    target_trigger_price: float
    target_order_price: str
    trail_distance: float
    created_at: datetime
    last_modified: datetime
    gtt_order_no: int
    module: str
    filled_qty: int
    filled_value: float
    exit_qty: int
    exit_value: float
    reason: str
    flags: int
    api_source: str
    sender_order_no: int
    
    def get_dict(self):
        return asdict(self)

@dataclass
class ModifyGTTOrderResponse:
    status: int
    message: str
    data: Optional[ModifyGTTOrderData]
    
    def get_dict(self):
        return asdict(self)
