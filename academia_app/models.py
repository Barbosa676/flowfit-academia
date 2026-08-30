from dataclasses import dataclass

@dataclass
class Client:
    id: int
    name: str
    email: str | None
    phone: str | None
