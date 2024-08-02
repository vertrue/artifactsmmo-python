from api.base import BaseAPI

from models.resource import AllResources


class ResourceAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_all_resources(self) -> AllResources:
        all_data = self.get_all(
            method="/resources"
        )
        return AllResources(resources=all_data)
