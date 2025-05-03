from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class UserProfileData:
    client_id: str
    name: str
    mobile: str
    email: str
    trading_allowed: str
    products_allowed: str
    pan: str
    dp_id: str
    beneficiary_id: str
    has_poa: bool
    
    def get_dict(self):
        return asdict(self)

@dataclass
class UserProfileResponse:
    status: int
    message: str
    data: Optional[UserProfileData]

    def get_dict(self):
        return asdict(self)
    