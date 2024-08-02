from dataclasses import dataclass, field
from typing import List, Dict, AnyStr


@dataclass
class Drop:
    code: str
    rate: float
    min_quantity: int
    max_quantity: int


@dataclass
class Resource:
    name: str
    code: str
    skill: str
    level: int
    drops: List[Drop] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict) -> "Resource":
        drops = [Drop(**drop) for drop in data.get("drops", [])]
        return Resource(
            name=data.get("name", ""),
            code=data.get("code", ""),
            skill=data.get("skill", ""),
            level=data.get("level", 0),
            drops=drops,
        )


class AllResources:
    def __init__(self, resources: List[Dict]) -> None:
        self.resources = [Resource.from_dict(resource) for resource in resources]

    def filter(
        self, drop: AnyStr = None, max_level: int = None, min_level: int = None
    ) -> List[Resource]:

        filtered_drop = []
        if drop:
            for resource in self.resources:
                if resource.drops:
                    for dr_resource in resource.drops:
                        if dr_resource.code == drop:
                            filtered_drop += [resource]
        else:
            filtered_drop = self.resources

        filtered_max_level = []
        if max_level:
            for resource in filtered_drop:
                if resource.level <= max_level:
                    filtered_max_level += [resource]
        else:
            filtered_max_level = filtered_drop

        filtered_min_level = []
        if min_level:
            for resource in filtered_max_level:
                if resource.level >= min_level:
                    filtered_min_level += [resource]
        else:
            filtered_min_level = filtered_max_level

        return filtered_min_level

    def get_drops(self, drop: AnyStr = None) -> Resource:

        filtered_drops = self.filter(drop=drop)

        picked_resource = filtered_drops[0]
        for resource in filtered_drops:
            if resource.level < picked_resource.level:
                picked_resource = resource

        return picked_resource
