from dataclasses import dataclass
from typing import Dict, List


@dataclass
class GreatExchange:
    code: str
    stock: int
    sell_price: int
    buy_price: int

    @staticmethod
    def from_dict(data: Dict) -> "GreatExchange":
        return GreatExchange(
            code=data.get("code", ""),
            stock=data.get("stock", 0),
            sell_price=data.get("sell_price", 0),
            buy_price=data.get("buy_price", 0),
        )


class AllGreatExchange:
    def __init__(self, items: List[Dict]) -> None:
        self.items = [GreatExchange.from_dict(item) for item in items]
