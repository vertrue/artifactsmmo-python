from api.character import MyCharacterAPI
from api.bank import BankAPI

from models.monster import AllMonsters
from models.map import AllMaps
from models.item import AllItems

from typing import AnyStr, List


class MonsterResource:
    def __init__(self, code: AnyStr, quantity: int, monsters: AllMonsters) -> None:
        self.resource = code
        self.monster = monsters.get_drops(drop=code)
        self.quantity = quantity


class FarmResources:
    def __init__(self, monsters: AllMonsters) -> None:
        self.resources: List[MonsterResource] = []
        self.monsters = monsters

    def add(self, code: AnyStr, quantity: int) -> None:
        self.resources.append(
            MonsterResource(code=code, quantity=quantity, monsters=self.monsters)
        )

    def get(self) -> MonsterResource | None:
        try:
            return self.resources[0]
        except IndexError:
            return None

    def farmed(self, quantity: int = 1) -> None:
        self.resources[0].quantity -= quantity
        if self.resources[0].quantity <= 0:
            del self.resources[0]
            return True
        return False


class Attacker:
    def __init__(
        self,
        character: MyCharacterAPI,
        monsters: AllMonsters,
        maps: AllMaps,
        items: AllItems,
    ) -> None:
        self.character = character
        self.monsters = monsters
        self.maps = maps
        self.items = items

        self.bank = BankAPI()
        self.bank_map = self.bank.get_map(
            character=self.character.character, maps=self.maps
        )

        self.farm_queue = FarmResources(monsters=self.monsters)

        self.action = None

        self.farm_xp_iter = 0

        self.character.deposit_all()

    def run(self):
        self.action = self.pick_action()
        if self.action:
            self.action()

    def pick_action(self):
        if self.has_farm_resources:
            return self.farm_resource
        else:
            return self.farm_xp

    def add_farm_resource(self, code: AnyStr, quantity: int):
        current_quantity = self.character.character.get_resource_quantity(code=code)
        monster = self.monsters.get_drops(drop=code)
        if not self.character.character.can_beat(monster):
            return False

        if current_quantity >= quantity:
            self.character.move(target=self.bank_map)
            self.character.deposit_all()
        else:
            diff_quantity = quantity - current_quantity
            self.farm_queue.add(code=code, quantity=diff_quantity)
        return True

    def farm_resource(self):
        resource = self.farm_queue.get()
        print(f"{self.character.character.name} is farming {resource.resource}... {resource.quantity} {resource.resource} left")
        resource_q_before = self.character.character.get_resource_quantity(
            code=resource.resource
        )

        closest_monster = self.maps.closest(
            character=self.character.character, content_code=resource.monster.code
        )

        self.character.move(target=closest_monster)
        self.character.fight()

        resource_q_after = self.character.character.get_resource_quantity(
            code=resource.resource
        )

        if resource_q_before != resource_q_after:
            resource_diff = resource_q_after - resource_q_before
            result = self.farm_queue.farmed(quantity=resource_diff)
            if result:
                self.character.move(target=self.bank_map)
                self.character.deposit_all()

    def farm_xp(self):
        print(
            f"{self.character.character.name} is farming xp {self.farm_xp_iter} times..."
        )
        if self.farm_xp_iter % 10 == 0:
            self.check_better_equipment()
            self.character.move(target=self.bank_map)
            self.character.deposit_all()
        best_monster = self.character.character.find_best_monster(
            monsters=self.monsters
        )
        closest_monster = self.maps.closest(
            character=self.character.character, content_code=best_monster.code
        )

        self.character.move(target=closest_monster)
        self.character.fight()

        self.farm_xp_iter += 1

    def check_better_equipment(self):
        print(f"{self.character.character.name} is checking for better equipment...")
        bank_items = self.bank.get_all_items().items

        for item in bank_items:
            bank_item = self.items.get_one(code=item.code)
            character_item = self.character.character.get_slot_item(
                slot=bank_item.type, items=self.items
            )

            if self.character.character.get_slot(slot=bank_item.type) is None:
                continue

            if character_item is None:
                self.character.move(target=self.bank_map)
                self.character.withdraw(code=bank_item.code)
                self.character.equip(code=bank_item.code, slot=bank_item.type)
            elif bank_item.level > character_item.level:
                if bank_item.level > self.character.character.level:
                    continue
                self.character.move(target=self.bank_map)
                self.character.withdraw(code=bank_item.code)
                self.character.unequip(slot=bank_item.type)
                self.character.equip(code=bank_item.code, slot=bank_item.type)

    @property
    def has_farm_resources(self):
        return len(self.farm_queue.resources) > 0
