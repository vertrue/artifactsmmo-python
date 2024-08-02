from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Bank:
    code: str
    quantity: int

    @staticmethod
    def from_dict(data: Dict) -> "Bank":
        return Bank(code=data.get("code", ""), quantity=data.get("quantity", 0))


class AllBankItems:
    def __init__(self, items: List[Dict]) -> None:
        self.items = [Bank.from_dict(item) for item in items]
