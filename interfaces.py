from api.map import MapAPI
from api.item import ItemAPI
from api.monster import MonsterAPI
from api.characters import MyCharactersAPI
from api.character import MyCharacterAPI
from api.resource import ResourceAPI
from api.bank import BankAPI


map_api = MapAPI()
maps = map_api.get_all_maps()

item_api = ItemAPI()
items = item_api.get_all_items()

monster_api = MonsterAPI()
monsters = monster_api.get_all_monsters()

resource_api = ResourceAPI()
resources = resource_api.get_all_resources()

bank = BankAPI()

characters_api = MyCharactersAPI()

attacker_character = MyCharacterAPI(
    character=characters_api.get_all()[0]
)
gearcrafter_character = MyCharacterAPI(
    character=characters_api.get_all()[1]
)
weaponcrafter_character = MyCharacterAPI(
    character=characters_api.get_all()[3]
)
jewelrycrafter_character = MyCharacterAPI(
    character=characters_api.get_all()[4]
)
coocker_character = MyCharacterAPI(
    character=characters_api.get_all()[2]
)
