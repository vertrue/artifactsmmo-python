from dataclasses import dataclass
from typing import List, Dict, Optional, AnyStr, Any, Union

from math import inf

from models.character import Character


@dataclass
class Content:
    type: str
    code: str


@dataclass
class Map:
    name: str
    skin: str
    x: int
    y: int
    content: Optional[Content]

    @staticmethod
    def from_dict(data: Dict) -> "Map":
        content_data = data.get("content")
        content = None
        if content_data:
            content = Content(
                type=content_data.get("type", ""), code=content_data.get("code", "")
            )
        return Map(
            name=data.get("name", ""),
            skin=data.get("skin", ""),
            x=data.get("x", 0),
            y=data.get("y", 0),
            content=content,
        )


class AllMaps:
    def __init__(self, maps: List[Dict]) -> None:
        self.maps = [Map.from_dict(map) for map in maps]

    def filter(
        self, content_code: AnyStr = None, content_type: AnyStr = None
    ) -> List[Map]:

        filtered_code = []

        if content_code:
            for map in self.maps:
                if map.content:
                    if map.content.code == content_code:
                        filtered_code += [map]
        else:
            filtered_code = self.maps

        filtered_type = []

        if content_type:
            for map in filtered_code:
                if map.content:
                    if map.content.type == content_type:
                        filtered_type += [map]
        else:
            filtered_type = filtered_code

        return filtered_type

    @staticmethod
    def dist(inst1: Union[Character, Map], inst2: Union[Character, Map]):
        return abs(inst1.x - inst2.x) + abs(inst1.y - inst2.y)

    def closest(
        self,
        character: Character,
        content_code: AnyStr = None,
        content_type: AnyStr = None,
    ):
        filtered = self.filter(content_code=content_code, content_type=content_type)

        closest = filtered[0]

        for map in filtered:
            if self.dist(map, character) < self.dist(closest, character):
                closest = map

        return map
