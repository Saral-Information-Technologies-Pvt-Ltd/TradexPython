from typing import Optional, Union
from dataclasses import dataclass, asdict, field
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT = os.getenv("CLIENT_ID")

@dataclass
class LoginRequest:
    app_key: str
    secret_key: str
    source: str
    client: str = field(default_factory=lambda: DEFAULT_CLIENT)
    
    def get_dict(self):
        return asdict(self)

@dataclass
class LoginData:
    user_id: str
    exchanges_allowed: str
    products_allowed: str
    token: str
    
    def get_dict(self):
        return asdict(self)

@dataclass
class LoginResponse:
    status: Union[str, int]
    message: str
    data: Optional[LoginData]
    
    def get_dict(self):
        return asdict(self)