from api.base import BaseAPI

from models.bank import AllBankItems
from models.map import AllMaps
from models.character import Character

from typing import AnyStr


class BankAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_quantity(self, item_code: AnyStr) -> int:
        params = {
            "item_code": item_code
        }

        code, response = self.get(
            method="/my/bank/items",
            params=params
        )

        if code == 404:
            return 0

        return response["data"][0]["quantity"]

    @staticmethod
    def get_map(character: Character, maps: AllMaps):
        return maps.closest(
            character=character,
            content_code="bank"
        )

    def get_all_items(self) -> AllBankItems:
        all_data = self.get_all(
            method="/my/bank/items"
        )
        return AllBankItems(items=all_data)
