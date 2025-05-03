from ..constants import valid_exchanges, valid_sides

from dataclasses import dataclass, field, asdict
from typing import List
from datetime import datetime

@dataclass
class GTTOrderBookData:
    client: str
    modified_by: str
    created_by: str
    exchange: str
    code: str
    symbol: str
    series: str
    strike: float
    option_type: str
    side: str
    product: str
    qty: int
    main_trigger_price: float
    main_order_price: float
    main_state: str
    price_condition: str
    stop_state: str
    stop_trigger_price: float
    stop_order_price: float 
    trail_gap: float
    target_state: str
    target_trigger_price: float
    target_order_price: float
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

    def __post_init__(self):
        self.strike = float(self.strike) if isinstance(self.strike, str) and self.strike else 0.0
        self.main_order_price = float(self.main_order_price) if isinstance(self.main_order_price, str) and self.main_order_price else 0.0
        self.stop_order_price = float(self.stop_order_price) if isinstance(self.stop_order_price, str) and self.stop_order_price else 0.0
        self.target_order_price = float(self.target_order_price) if isinstance(self.target_order_price, str) and self.target_order_price else 0.0
        
        if self.side not in valid_sides:
            raise ValueError(f"Invalid order side: {self.side}. Allowed Sides: {valid_sides}")

        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")
    
    def get_dict(self):
        return asdict(self)
    
    @staticmethod
    def parse_list(response):
        return [
            GTTOrderBookData(
                client=item["client"],
                modified_by=item["modified_by"],
                created_by=item["created_by"],
                exchange=item["exchange"],
                code=item["code"],
                symbol=item["symbol"],
                series=item["series"],
                strike=item["strike"],
                option_type=item["option_type"],
                side=item["side"],
                product=item["product"],
                qty=item["qty"],
                main_trigger_price=item["main_trigger_price"],
                main_order_price=item["main_order_price"],
                main_state=item["main_state"],
                price_condition=item["price_condition"],
                stop_state=item["stop_state"],
                stop_trigger_price=item["stop_trigger_price"],
                stop_order_price=item["stop_order_price"],
                trail_gap=item["trail_gap"],
                target_state=item["target_state"],
                target_trigger_price=item["target_trigger_price"],
                target_order_price=item["target_order_price"], 
                trail_distance=item["trail_distance"],
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                last_modified=datetime.fromisoformat(item["last_modified"].replace("Z", "+00:00")),
                gtt_order_no=item["gtt_order_no"],
                module=item["module"],
                filled_qty=item["filled_qty"],
                filled_value=item["filled_value"],
                exit_qty=item["exit_qty"],
                exit_value=item["exit_value"],
                reason=item["reason"],
                flags=item["flags"],
                api_source=item["api_source"],
                sender_order_no=item["sender_order_no"]
            ) for item in response.get("data", [])
        ]

@dataclass
class GTTOrdersBookResponse:
    status: int
    message: str
    data: List[GTTOrderBookData] = field(default_factory=list)
    
    def get_dict(self):
        return asdict(self)