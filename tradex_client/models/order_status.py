from ..constants import *

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class OrderStatusData:
    exchange: str
    # client: str
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
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

        if self.price < 0:
            raise ValueError("Price must not be less than zero.")

        if self.strike_price < 0:
            raise ValueError("Strike price must not be less than zero.")

        if self.average_fill_price < 0:
            raise ValueError("Average fill price must not be less than zero.")

        if self.trigger < 0:
            raise ValueError("Trigger price cannot be negative.")

        if self.qty_remaining < 0:
            raise ValueError("Remaining quantity cannot be negative.")

        if self.qty_traded < 0:
            raise ValueError("Traded quantity cannot be negative.")

        if self.disc_qty < 0:
            raise ValueError("Disclosed quantity cannot be negative.")

        if self.algol_id < 0:
            raise ValueError("Algorithm ID cannot be negative.")

    def get_dict(self):
        data = asdict(self)
        for key in ["client_entry_time", "entry_at", "last_modified"]:
            if isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data
    
    @staticmethod
    def parse_list(response):
        return [
            OrderStatusData(
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
class OrderStatusRequest:
    exchange: str
    code: str
    exchange_order_no: str
    sender_order_no: int
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)

    def __post_init__(self):
        if self.exchange not in valid_exchanges:
            raise ValueError(f"Invalid exchange: {self.exchange}. Allowed: {valid_exchanges}")
    
    def get_dict(self):
        return asdict(self)
    
@dataclass
class OrderStatusResponse:
    status: int
    message: str
    data: Any

    def get_dict(self):
        result = {
            "status": self.status,
            "message": self.message,
            "data": [item.get_dict() for item in self.data]
        }
        return result