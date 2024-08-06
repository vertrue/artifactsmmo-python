from api.character import MyCharacterAPI
from api.bank import BankAPI

from models.monster import AllMonsters
from models.map import AllMaps
from models.item import AllItems, Item
from models.resource import AllResources

from controller.attacker import Attacker

from typing import AnyStr, Dict

from time import sleep


class Cooker:
    def __init__(
        self,
        character: MyCharacterAPI,
        monsters: AllMonsters,
        maps: AllMaps,
        items: AllItems,
        resources: AllResources,
        craft_skill: AnyStr,
        secondary_skill: AnyStr,
        attacker: Attacker,
    ) -> None:
        self.character = character
        self.monsters = monsters
        self.maps = maps
        self.items = items
        self.resources = resources

        self.craft_skill = craft_skill
        self.secondary_skill = secondary_skill

        self.bank = BankAPI()
        self.bank_map = self.bank.get_map(
            character=self.character.character, maps=self.maps
        )

        self.attacker = attacker

        self.action = None

    def pre_run(self):
        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def reset(self):
        self.action = None

    def run(self):
        self.action = self.pick_action()
        if self.action:
            try:
                self.action()
            except Exception as e:
                print(e)
                sleep(60)
                self.reset()

    def pick_action(self):
        item_to_sell = self.find_sell()
        if item_to_sell:
            return self.sell
        else:
            return self.farm_xp

    def farm_xp(self):
        print(f"{self.character.character.name} is farming xp...")
        print(f"{self.character.character.name} is chopping woods...")
        secondary_items = self.character.character.find_all_crafts(
            skill=self.secondary_skill,
            items=self.items,
            bank=self.bank
        )
        for item in secondary_items:
            self._craft(item=item, quantity=3)
            self.character.move(target=self.bank_map)
            self.character.deposit_all()

        item = self.character.character.find_best_craft(
            skill=self.craft_skill, items=self.items, bank=self.bank
        )
        self._craft(item=item)

        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def sell(self):
        item = self.find_sell()
        print(f"{self.character.character.name} is selling")
        if item.code == "tasks_coin":
            self.exchange_task_coin()
            return
        quantity = (
            self.bank.get_quantity(
                item_code=item.code, character_name=self.character.character.name
            )
            - 2
        )
        quantity = min(50, quantity, self.character.character.inventory_max_items)

        self.character.move(target=self.bank_map)
        self.character.deposit_all()
        self.character.withdraw(
            code=item.code,
            quantity=min(quantity, self.character.character.inventory_max_items),
        )

        price = self.bank.get_ge_sell_price(item=item)

        print(
            f"{self.character.character.name} is selling {quantity} {item.name} \
for {price * quantity} gold ({price} for 1)..."
        )

        ge_map = self.maps.closest(
            character=self.character.character,
            content_type="grand_exchange",
        )
        self.character.move(target=ge_map)
        self.character.sell(code=item.code, quantity=quantity, price=price)

    def exchange_task_coin(self):
        item = self.find_sell()
        print(f"{self.character.character.name} is exchanging {item.name}")
        quantity = (
            self.bank.get_quantity(
                item_code=item.code, character_name=self.character.character.name
            ) // 3 * 3
        )
        quantity = min(50, quantity, self.character.character.inventory_max_items)
        self.character.move(target=self.bank_map)
        self.character.deposit_all()
        self.character.withdraw(
            code=item.code,
            quantity=min(quantity, self.character.character.inventory_max_items),
        )

        task_map = self.maps.closest(
            character=self.character.character, content_type="tasks_master"
        )
        self.character.move(target=task_map)
        while quantity > 0:
            self.character.exchange_task()
            quantity -= 3

    def find_sell(self) -> Item | None:
        bank_items = self.bank.get_all_items()

        for bank_item in bank_items.items:
            item = self.items.get_one(code=bank_item.code)
            if item.code == "tasks_coin" and bank_item.quantity >= 3:
                return item

            if bank_item.quantity > 2:
                if item.type not in ["resource", "currency", "tool"]:
                    return item

        return None

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

        character_quantity = self.character.character.get_resource_quantity(
            code=item.code
        )

        if quantity <= character_quantity:
            return

        resource = self.resources.get_drops(drop=item.code)

        map = self.maps.closest(
            character=self.character.character,
            content_code=resource.code,
        )
        while self.character.character.get_resource_quantity(code=item.code) < quantity:
            self.character.move(target=map)
            self.character.gather()

    def _craft(self, item: Item, quantity: int = 1, root: bool = True):
        original_quantity = quantity
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
            content_type="workshop",
        )

        while (
            self.character.character.get_resource_quantity(code=item.code)
            < original_quantity
        ):
            self.character.move(target=map)
            crafted = self.character.craft(code=item.code)
            if crafted:
                print(f"{self.character.character.name} has crafted {item.code}...")
            else:
                break

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
