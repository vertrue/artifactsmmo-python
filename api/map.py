from api.base import BaseAPI

from models.map import AllMaps, Map

from typing import List


class MapAPI(BaseAPI):
    def __init__(self) -> None:
        super().__init__()

    def get_all_maps(self) -> AllMaps:
        all_data = self.get_all(method="/maps")
        return AllMaps(maps=all_data)

    def get_event_maps(self) -> AllMaps:
        try:
            all_data = self.get_all(method="/events")
            event_maps = [event["map"] for event in all_data]
            return AllMaps(maps=event_maps)
        except KeyError:
            return AllMaps(maps=[])

    @property
    def has_events(self) -> bool:
        events = self.get_event_maps()
        has_monster_event = False
        for event in events.maps:
            if event.content.type == "monster":
                has_monster_event = True
        return has_monster_event
