from api.base import BaseAPI

from models.bank import AllBankItems
from models.map import AllMaps
from models.character import Character
from models.item import Item

from typing import AnyStr, List


class Reserve:
    def __init__(self, code: AnyStr, quantity: int, reverved_by: AnyStr) -> None:
        self.code = code
        self.quantity = quantity
        self.reverved_by = reverved_by

    def __eq__(self, value: "Reserve") -> bool:
        return (
            self.code == value.code
            and self.quantity == value.quantity
            and self.reverved_by == value.reverved_by
        )


class BankAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()
        self.reserves: List[Reserve] = []

    def add_reserve(self, item_code: AnyStr, quantity: int, reverved_by: AnyStr):
        self.reserves.append(
            Reserve(code=item_code, quantity=quantity, reverved_by=reverved_by)
        )

    def delete_reserve(self, item_code: AnyStr, quantity: int, reverved_by: AnyStr):
        to_delete = Reserve(code=item_code, quantity=quantity, reverved_by=reverved_by)
        for i in range(len(self.reserves)):
            if self.reserves[i] == to_delete:
                del self.reserves[i]
                break

    def get_quantity(self, item_code: AnyStr, character_name: AnyStr) -> int:
        params = {"item_code": item_code}

        code, response = self.get(method="/my/bank/items", params=params)

        if code == 404:
            return 0

        total_reserve = 0
        for reserve in self.reserves:
            if reserve.reverved_by == character_name and reserve.code == item_code:
                break
            if reserve.reverved_by != character_name and reserve.code == item_code:
                total_reserve += reserve.quantity

        return max(response["data"][0]["quantity"] - total_reserve, 0)

    @staticmethod
    def get_map(character: Character, maps: AllMaps):
        return maps.closest(character=character, content_code="bank")

    def get_all_items(self) -> AllBankItems:
        all_data = self.get_all(method="/my/bank/items")
        return AllBankItems(items=all_data)

    def has_item(self, item: Item) -> bool:
        code, _ = self.get(method="/my/bank/items", params={"item_code": item.code})
        return code == 200
