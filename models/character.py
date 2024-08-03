from dataclasses import dataclass, field
from typing import List, Dict, Optional, AnyStr

from models.monster import Monster, AllMonsters
from models.item import Item, AllItems


@dataclass
class InventoryItem:
    slot: int
    code: str
    quantity: int


@dataclass
class Character:
    name: str
    skin: str
    level: int
    xp: int
    max_xp: int
    total_xp: int
    gold: int
    speed: int
    mining_level: int
    mining_xp: int
    mining_max_xp: int
    woodcutting_level: int
    woodcutting_xp: int
    woodcutting_max_xp: int
    fishing_level: int
    fishing_xp: int
    fishing_max_xp: int
    weaponcrafting_level: int
    weaponcrafting_xp: int
    weaponcrafting_max_xp: int
    gearcrafting_level: int
    gearcrafting_xp: int
    gearcrafting_max_xp: int
    jewelrycrafting_level: int
    jewelrycrafting_xp: int
    jewelrycrafting_max_xp: int
    cooking_level: int
    cooking_xp: int
    cooking_max_xp: int
    hp: int
    haste: int
    critical_strike: int
    stamina: int
    attack_fire: int
    attack_earth: int
    attack_water: int
    attack_air: int
    dmg_fire: int
    dmg_earth: int
    dmg_water: int
    dmg_air: int
    res_fire: int
    res_earth: int
    res_water: int
    res_air: int
    x: int
    y: int
    cooldown: int
    cooldown_expiration: str
    weapon_slot: str
    shield_slot: str
    helmet_slot: str
    body_armor_slot: str
    leg_armor_slot: str
    boots_slot: str
    ring1_slot: str
    ring2_slot: str
    amulet_slot: str
    artifact1_slot: str
    artifact2_slot: str
    artifact3_slot: str
    consumable1_slot: str
    consumable1_slot_quantity: int
    consumable2_slot: str
    consumable2_slot_quantity: int
    task: str
    task_type: str
    task_progress: int
    task_total: int
    inventory_max_items: int
    account: Optional[str] = None
    inventory: List[InventoryItem] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict) -> "Character":
        inventory_items = [InventoryItem(**item) for item in data.get("inventory", [])]

        character_data = {
            key: value
            for key, value in data.items()
            if key != "inventory" and key.find("inventory_slot") == -1
        }

        character = Character(**character_data)
        character.inventory = inventory_items

        return character

    def get_slot(self, slot: AnyStr) -> AnyStr | None:
        try:
            return eval(f"self.{slot}_slot")
        except AttributeError:
            return None

    def get_slot_item(self, slot: AnyStr, items: AllItems) -> Item | None:
        try:
            item_code = eval(f"self.{slot}_slot")
            item = items.get_one(item_code)
            return item
        except AttributeError:
            try:
                item_code = eval(f"self.{slot}1_slot")
                item = items.get_one(item_code)
                return item
            except AttributeError:
                try:
                    item_code = eval(f"self.{slot}2_slot")
                    item = items.get_one(item_code)
                    return item
                except AttributeError:
                    try:
                        item_code = eval(f"self.{slot}3_slot")
                        item = items.get_one(item_code)
                        return item
                    except AttributeError:
                        return None

    def get_resource_quantity(self, code: AnyStr):
        for item in self.inventory:
            if item.code == code:
                return item.quantity
        return 0

    def get_skill_level(self, skill: AnyStr):
        try:
            skill_level = eval(f"self.{skill}_level")
            return skill_level
        except AttributeError:
            return 0

    def find_best_monster(self, monsters: AllMonsters):
        filtered_monsters = monsters.filter()

        for monster in filtered_monsters:
            if self.can_beat(monster=monster):
                target_monster = monster
                break

        for monster in filtered_monsters:
            if self.can_beat(monster=monster) and monster.level > target_monster.level:
                target_monster = monster

        return target_monster

    def find_unique_craft(
        self,
        skill: AnyStr,
        attacker: "Character",
        items: AllItems,
        bank,
        monsters: AllMonsters,
    ):
        filtered_items = items.filter(craft_skill=skill)

        for item in filtered_items:
            if self.can_craft(
                code=item.code, attacker=attacker, items=items, monsters=monsters
            ):
                if not bank.has_item(item=item):
                    if attacker.get_slot_item(slot=item.type, items=items) != item:
                        return item

        return None

    def find_best_craft(self, skill: AnyStr, items: AllItems, bank):
        filtered_items = items.filter(craft_skill=skill)

        for item in filtered_items:
            if self.can_craft_without_attacker(code=item.code, items=items, bank=bank):
                best_item = item
                break

        for item in filtered_items:
            if self.can_craft_without_attacker(code=item.code, items=items, bank=bank):
                if item.level > best_item.level:
                    best_item = item

        return best_item

    def find_best_craft_for_attacker(
        self,
        skill: AnyStr,
        attacker: "Character",
        items: AllItems,
        monsters: AllMonsters,
    ):
        filtered_items = items.filter(craft_skill=skill)

        for item in filtered_items:
            if self.can_craft(
                code=item.code, attacker=attacker, items=items, monsters=monsters
            ):
                if attacker.get_slot_item(slot=item.type, items=items) is None:
                    return item
                if (
                    attacker.get_slot_item(slot=item.type, items=items).level
                    < item.level
                ):
                    return item

    def can_beat(self, monster: Monster):
        players_hp = self.hp
        mobs_hp = monster.hp

        for _ in range(50):
            # player
            player_attack = (
                self.attack_air * (1 + self.dmg_air / 100) * (1 - monster.res_air / 100)
            )
            player_attack += (
                self.attack_earth
                * (1 + self.dmg_earth / 100)
                * (1 - monster.res_earth / 100)
            )
            player_attack += (
                self.attack_fire
                * (1 + self.dmg_fire / 100)
                * (1 - monster.res_fire / 100)
            )
            player_attack += (
                self.attack_water
                * (1 + self.dmg_water / 100)
                * (1 - monster.res_water / 100)
            )

            mobs_hp -= player_attack

            # print(players_hp, mobs_hp)

            if mobs_hp < 0:
                return True

            # mob
            mob_attack = monster.attack_air * (1 - self.res_air / 100)
            mob_attack += monster.attack_earth * (1 - self.attack_earth / 100)
            mob_attack += monster.attack_fire * (1 - self.res_fire / 100)
            mob_attack += monster.attack_water * (1 - self.res_water / 100)

            players_hp -= mob_attack

            # print(players_hp, mobs_hp)

            if players_hp < 0:
                return False

        return False

    def can_farm_resource(self, code: AnyStr, monsters: AllMonsters) -> bool:
        monster = monsters.get_drops(drop=code)
        return self.can_beat(monster)

    def can_craft(
        self,
        code: AnyStr,
        attacker: "Character",
        items: AllItems,
        monsters: AllMonsters,
    ) -> bool:
        item = items.get_one(code=code)

        if item.craft is None:
            if item.subtype == "mob":
                return attacker.can_farm_resource(code=item.code, monsters=monsters)
            else:
                return item.level <= self.get_skill_level(skill=item.subtype)
        else:
            if item.craft.level > self.get_skill_level(skill=item.craft.skill):
                return False

            can_craft_children = True
            for child_item in item.craft.items:
                can_craft_child = self.can_craft(
                    code=child_item.code,
                    attacker=attacker,
                    items=items,
                    monsters=monsters,
                )
                can_craft_children = can_craft_children and can_craft_child

            return can_craft_children

    def can_craft_without_attacker(self, code: AnyStr, items: AllItems, bank) -> bool:
        item = items.get_one(code=code)

        if item.craft is None:
            if item.subtype == "mob":
                return False
            else:
                return item.level <= self.get_skill_level(skill=item.subtype)
        else:
            if item.craft.level > self.get_skill_level(skill=item.craft.skill):
                return False

            can_craft_children = True
            for child_item in item.craft.items:
                sub_item = items.get_one(code=child_item.code)
                bank_quantity = bank.get_quantity(
                    item_code=sub_item.code, character_name=self.name
                )
                if bank_quantity >= child_item.quantity:
                    continue
                else:
                    can_craft_child = self.can_craft_without_attacker(
                        code=child_item.code, items=items, bank=bank
                    )
                    can_craft_children = can_craft_children and can_craft_child

            return can_craft_children
