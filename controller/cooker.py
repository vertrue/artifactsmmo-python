from api.character import MyCharacterAPI
from api.bank import BankAPI

from models.monster import AllMonsters
from models.map import AllMaps
from models.item import AllItems, Item
from models.resource import AllResources

from controller.attacker import Attacker

from typing import AnyStr, Dict


class Cooker:
    def __init__(
        self,
        character: MyCharacterAPI,
        monsters: AllMonsters,
        maps: AllMaps,
        items: AllItems,
        resources: AllResources,
        craft_skill: AnyStr,
        attacker: Attacker,
    ) -> None:
        self.character = character
        self.monsters = monsters
        self.maps = maps
        self.items = items
        self.resources = resources

        self.craft_skill = craft_skill

        self.bank = BankAPI()
        self.bank_map = self.bank.get_map(
            character=self.character.character, maps=self.maps
        )

        self.attacker = attacker

        self.action = None

        self.farm_xp_iter = 0

        self.character.deposit_all()

    def run(self):
        self.action = self.pick_action()
        if self.action:
            self.action()

    def pick_action(self):
        return self.farm_xp

    def farm_xp(self):
        print(f"{self.character.character.name} is farming xp...")
        item = self.character.character.find_best_craft(
            skill=self.craft_skill, items=self.items, bank=self.bank
        )
        self._craft(item=item)

        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def craft_for_attacker(self):
        print(
            f"{self.character.character.name} is crafting for {self.attacker.character.character.name}..."
        )
        item_for_attacker = self.character.character.find_unique_craft(
            skill=self.craft_skill,
            attacker=self.attacker.character.character,
            items=self.items,
            bank=self.bank,
            monsters=self.monsters,
        )
        if item_for_attacker is None:
            item_for_attacker = self.character.character.find_best_craft_for_attacker(
                skill=self.craft_skill,
                attacker=self.attacker.character.character,
                items=self.items,
                monsters=self.monsters,
            )
        self._craft(item=item_for_attacker)

        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def _collect(self, item: Item, quantity: int):
        character_quantity = self.character.character.get_resource_quantity(
            code=item.code
        )
        bank_quantity = self.bank.get_quantity(
            item_code=item.code, character_name=self.character.character.name
        )

        if quantity <= character_quantity:
            return

        if bank_quantity > 0:
            self.character.move(target=self.bank_map)
            self.character.withdraw(
                code=item.code, quantity=min(quantity, bank_quantity)
            )
            self.bank.delete_reserve(
                item_code=item.code,
                quantity=quantity,
                reverved_by=self.character.character.name,
            )
            quantity -= min(quantity, bank_quantity)

        character_quantity = self.character.character.get_resource_quantity(
            code=item.code
        )

        if quantity <= character_quantity:
            return
        left = quantity - character_quantity

        if left <= 0:
            return

        resource = self.resources.get_drops(drop=item.code)

        map = self.maps.closest(
            character=self.character.character,
            content_code=resource.code,
        )
        self.character.move(target=map)
        for _ in range(left):
            self.character.gather()

    def _craft(self, item: Item, quantity: int = 1, root: bool = True):
        if not root:
            character_quantity = self.character.character.get_resource_quantity(
                code=item.code
            )
            quantity -= character_quantity
            if quantity > 0:
                bank_quantity = self.bank.get_quantity(
                    item_code=item.code, character_name=self.character.character.name
                )
                if bank_quantity > 0:
                    self.character.move(target=self.bank_map)
                    self.character.withdraw(
                        code=item.code, quantity=min(quantity, bank_quantity)
                    )
                    quantity -= min(quantity, bank_quantity)

        print(f"{self.character.character.name} is crafting {item.code}...")
        for part in item.craft.items:
            item_quantity = part.quantity
            item_code = part.code

            craft_item = self.items.get_one(code=item_code)

            if craft_item.craft is None:
                self._collect(craft_item, item_quantity * quantity)
            else:
                self._craft(item=craft_item, quantity=item_quantity, root=False)

        map = self.maps.closest(
            character=self.character.character,
            content_code=item.craft.skill,
        )
        for _ in range(quantity):
            self.character.move(target=map)
            self.character.craft(code=item.code)
            print(f"{self.character.character.name} has crafted {item_code}...")

    def _calculate_collect(self, item: Item, quantity: int) -> int:
        character_quantity = self.character.character.get_resource_quantity(
            code=item.code
        )
        bank_quantity = self.bank.get_quantity(
            item_code=item.code, character_name=self.character.character.name
        )

        if quantity <= character_quantity:
            return 0

        quantity -= bank_quantity

        if quantity <= character_quantity:
            return 0
        left = quantity - character_quantity

        return left

    def _calculate_craft(
        self, item: Item, quantity: int = 1, root: bool = True
    ) -> Dict:
        absent = {}

        if not root:
            character_quantity = self.character.character.get_resource_quantity(
                code=item.code
            )
            quantity -= character_quantity
            if quantity > 0:
                bank_quantity = self.bank.get_quantity(
                    item_code=item.code, character_name=self.character.character.name
                )
                if bank_quantity > 0:
                    quantity -= min(quantity, bank_quantity)

        for part in item.craft.items:
            item_quantity = part.quantity
            item_code = part.code

            craft_item = self.items.get_one(code=item_code)

            if craft_item.craft is None:
                if craft_item.subtype == "mob":
                    left = self._calculate_collect(craft_item, item_quantity)
                    if left > 0:
                        absent[craft_item.code] = left * quantity
            else:
                child_absent = self._calculate_craft(
                    item=craft_item, quantity=item_quantity, root=False
                )
                for key, value in child_absent.items():
                    try:
                        if value > 0:
                            absent[key] += value * quantity
                    except KeyError:
                        absent[key] = value * quantity

        return absent
