from dataclasses import dataclass, field, asdict
from typing import List
from decimal import Decimal

@dataclass
class HoldingsData:
    client: str
    isin: str
    nse_name: str
    bse_name: str
    bse_code: str
    nse_code: str
    nse_ltp: Decimal
    bse_ltp: Decimal
    position: int
    free_qty: int
    collateral_qty: int
    pledged_qty: int
    btst_qty: int
    blocked_qty: int
    non_poa_qty: int
    value: Decimal
    collateral_value: Decimal
    buy_price: Decimal
    close_price: Decimal
    
    def get_dict(self):
        return asdict(self)
    
    @staticmethod
    def parse_list(response):
        return [
            HoldingsData(
                client=item["client"],
                isin=item["isin"],
                nse_name=item["nse_name"],
                bse_name=item["bse_name"],
                bse_code=item["bse_code"],
                nse_code=item["nse_code"],
                nse_ltp=item["nse_ltp"],
                bse_ltp=item["bse_ltp"],
                position=item["position"],
                free_qty=item["free_qty"],
                collateral_qty=item["collateral_qty"],
                pledged_qty=item["pledged_qty"],
                btst_qty=item["btst_qty"],
                blocked_qty=item["blocked_qty"],
                non_poa_qty=item["non_poa_qty"],
                value=item["value"],
                collateral_value=item["collateral_value"],
                buy_price=item["buy_price"],
                close_price=item["close_price"]
            ) for item in response.get("data", [])
        ]

@dataclass
class HoldingsResponse:
    status: int
    message: str
    data: List[HoldingsData] = field(default_factory=list)
    
    def get_dict(self):
        return asdict(self)