from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class CancelGTTOrderData:
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
class CancelGTTOrderResponse:
    status: int
    message: str
    data: Optional[CancelGTTOrderData]
    
    def get_dict(self):
        return asdict(self)