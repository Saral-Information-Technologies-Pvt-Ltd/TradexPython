from dataclasses import dataclass, field, asdict
from typing import List

@dataclass
class ExchangeStatusData:
    exchange: str
    isConnected: bool
    session: str
    
    def get_dict(self):
        return asdict(self)
    
    @staticmethod
    def parse_list(response):
        return [
            ExchangeStatusData(
                exchange=item["exchange"],
                isConnected=item["isConnected"],
                session=item["session"]
            ) for item in response.get("data", [])
        ]

@dataclass
class ExchangeStatusResponse:
    status: int
    message: str
    data: List[ExchangeStatusData] = field(default_factory=list)
    
    def get_dict(self):
        return asdict(self)
    