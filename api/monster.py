from api.base import BaseAPI

from models.monster import AllMonsters


class MonsterAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_all_monsters(self) -> AllMonsters:
        all_data = self.get_all(
            method="/monsters"
        )
        return AllMonsters(monsters=all_data)
