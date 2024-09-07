from api.character import MyCharacterAPI
from api.bank import BankAPI
from api.map import MapAPI

from models.monster import AllMonsters, Monster
from models.map import AllMaps
from models.item import AllItems

from typing import AnyStr, List

from time import sleep
import traceback


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
        is_crafter: bool = False,
    ) -> None:
        self.character = character
        self.monsters = monsters
        self.maps = maps
        self.items = items

        self.bank = BankAPI()
        self.bank_map = self.bank.get_map(
            character=self.character.character, maps=self.maps
        )

        self.map = MapAPI()

        self.farm_queue: FarmResources = FarmResources(monsters=self.monsters)

        self.is_crafter = is_crafter

        self.action = None
        self.iter = 0

        self.final_boss = self.monsters.get(code="lich")

        self.cooker = None

    def _set_cooker(self, cooker):
        self.cooker = cooker

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
                print(traceback.format_exc())
                sleep(60)
                self.reset()

    def pick_action(self, crafter_max_level=False):
        if self.iter % 30 == 0:
            self.character.move(target=self.bank_map)
            self.character.deposit_all()

        if self.cooker and self.character.character.level == 35:
            if self.can_beat_final_boss:
                return self.kill_final_boss
            #if not self.cooker.cooking:
                #return self.kill_final_boss

        if self.map.has_events:
            event = self.character.character.find_best_event(
                map=self.map, monsters=self.monsters, items=self.items, bank=self.bank
            )

            if event:
                return self.do_event

        if not self.has_task and (not self.is_crafter or crafter_max_level):
            return self.accept_task

        if self.has_farm_resources:
            return self.farm_resource
        elif not self.is_crafter or crafter_max_level:
            best_monster = self.character.character.find_best_monster(
                monsters=self.monsters, items=self.items, maps=self.maps, bank=self.bank
            )
            if self.can_complete_task and self.has_task:
                return self.do_task
            elif self.character.character.level != 35 and (self.character.character.level - best_monster.level) < 11:
                return self.farm_xp
            elif self.character.character.level == 35:
                return self.change_task
            else:
                return self.kill_all
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

        can_beat, _ = self.character.character.find_optimal_build(
            monster=monster, items=self.items, bank=self.bank
        )
        if not can_beat:
            return False

        diff_quantity = quantity - current_quantity
        self.farm_queue.add(code=code, quantity=diff_quantity, source=source)
        print(f"{self.character.character.name} is farming {monster.name}")
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

        self.iter += 1

    def farm_xp(self):
        print(f"{self.character.character.name} is farming xp {self.iter} times...")
        best_monster = self.character.character.find_best_monster(
            monsters=self.monsters, items=self.items, maps=self.maps, bank=self.bank
        )
        self.check_better_equipment(monster=best_monster)
        closest_monster = self.maps.closest(
            character=self.character.character, content_code=best_monster.code
        )

        self.character.move(target=closest_monster)
        self.character.fight()

        self.iter += 1

    def kill_all(self):
        filtered_monsters = self.monsters.filter()

        targets: List[Monster] = []

        for monster in filtered_monsters:
            can_beat, _ = self.character.character.find_optimal_build(
                monster=monster, items=self.items, bank=self.bank
            )
            if can_beat:
                targets += [monster]

        for monster in targets:
            self.check_better_equipment(monster=monster)
            for _ in range(20):
                print(f"{self.character.character.name} is killing {monster.code}...")
                closest_monster = self.maps.closest(
                    character=self.character.character, content_code=monster.code
                )

                self.character.move(target=closest_monster)
                self.character.fight()

            self.character.move(target=self.bank_map)
            self.character.deposit_all()

    def kill_final_boss(self):
        monster = self.final_boss
        self.check_better_equipment(monster=monster, final_boss=True)
        print(f"{self.character.character.name} is killing {monster.code}...")
        closest_monster = self.maps.closest(
            character=self.character.character, content_code=monster.code
        )

        self.character.move(target=closest_monster)
        self.character.fight()

        self.iter += 1

    def check_better_equipment(self, monster: Monster, final_boss: bool = False):
        print(f"{self.character.character.name} is checking for better equipment...")
        _, picked_items = self.character.character.find_optimal_build(
            monster=monster, items=self.items, bank=self.bank, final_boss=final_boss
        )

        for slot, item in picked_items.items():
            if slot == "rounds":
                continue
            quantity = 1
            if "consumable" in slot:
                quantity = self.bank.get_quantity(item_code=item.code, character_name=self.character.character.name)

            character_item = self.character.character.get_slot_item(
                slot=slot, items=self.items
            )
            if character_item is None and item is not None:
                print(f"{self.character.character.name} is equiping {item.code}...")
                self.character.move(target=self.bank_map)
                self.character.withdraw(code=item.code, quantity=quantity)
                self.character.equip(code=item.code, slot=slot)

            if character_item is not None and item is not None:
                if character_item == item and item.type != "consumable":
                    continue
                print(f"{self.character.character.name} is equiping {item.code}...")
                self.character.move(target=self.bank_map)
                self.character.withdraw(code=item.code, quantity=quantity)
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
            f"{self.character.character.name} is doing task \
{self.character.character.task_progress}/{self.character.character.task_total} {self.character.character.task}..."
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

        self.iter += 1

    def complete_task(self):
        print(f"{self.character.character.name} has completed task...")
        task_map = self.maps.closest(
            character=self.character.character, content_type="tasks_master"
        )
        self.character.move(target=task_map)
        self.character.complete_task()
        self.character.accept_task()
        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def change_task(self):
        print(f"{self.character.character.name} need to change task...")
        task_map = self.maps.closest(
            character=self.character.character, content_type="tasks_master"
        )
        self.character.move(target=self.bank_map)
        self.character.withdraw(code="tasks_coin")
        self.character.move(target=task_map)
        self.character.cancel_task()
        self.character.accept_task()
        self.character.move(target=self.bank_map)
        self.character.deposit_all()

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

    @property
    def can_beat_final_boss(self):
        can_beat, _ = self.character.character.find_optimal_build(
            monster=self.final_boss,
            items=self.items,
            bank=self.bank,
            final_boss=True
        )
        print(f"{self.character.character.name} can beat {self.final_boss.name} = {can_beat}")
        if not can_beat and not self.cooker.cooking:
            print(f"{self.character.character.name} commanding {self.cooker.character.character.name} to make food...")
            self.cooker.cooking = True
            self.cooker.cooking_quantity = 10
        return can_beat

    def do_event(self):
        print(f"{self.character.character.name} is fighting event...")
        event = self.character.character.find_best_event(
            map=self.map, monsters=self.monsters, items=self.items, bank=self.bank
        )
        monster = self.monsters.get(code=event.content.code)

        self.check_better_equipment(monster=monster)

        self.character.move(target=event)
        self.character.fight()

        self.iter += 1
