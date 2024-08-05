from api.map import MapAPI

from models.character import Character

from models.map import Map

from typing import AnyStr


class MyCharacterAPI(MapAPI):
    def __init__(self, character: Character) -> None:
        super().__init__()
        self.character = character

    def move(self, target: Map) -> None:
        if (self.character.x, self.character.y) == (target.x, target.y):
            return

        method = f"/my/{self.character.name}/action/move"
        self.post(method=method, body={"x": target.x, "y": target.y})

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

        response_code, response_data = self.post(method=method, body={"code": code})

        self._update_character()

        return response_code == 200

    def unequip(self, slot: AnyStr) -> bool:
        method = f"/my/{self.character.name}/action/unequip"

        response_code, response_data = self.post(method=method, body={"slot": slot})

        self._update_character()

        return response_code == 200

    def equip(self, code: AnyStr, slot: AnyStr) -> bool:
        method = f"/my/{self.character.name}/action/equip"

        response_code, response_data = self.post(
            method=method, body={"slot": slot, "code": code}
        )

        self._update_character()

        return response_code == 200

    def deposit(self, code: AnyStr, quantity: int = 1):
        method = f"/my/{self.character.name}/action/bank/deposit"

        response_code, response_data = self.post(
            method=method, body={"quantity": quantity, "code": code}
        )

        self._update_character()

    def deposit_all(self):
        method = f"/my/{self.character.name}/action/bank/deposit"

        for item in self.character.inventory:
            if item.quantity > 0:
                response_code, response_data = self.post(
                    method=method, body={"quantity": item.quantity, "code": item.code}
                )

        self._update_character()

        gold_quantity = self.character.gold
        method = f"/my/{self.character.name}/action/bank/deposit/gold"
        response_code, response_data = self.post(
            method=method, body={"quantity": gold_quantity}
        )

        self._update_character()

    def withdraw(self, code: AnyStr, quantity: int = 1):
        method = f"/my/{self.character.name}/action/bank/withdraw"

        response_code, response_data = self.post(
            method=method, body={"quantity": quantity, "code": code}
        )

        self._update_character()

    def accept_task(self):
        method = f"/my/{self.character.name}/action/task/new"

        response_code, response_data = self.post(method=method)

        self._update_character()

    def complete_task(self):
        method = f"/my/{self.character.name}/action/task/complete"

        response_code, response_data = self.post(method=method)

        self._update_character()

    def sell(self, code: AnyStr, quantity: int, price: int):
        method = f"/my/{self.character.name}/action/ge/sell"

        response_code, response_data = self.post(
            method=method, body={"quantity": quantity, "code": code, "price": price}
        )

        self._update_character()

    def recycle(self, code: AnyStr, quantity: int = 1):
        method = f"/my/{self.character.name}/action/recycling"

        response_code, response_data = self.post(
            method=method, body={"quantity": quantity, "code": code}
        )

        self._update_character()

    def _update_character(self) -> None:
        method = f"/characters/{self.character.name}"
        code, response = self.get(method=method)

        self.character = Character.from_dict(response["data"])
