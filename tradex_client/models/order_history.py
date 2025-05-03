from ..constants import valid_exchanges

from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class OrderHistoryRequest:
    exchange: str
    code: str
    exchange_order_no: str
    sender_order_no: int
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)

    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed Exchanges: {valid_exchanges}")

    def get_dict(self):
        return asdict(self)

@dataclass
class OrderHistoryData:
    client: str
    exchange: str
    code: str
    symbol: str
    series: str
    instrument: str
    strike_price: float
    option_type: str
    user: str
    settlor: str
    api_source: str
    executing_id: str
    generated_by: str
    status: str
    side: str
    book: str
    product: str
    validity: str
    price: float
    trigger: float
    average_fill_price: float
    qty_remaining: int
    qty_traded: int
    disc_qty: int
    flags: str
    reason: str
    gtd: str
    client_entry_time: datetime
    entry_at: datetime
    last_modified: datetime
    exchange_order_no: str
    user_order_no: int
    sender_order_no: int
    auction_number: int
    order_category: str
    algol_id: int
    
    def get_dict(self):
        data = asdict(self)
        for key in ["client_entry_time", "entry_at", "last_modified"]:
            if isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data

    @staticmethod
    def parse_list(response):
        return [
            OrderHistoryData(
                exchange=item["exchange"],
                code=item["code"],
                symbol=item["symbol"],
                series=item["series"],
                instrument=item["instrument"],
                strike_price=item["strike_price"],
                option_type=item["option_type"],
                client=item["client"],
                user=item["user"],
                settlor=item["settlor"],
                api_source=item["api_source"],
                executing_id=item["executing_id"],
                generated_by=item["generated_by"],
                status=item["status"],
                side=item["side"],
                book=item["book"],
                product=item["product"],
                validity=item["validity"],
                price=item["price"],
                trigger=item["trigger"],
                average_fill_price=item["average_fill_price"],
                qty_remaining=item["qty_remaining"],
                qty_traded=item["qty_traded"],
                disc_qty=item["disc_qty"],
                flags=item["flags"],
                reason=item["reason"],
                gtd=item["gtd"],
                client_entry_time=datetime.fromisoformat(item["client_entry_time"].replace("Z", "+00:00")),
                entry_at=datetime.fromisoformat(item["entry_at"].replace("Z", "+00:00")),
                last_modified=datetime.fromisoformat(item["last_modified"].replace("Z", "+00:00")),
                exchange_order_no=item["exchange_order_no"],
                user_order_no=item["user_order_no"],
                sender_order_no=item["sender_order_no"],
                auction_number=item["auction_number"],
                order_category=item["order_category"],
                algol_id=item["algol_id"]
            ) for item in response.get("data", [])
        ]

@dataclass
class OrderHistoryResponse:
    status: int
    message: str
    data: List[OrderHistoryData] = field(default_factory=list)
    
    def get_dict(self):
        result = {
            "status": self.status,
            "message": self.message,
            "data": [item.get_dict() for item in self.data]
        }
        return result