from dataclasses import dataclass
from typing import Dict, List, AnyStr


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

    def get_quantity(self, item_code: AnyStr, *args, **kargs):
        for item in self.items:
            if item.code == item_code:
                return item.quantity
        return 0
