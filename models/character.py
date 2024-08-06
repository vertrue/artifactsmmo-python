from dataclasses import dataclass, field
from typing import List, Dict, Optional, AnyStr

from models.monster import Monster, AllMonsters
from models.item import Item, AllItems

from copy import copy

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
            if slot == "ring":
                try:
                    item_code_1 = eval(f"self.{slot}1_slot")
                    item_1 = items.get_one(item_code_1)
                    item_code_2 = eval(f"self.{slot}2_slot")
                    item_2 = items.get_one(item_code_2)
                    return item_1 if item_1.level < item_2.level else item_2
                except AttributeError:
                    return None
            elif slot == "artifact":
                try:
                    item_code_1 = eval(f"self.{slot}1_slot")
                    item_1 = items.get_one(item_code_1)
                    item_code_2 = eval(f"self.{slot}2_slot")
                    item_2 = items.get_one(item_code_2)
                    item_code_3 = eval(f"self.{slot}3_slot")
                    item_3 = items.get_one(item_code_3)
                    if item_1.level <= item_2.level and item_1.level <= item_3.level:
                        return item_1
                    if item_2.level <= item_3.level and item_2.level <= item_1.level:
                        return item_2
                    if item_3.level <= item_2.level and item_3.level <= item_1.level:
                        return item_1
                    return item_1
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

    def find_best_monster(self, monsters: AllMonsters, items: AllItems, bank):
        filtered_monsters = monsters.filter()

        for monster in filtered_monsters:
            can_beat, _ = self.find_optimal_build(
                monster=monster, items=items, bank=bank
            )
            if can_beat:
                target_monster = monster
                break

        for monster in filtered_monsters:
            can_beat, _ = self.find_optimal_build(
                monster=monster, items=items, bank=bank
            )
            if can_beat and monster.level > target_monster.level:
                target_monster = monster

        return target_monster

    def can_beat(self, monster: Monster) -> bool:
        players_hp = self.hp
        mobs_hp = monster.hp

        for i in range(1, 101):
            if i % 2 == 1:
                # player
                player_attack = round(
                    self.attack_air
                    * (1 + self.dmg_air / 100)
                    * (1 - monster.res_air / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True

                player_attack = round(
                    self.attack_earth
                    * (1 + self.dmg_earth / 100)
                    * (1 - monster.res_earth / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True

                player_attack = round(
                    self.attack_fire
                    * (1 + self.dmg_fire / 100)
                    * (1 - monster.res_fire / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True

                player_attack = round(
                    self.attack_water
                    * (1 + self.dmg_water / 100)
                    * (1 - monster.res_water / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True
            else:
                # mob
                mob_attack = round(monster.attack_air * (1 - self.res_air / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False

                mob_attack = round(monster.attack_earth * (1 - self.res_earth / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False

                mob_attack = round(monster.attack_fire * (1 - self.res_fire / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False

                mob_attack = round(monster.attack_water * (1 - self.res_water / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False

        return False

    @staticmethod
    def unequiped_stats(character: "Character", item: Item):
        char = copy(character)
        for effect in item.effects:
            try:
                current_value = getattr(char, effect.name)
                setattr(char, effect.name, current_value - effect.value)
            except AttributeError:
                pass

        return char

    @staticmethod
    def equiped_stats(character: "Character", item: Item):
        char = copy(character)
        for effect in item.effects:
            try:
                current_value = getattr(char, effect.name)
                setattr(char, effect.name, current_value + effect.value)
            except AttributeError:
                pass

        return char

    def can_beat_check(
        self,
        monster: Monster,
        items: AllItems,
        picked_items: Dict[AnyStr, Item | int | bool | None],
    ):
        character = copy(self)
        for slot, picked_item in picked_items.items():
            if slot != "can_beat" and slot != "rounds" and picked_item is not None:
                equiped_item = character.get_slot_item(slot=slot, items=items)
                if equiped_item is None:
                    equiped = character.equiped_stats(character=character, item=picked_item)
                else:
                    unequiped = character.unequiped_stats(
                        character=character, item=equiped_item
                    )
                    equiped = character.equiped_stats(character=unequiped, item=picked_item)
                character = equiped

        players_hp = character.hp
        mobs_hp = monster.hp

        for i in range(1, 101):
            if i % 2 == 1:
                # player
                player_attack = round(
                    character.attack_air
                    * (1 + character.dmg_air / 100)
                    * (1 - monster.res_air / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True, i, players_hp, mobs_hp

                player_attack = round(
                    character.attack_earth
                    * (1 + character.dmg_earth / 100)
                    * (1 - monster.res_earth / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True, i, players_hp, mobs_hp

                player_attack = round(
                    character.attack_fire
                    * (1 + character.dmg_fire / 100)
                    * (1 - monster.res_fire / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True, i, players_hp, mobs_hp

                player_attack = round(
                    character.attack_water
                    * (1 + character.dmg_water / 100)
                    * (1 - monster.res_water / 100)
                )
                mobs_hp -= player_attack
                if mobs_hp <= 0:
                    return True, i, players_hp, mobs_hp
            else:
                # mob
                mob_attack = round(monster.attack_air * (1 - character.res_air / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False, i, players_hp, mobs_hp

                mob_attack = round(monster.attack_earth * (1 - character.res_earth / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False, i, players_hp, mobs_hp

                mob_attack = round(monster.attack_fire * (1 - character.res_fire / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False, i, players_hp, mobs_hp

                mob_attack = round(monster.attack_water * (1 - character.res_water / 100))
                players_hp -= mob_attack
                if players_hp <= 0:
                    return False, i, players_hp, mobs_hp

        return False, i, players_hp, mobs_hp

    def find_optimal_build(
        self, monster: Monster, items: AllItems, bank
    ) -> tuple[bool, Dict[AnyStr, Item | int | bool | None]]:
        slots = [
            "shield",
            "helmet",
            "body_armor",
            "leg_armor",
            "boots",
            "ring1",
            "ring2",
            "amulet",
            "artifact1",
            "artifact2",
            "artifact3",
        ]

        all_items = bank.get_all_items()
        bank_items_amount = {}
        for item in all_items.items:
            bank_items_amount[item.code] = item.quantity
        bank_items = [items.get_one(item.code) for item in all_items.items]

        # weapon
        character_weapon = self.get_slot_item(slot="weapon", items=items)
        possible_weapons = [character_weapon]
        for item in bank_items:
            if item.type == "weapon":
                possible_weapons += [item]

        best_build = {"can_beat": self.can_beat(monster=monster), "rounds": 100}

        for weapon in possible_weapons:
            if weapon is None:
                continue
            if weapon.level > self.level:
                continue

            picked_items = {"weapon": weapon}
            picked_items_amount = {}
            for item in all_items.items:
                picked_items_amount[item.code] = 0

            for slot in slots:
                character_item = self.get_slot_item(slot=slot, items=items)

                possible_items = [character_item]

                for item in bank_items:
                    if item.level > self.level:
                        continue
                    if item.type == slot or item.type == slot[: len(slot) - 1]:
                        if picked_items_amount[item.code] < bank_items_amount[item.code]:
                            possible_items += [item]

                if possible_items == [None]:
                    continue

                best_item_score = 0
                best_item = character_item

                for item in possible_items:
                    if item is not None:
                        item_score = self.item_score(
                            monster=monster,
                            item=item,
                            weapon=weapon
                        )
                        if item_score > best_item_score:
                            best_item = item
                            best_item_score = item_score

                picked_items[slot] = best_item

                if best_item:
                    try:
                        picked_items_amount[best_item.code] += 1
                    except KeyError:
                        picked_items_amount[best_item.code] = 1

            picked_items["can_beat"], rounds, _, _ = (
                self.can_beat_check(
                    monster=monster,
                    items=items,
                    picked_items=picked_items,
                )
            )
            picked_items["rounds"] = rounds

            if picked_items["can_beat"] and picked_items["rounds"] < best_build["rounds"]:
                best_build = picked_items

        can_beat = best_build["can_beat"]
        best_build.pop("can_beat", None)
        best_build.pop("rounds", None)

        return can_beat, best_build

    def item_score(self, monster: Monster, item: Item, weapon: Item):
        attack_coof = 5
        dmg_coof = 3
        res_coof = 1
        # TODO: hp
        score = 0
        for effect in item.effects:
            element = effect.name.split("_")[-1]
            attack_element = f"attack_{element}"

            if "attack_" in effect.name:
                score += attack_coof * effect.value

            if "dmg_" in effect.name:
                if weapon.get_effect_value(effect_name=attack_element) > 0:
                    score += dmg_coof * effect.value

            if "res_" in effect.name:
                if getattr(monster, f"attack_{element}") > 0:
                    score += res_coof * effect.value

        return score

    def can_farm_resource(self, code: AnyStr, items: AllItems, monsters: AllMonsters, bank) -> bool:
        monster = monsters.get_drops(drop=code)
        can_beat, _ = self.find_optimal_build(
            monster=monster,
            items=items,
            bank=bank,
        )
        return can_beat

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
                code=item.code, attacker=attacker, items=items, monsters=monsters, bank=bank
            ):
                if not bank.has_item(item=item):
                    return item

        return None

    def find_all_crafts(self, skill: AnyStr, items: AllItems, bank) -> List[Item]:
        filtered_items = items.filter(craft_skill=skill)

        all_crafts = []
        for item in filtered_items:
            if self.can_craft_without_attacker(code=item.code, items=items, bank=bank):
                all_crafts += [item]

        return all_crafts

    def find_best_craft(self, skill: AnyStr, items: AllItems, bank) -> Item:
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

    def find_best_craft_with_attacker(self, skill: AnyStr, attacker: 'Character', items: AllItems, monsters: AllMonsters, bank) -> Item:
        filtered_items = items.filter(craft_skill=skill)

        for item in filtered_items:
            if self.can_craft(code=item.code, attacker=attacker, items=items, monsters=monsters, bank=bank):
                best_item = item
                break

        for item in filtered_items:
            if self.can_craft(code=item.code, attacker=attacker, items=items, monsters=monsters, bank=bank):
                if item.level > best_item.level:
                    best_item = item

        return best_item

    def find_best_craft_for_attacker(
        self,
        skill: AnyStr,
        attacker: "Character",
        items: AllItems,
        monsters: AllMonsters,
        bank
    ):
        filtered_items = items.filter(craft_skill=skill)

        for item in filtered_items:
            if self.can_craft(
                code=item.code, attacker=attacker, items=items, monsters=monsters, bank=bank
            ):
                if attacker.get_slot_item(slot=item.type, items=items) is None:
                    return item
                if (
                    attacker.get_slot_item(slot=item.type, items=items).level
                    < item.level
                ):
                    return item

    def can_craft(
        self,
        code: AnyStr,
        attacker: "Character",
        items: AllItems,
        monsters: AllMonsters,
        quantity=1,
        bank=None,
        root=True
    ) -> bool:
        item = items.get_one(code=code)

        if bank and not root:
            if bank.get_quantity(item_code=item.code, character_name=self.name) >= quantity:
                return True

        if item.craft is None:
            if item.subtype == "mob":
                return attacker.can_farm_resource(code=item.code, items=items, monsters=monsters, bank=bank)
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
                    quantity=child_item.quantity,
                    bank=bank,
                    root=False
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
