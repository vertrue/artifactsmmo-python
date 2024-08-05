from dataclasses import dataclass, field
from typing import List, Dict, Optional, AnyStr


@dataclass
class Effect:
    name: str
    value: int


@dataclass
class CraftItem:
    code: str
    quantity: int


@dataclass
class Craft:
    skill: str
    level: int
    quantity: int
    items: List[CraftItem] = field(default_factory=list)


@dataclass
class Item:
    name: str
    code: str
    level: int
    type: str
    subtype: str
    description: str
    craft: Optional[Craft] = None
    effects: List[Effect] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict) -> "Item":
        effects = [Effect(**effect) for effect in data.get("effects", [])]
        try:
            craft_items = [
                CraftItem(**item) for item in data.get("craft", {}).get("items", [])
            ]
        except AttributeError:
            craft_items = None

        try:
            craft = Craft(
                skill=data.get("craft", {}).get("skill", ""),
                level=data.get("craft", {}).get("level", 0),
                items=craft_items,
                quantity=data.get("craft", {}).get("quantity", 0),
            )
        except AttributeError:
            craft = None
        return Item(
            name=data.get("name", ""),
            code=data.get("code", ""),
            level=data.get("level", 1),
            type=data.get("type", ""),
            subtype=data.get("subtype", ""),
            description=data.get("description", ""),
            effects=effects,
            craft=craft,
        )

    def get_effect_value(self, effect_name: AnyStr) -> int:
        for effect in self.effects:
            if effect.name == effect_name:
                return effect.value
        return 0


class AllItems:
    def __init__(self, items: List[Dict]) -> None:
        self.items = [Item.from_dict(item) for item in items]

    def filter(
        self,
        craft_material: AnyStr = None,
        craft_skill: AnyStr = None,
        max_level: int = None,
        min_level: int = None,
    ) -> List[Item]:

        filtered_craft_material = []
        if craft_material:
            for item in self.items:
                if item.craft:
                    for cr_item in item.craft.items:
                        if cr_item.code == craft_material:
                            filtered_craft_material += [item]
        else:
            filtered_craft_material = self.items

        filtered_craft_skill = []
        if craft_skill:
            for item in filtered_craft_material:
                if item.craft:
                    if item.craft.skill == craft_skill:
                        filtered_craft_skill += [item]
        else:
            filtered_craft_skill = filtered_craft_material

        filtered_max_level = []
        if max_level:
            for item in filtered_craft_skill:
                if item.craft:
                    if item.craft.level <= max_level:
                        filtered_max_level += [item]
        else:
            filtered_max_level = filtered_craft_skill

        filtered_min_level = []
        if min_level:
            for item in filtered_max_level:
                if item.craft:
                    if item.craft.level >= min_level:
                        filtered_min_level += [item]
        else:
            filtered_min_level = filtered_max_level

        return filtered_min_level

    def get_one(self, code: AnyStr) -> Item:
        for item in self.items:
            if item.code == code:
                return item
        return None
