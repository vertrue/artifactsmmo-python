from api.map import MapAPI
from api.resource import ResourceAPI
from api.bank import BankAPI

from models.character import Character
from models.item import Item

from models.map import Map

from typing import AnyStr


class MyCharacterAPI(MapAPI):
    def __init__(self, character: Character) -> None:
        super().__init__()
        self.character = character

    def move(self, target: Map) -> None:
        if (self.character.x, self.character.y) == (target.x, target.y):
            return

        print(f"{self.character.name} is moving to ({target.x}, {target.y})")
        method = f"/my/{self.character.name}/action/move"
        self.post(
                method=method,
                body={
                    "x": target.x,
                    "y": target.y
                }
            )
        self._update_character()

    def fight(self):
        method = f"/my/{self.character.name}/action/fight"
        self.post(method=method)

        self._update_character()

    def gather(self):
        method = f"/my/{self.character.name}/action/gathering"
        self.post(method=method)

        self._update_character()

    def craft(self, code: AnyStr):
        method = f"/my/{self.character.name}/action/crafting"

        self.post(
            method=method,
            body={
                "code": code
            }
        )

        self._update_character()

    def unequip(self, slot: AnyStr) -> bool:
        method = f"/my/{self.character.name}/action/unequip"

        response_code, response_data = self.post(
            method=method,
            body={
                "slot": slot
            }
        )

        return response_code == 200

    def equip(self, code: AnyStr, slot: AnyStr) -> bool:
        method = f"/my/{self.character.name}/action/equip"

        response_code, response_data = self.post(
            method=method,
            body={
                "slot": slot,
                "code": code
            }
        )

        return response_code == 200

    def deposit(self, code: AnyStr, quantity: int = 1):
        method = f"/my/{self.character.name}/action/bank/deposit"

        response_code, response_data = self.post(
            method=method,
            body={
                "quantity": quantity,
                "code": code
            }
        )
        self._update_character()

    def deposit_all(self):
        method = f"/my/{self.character.name}/action/bank/deposit"

        for item in self.character.inventory:
            if item.quantity > 0:
                response_code, response_data = self.post(
                    method=method,
                    body={
                        "quantity": item.quantity,
                        "code": item.code
                    }
                )
        self._update_character()

    def withdraw(self, code: AnyStr, quantity: int = 1):
        method = f"/my/{self.character.name}/action/bank/withdraw"

        response_code, response_data = self.post(
            method=method,
            body={
                "quantity": quantity,
                "code": code
            }
        )
        self._update_character()

    def _update_character(self) -> None:
        method = f"/characters/{self.character.name}"
        code, response = self.get(method=method)

        self.character = Character.from_dict(response["data"])
