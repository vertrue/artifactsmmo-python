from interfaces import (
    attacker_character,
    gearcrafter_character,
    weaponcrafter_character,
    jewelrycrafter_character,
    coocker_character,
    monsters,
    maps,
    items,
    resources,
    bank,
)
from controller.attacker import Attacker
from controller.crafter import Crafter
from controller.cooker import Cooker

attacker = Attacker(
    character=attacker_character, monsters=monsters, maps=maps, items=items
)

gearcrafter = Crafter(
    character=gearcrafter_character,
    monsters=monsters,
    maps=maps,
    items=items,
    resources=resources,
    bank=bank,
    craft_skill="gearcrafting",
    attacker=attacker,
)

weaponcrafter = Crafter(
    character=weaponcrafter_character,
    monsters=monsters,
    maps=maps,
    items=items,
    resources=resources,
    bank=bank,
    craft_skill="weaponcrafting",
    attacker=attacker,
)

jewelrycrafter = Crafter(
    character=jewelrycrafter_character,
    monsters=monsters,
    maps=maps,
    items=items,
    resources=resources,
    bank=bank,
    craft_skill="jewelrycrafting",
    attacker=attacker,
)

coocker = Cooker(
    character=coocker_character,
    monsters=monsters,
    maps=maps,
    items=items,
    resources=resources,
    craft_skill="cooking",
    attacker=attacker,
)
