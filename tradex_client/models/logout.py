from dataclasses import dataclass, asdict

@dataclass
class LogoutData:
    status: int
    message: str
    data: str

    def get_dict(self):
        return asdict(self)