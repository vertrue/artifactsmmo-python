from api.base import BaseAPI

from models.item import AllItems


class ItemAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_all_items(self) -> AllItems:
        all_data = self.get_all(method="/items")
        return AllItems(items=all_data)
