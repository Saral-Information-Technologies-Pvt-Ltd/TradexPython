from dataclasses import dataclass, field, asdict
from typing import List

@dataclass
class FundsReportData:
    client_id: str
    limit_id: str
    cash: str
    adhoc: str
    payin: str
    collateral: str
    cnc_sell_benefit: str
    payout: str
    costs: str
    margin_used: str
    margin_available: str
    cash_available: str
    
    def get_dict(self):
        return asdict(self)
    
    @staticmethod
    def parse_list(response):
        return [
            FundsReportData(
                client_id=item["client_id"],
                limit_id=item["limit_id"],
                cash=item["cash"],
                adhoc=item["adhoc"],
                payin=item["payin"],
                collateral=item["collateral"],
                cnc_sell_benefit=item["cnc_sell_benefit"],
                payout=item["payout"],
                costs=item["costs"],
                margin_used=item["margin_used"],
                margin_available=item["margin_available"],
                cash_available=item["cash_available"]
            ) for item in response.get("data", [])
        ]

@dataclass
class FundsReportResponse:
    status: int
    message: str
    data: List[FundsReportData] = field(default_factory=list)
    
    def get_dict(self):
        return asdict(self)
