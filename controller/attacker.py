from api.character import MyCharacterAPI
from api.bank import BankAPI

from models.monster import AllMonsters, Monster
from models.map import AllMaps
from models.item import AllItems

from typing import AnyStr


class MonsterResource:
    def __init__(self, code: AnyStr, quantity: int, monsters: AllMonsters) -> None:
        self.resource = code
        self.monster: Monster = monsters.get_drops(drop=code)
        self.quantity = quantity


class FarmResources:
    def __init__(self, monsters: AllMonsters) -> None:
        self.resources: MonsterResource = None
        self.monsters = monsters
        self.source = None

    def add(self, code: AnyStr, quantity: int, source) -> None:
        self.resources = MonsterResource(
            code=code, quantity=quantity, monsters=self.monsters
        )
        self.source = source

    def get(self) -> MonsterResource | None:
        return self.resources

    def farmed(self, quantity: int = 1) -> None:
        self.resources.quantity -= quantity
        if self.resources.quantity <= 0:
            self.resources = None
            self.source.wait_for_attacker = False
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

        self.farm_queue: FarmResources = FarmResources(monsters=self.monsters)

        self.action = None

        self.farm_xp_iter = 0

    def pre_run(self):
        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def run(self):
        self.action = self.pick_action()
        if self.action:
            self.action()

    def pick_action(self):
        if not self.has_task:
            self.accept_task()

        if self.has_farm_resources:
            return self.farm_resource
        elif self.can_complete_task and self.has_task:
            return self.do_task
        else:
            return self.farm_xp

    def add_farm_resource(self, code: AnyStr, quantity: int, source):
        current_quantity = self.character.character.get_resource_quantity(code=code)
        if current_quantity >= quantity:
            self.character.move(target=self.bank_map)
            self.character.deposit_all()

        monster = self.monsters.get_drops(drop=code)
        if self.farm_queue.get():
            print(
                f"{self.character.character.name} is farming {self.farm_queue.get().resource} and cannot add new queue"
            )
            return False
        if not self.character.character.can_beat(monster):
            return False

        diff_quantity = quantity - current_quantity
        self.farm_queue.add(code=code, quantity=diff_quantity, source=source)
        print(f"{self.character.character.name} is now farming {monster.name}")
        return True

    def farm_resource(self):
        resource = self.farm_queue.get()
        print(
            f"{self.character.character.name} is farming {resource.resource}... {resource.quantity} {resource.resource} left"
        )
        self.check_better_equipment(monster=resource.monster)

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
            self.character.move(target=self.bank_map)
            self.character.deposit_all()
        best_monster = self.character.character.find_best_monster(
            monsters=self.monsters
        )
        self.check_better_equipment(monster=best_monster)
        closest_monster = self.maps.closest(
            character=self.character.character, content_code=best_monster.code
        )

        self.character.move(target=closest_monster)
        self.character.fight()

        self.farm_xp_iter += 1

    def check_better_equipment(self, monster: Monster):
        print(f"{self.character.character.name} is checking for better equipment...")
        _, picked_items = self.character.character.find_optimal_build(
            monster=monster, items=self.items, bank=self.bank
        )

        for slot, item in picked_items.items():
            character_item = self.character.character.get_slot_item(
                slot=slot, items=self.items
            )
            if character_item is None and item is not None:
                print(f"{self.character.character.name} is equiping {item.code}...")
                self.character.move(target=self.bank_map)
                self.character.withdraw(code=item.code)
                self.character.equip(code=item.code, slot=slot)

            if character_item is not None and item is not None:
                if character_item == item:
                    continue
                print(f"{self.character.character.name} is equiping {item.code}...")
                self.character.move(target=self.bank_map)
                self.character.withdraw(code=item.code)
                self.character.unequip(slot=slot)
                self.character.equip(code=item.code, slot=slot)
                self.character.deposit(code=character_item.code)

    def accept_task(self):
        print(f"{self.character.character.name} is accepting new task...")
        task_map = self.maps.closest(
            character=self.character.character, content_type="tasks_master"
        )
        self.character.move(target=task_map)
        self.character.accept_task()

    def do_task(self):
        print(
            f"{self.character.character.name} is doing task {self.character.character.task_progress}/{self.character.character.task_total} {self.character.character.task}..."
        )
        if (
            self.character.character.task_progress
            == self.character.character.task_total
        ):
            self.complete_task()
        monster = self.monsters.get(code=self.character.character.task)
        self.check_better_equipment(monster=monster)
        monster_map = self.maps.closest(
            character=self.character.character,
            content_code=self.character.character.task,
        )
        self.character.move(target=monster_map)
        self.character.fight()

    def complete_task(self):
        print(f"{self.character.character.name} completed task...")
        task_map = self.maps.closest(
            character=self.character.character, content_type="tasks_master"
        )
        self.character.move(target=task_map)
        self.character.complete_task()
        self.character.accept_task()

    @property
    def has_farm_resources(self):
        return self.farm_queue.resources is not None

    @property
    def has_task(self):
        return self.character.character.task != ""

    @property
    def can_complete_task(self):
        can_beat, _ = self.character.character.find_optimal_build(
            monster=self.monsters.get(self.character.character.task),
            items=self.items,
            bank=self.bank,
        )

        return can_beat
