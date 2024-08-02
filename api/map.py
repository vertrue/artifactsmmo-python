from api.base import BaseAPI

from models.map import AllMaps


class MapAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_all_maps(self) -> AllMaps:
        all_data = self.get_all(method="/maps")
        return AllMaps(maps=all_data)
