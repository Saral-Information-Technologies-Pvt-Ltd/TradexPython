from dataclasses import dataclass, field, asdict
from typing import List
from datetime import datetime

@dataclass
class TradesBookData:
    client: str
    exchange: str
    code: str
    symbol: str
    series: str
    strike_price: float
    option_type: str
    instrument: str
    user: str
    generated_by: str
    api_source: str
    side: str
    traded_qty: int
    traded_price: float
    traded_value: float
    qty_remaining: int
    qty_cumulative: int
    trade_time: datetime
    product: str
    order_category: str
    order_book: str
    order_validity: str
    order_price: float
    order_qty: int
    order_trigger: float
    average_fill_price: float
    order_status: str
    order_disc_qty: int
    order_entry_at: datetime
    order_last_modified: datetime
    trade_no: str
    exchange_order_no: str
    sender_order_no: int
    user_order_no: int
    algol_id: int
    
    def get_dict(self):
        data = asdict(self)
        for key in ["trade_time", "order_entry_at", "order_last_modified"]:
            if isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data
    
    @staticmethod
    def parse_list(response):
        return [
            TradesBookData(
                exchange=item["exchange"],
                code=item["code"],
                symbol=item["symbol"],
                series=item["series"],
                strike_price=item["strike_price"],
                option_type=item["option_type"],
                instrument=item["instrument"],
                client=item["client"],
                user=item["user"],
                generated_by=item["generated_by"],
                api_source=item["api_source"],
                side=item["side"],
                traded_qty=item["traded_qty"],
                traded_price=item["traded_price"],
                traded_value=item["traded_value"],
                qty_remaining=item["qty_remaining"],
                qty_cumulative=item["qty_cumulative"],
                trade_time=datetime.fromisoformat(item["trade_time"].replace("Z", "+00:00")),
                product=item["product"],
                order_category=item["order_category"],
                order_book=item["order_book"],
                order_validity=item["order_validity"],
                order_price=item["order_price"],
                order_qty=item["order_qty"],
                order_trigger=item["order_trigger"],
                average_fill_price=item["average_fill_price"],
                order_status=item["order_status"],
                order_disc_qty=item["order_disc_qty"],
                order_entry_at=datetime.fromisoformat(item["order_entry_at"].replace("Z", "+00:00")),
                order_last_modified=datetime.fromisoformat(item["order_last_modified"].replace("Z", "+00:00")),
                trade_no=item["trade_no"],
                exchange_order_no=item["exchange_order_no"],
                sender_order_no=item["sender_order_no"],
                user_order_no=item["user_order_no"],
                algol_id=item["algol_id"]
            ) for item in response.get("data", [])
        ]

@dataclass
class TradesBookResponse:
    status: int
    message: str
    data: List[TradesBookData] = field(default_factory=list)

    def get_dict(self):
        result = {
            "status": self.status,
            "message": self.message,
            "data": [item.get_dict() for item in self.data]
        }
        return result