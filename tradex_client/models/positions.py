from dataclasses import dataclass, field, asdict
from typing import List
from decimal import Decimal

@dataclass
class NetPositionData:
    client: str
    exchange: str
    code: str
    instrument: str
    symbol: str
    series: str
    strike_price: Decimal
    option_type: str
    product: str
    lot_size: int
    multiplier: int
    buy_avg: Decimal
    buy_qty: int
    buy_value: Decimal
    sell_avg: Decimal
    sell_qty: int
    sell_value: Decimal
    net_price: Decimal
    net_qty: int
    net_value: Decimal
    mtm: Decimal
    unrealized_mtm: Decimal
    realized_mtm: Decimal
    market_price: Decimal
    close_price: Decimal
    breakeven_point: Decimal
    intrinsic_value: Decimal
    extrinsic_value: Decimal
    
    def get_dict(self):
        return asdict(self)
    
    @staticmethod
    def parse_list(response):
        return [
            NetPositionData(
                client=item["client"],
                exchange=item["exchange"],
                code=item["code"],
                instrument=item["instrument"],
                symbol=item["symbol"],
                series=item["series"],
                strike_price=item["strike_price"],
                option_type=item["option_type"],
                product=item["product"],
                lot_size=item["lot_size"],
                multiplier=item["multiplier"],
                buy_avg=item["buy_avg"],
                buy_qty=item["buy_qty"],
                buy_value=item["buy_value"],
                sell_avg=item["sell_avg"],
                sell_qty=item["sell_qty"],
                sell_value=item["sell_value"],
                net_price=item["net_price"],
                net_qty=item["net_qty"],
                net_value=item["net_value"],
                mtm=item["mtm"],
                unrealized_mtm=item["unrealized_mtm"],
                realized_mtm=item["realized_mtm"],
                market_price=item["market_price"],
                close_price=item["close_price"],
                breakeven_point=item["breakeven_point"],
                intrinsic_value=item["intrinsic_value"],
                extrinsic_value=item["extrinsic_value"]
            ) for item in response.get("data", [])
        ]

@dataclass
class NetPositionResponse:
    status: int
    message: str
    data: List[NetPositionData] = field(default_factory=list)
    
    def get_dict(self):
        return asdict(self)
