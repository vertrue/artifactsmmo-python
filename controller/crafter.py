from api.character import MyCharacterAPI
from api.bank import BankAPI

from models.monster import AllMonsters
from models.map import AllMaps
from models.item import AllItems, Item
from models.resource import AllResources

from controller.attacker import Attacker

from typing import AnyStr, Dict

from time import sleep


class Crafter:
    def __init__(
        self,
        character: MyCharacterAPI,
        monsters: AllMonsters,
        maps: AllMaps,
        items: AllItems,
        resources: AllResources,
        bank: BankAPI,
        craft_skill: AnyStr,
        attacker: Attacker,
    ) -> None:
        self.character = character
        self.monsters = monsters
        self.maps = maps
        self.items = items
        self.resources = resources

        self.craft_skill = craft_skill

        self.bank = bank
        self.bank_map = self.bank.get_map(
            character=self.character.character, maps=self.maps
        )

        self.attacker = attacker

        self.action = None
        self.wait_for_attacker = False

        self.attacker_mode = Attacker(
            character=self.character,
            monsters=self.monsters,
            maps=self.maps,
            items=self.items,
            is_crafter=True
        )

    def pre_run(self):
        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def reset(self):
        self.action = None
        self.wait_for_attacker = False

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
        if self.wait_for_attacker:
            return self.attacker_mode.pick_action()

        item_for_attacker = self.character.character.find_unique_craft(
            skill=self.craft_skill,
            attacker=self.attacker.character.character,
            items=self.items,
            bank=self.bank,
            monsters=self.monsters,
        )
        if item_for_attacker:
            calculate_mobs_resource = self._calculate_craft(item=item_for_attacker)
            if calculate_mobs_resource:
                if self.wait_for_attacker:
                    return self.attacker_mode.pick_action()
                for item_code, quantity in calculate_mobs_resource.items():
                    added = self.attacker_mode.add_farm_resource(
                        code=item_code, quantity=quantity, source=self
                    )
                    if added:
                        print(
                            f"{self.character.character.name} is collecting {item_code} for {item_for_attacker.name}..."
                        )
                        self.bank.add_reserve(
                            item_code=item_code,
                            quantity=quantity,
                            reverved_by=self.character.character.name,
                        )
                        self.wait_for_attacker = True
                        return self.attacker_mode.pick_action()
                print(f"{self.character.character.name} does not have level for collecting {item_code} for {item_for_attacker.name}...")
                return self.attacker_mode.pick_action()
            else:
                self.wait_for_attacker = False
                return self.craft_for_attacker
        else:
            return self.farm_xp

    def farm_xp(self):
        print(f"{self.character.character.name} is farming xp...")
        item = self.character.character.find_best_craft_with_attacker(
            skill=self.craft_skill,
            attacker=self.attacker_mode.character.character,
            items=self.items,
            monsters=self.monsters,
            bank=self.bank
        )
        if (
            self.bank.get_quantity(
                item_code=item.code, character_name=self.character.character.name
            )
            > 1
        ):
            print(f"{self.character.character.name} is recycling {item.name}...")
            self.character.move(target=self.bank_map)
            self.character.withdraw(code=item.code)
            map = self.maps.closest(
                character=self.character.character,
                content_code=item.craft.skill,
                content_type="workshop",
            )
            self.character.move(target=map)
            self.character.recycle(code=item.code)
        self._craft(item=item)

        self.character.move(target=self.bank_map)
        self.character.deposit_all()

    def craft_for_attacker(self):
        print(
            f"{self.character.character.name} is crafting for attackers..."
        )
        item_for_attacker = self.character.character.find_unique_craft(
            skill=self.craft_skill,
            attacker=self.attacker.character.character,
            items=self.items,
            bank=self.bank,
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

        character_quantity = self.character.character.get_resource_quantity(
            code=item.code
        )

        if quantity <= character_quantity:
            return

        if item.subtype != "mob":
            # TODO: crafter leveling
            tool = self.bank.get_tool(skill=item.subtype, items=self.items)
            if tool:
                if self.character.character.level >= tool.level:
                    current_item = self.character.character.get_slot_item(slot=tool.type, items=self.items)
                    if current_item is None:
                        self.character.move(target=self.bank_map)
                        self.character.withdraw(code=tool.code)
                        self.character.equip(code=tool.code, slot=tool.type)
                    elif current_item.get_effect_value(effect_name=item.subtype) > tool.get_effect_value(effect_name=item.subtype):
                        self.character.move(target=self.bank_map)
                        self.character.unequip(slot=tool.type)
                        self.character.withdraw(code=tool.code)
                        self.character.equip(code=tool.code, slot=tool.type)
                        self.character.deposit(code=current_item.code)

            resource = self.resources.get_drops(drop=item.code)

            map = self.maps.closest(
                character=self.character.character,
                content_code=resource.code,
            )
            while self.character.character.get_resource_quantity(code=item.code) < quantity:
                self.character.move(target=map)
                self.character.gather()
        else:
            while self.character.character.get_resource_quantity(code=item.code) < quantity:
                monster = self.monsters.get_drops(drop=item.code)
                monster_map = self.maps.closest(
                    character=self.character.character,
                    content_code=monster.code
                )

                self.attacker_mode.check_better_equipment(monster=monster)
                self.character.move(target=monster_map)
                self.character.fight()

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

        if quantity == 0:
            return

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
