from api.base import BaseAPI

from models.character import Character

from typing import AnyStr, List


class MyCharactersAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_all(self) -> List[Character]:
        code, response = self.get(method="/my/characters")

        all_characters = []
        for character in response["data"]:
            all_characters.append(
                Character.from_dict(character)
            )
        return all_characters
