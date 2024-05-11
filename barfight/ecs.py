from typing import Any, Callable, Protocol

import esper
from pyglet.window import key

COMPONENT_ADDED_EVENT = "component_added"
COMPONENT_REMOVED_EVENT = "component_removed"
DRAW_EVENT = "draw"
KEY_UP_EVENT = "key_up"
KEY_DOWN_EVENT = "key_down"
EXIT_EVENT = "exit"
COLLISION_EVENT = "collision"
DAMAGE_EVENT = "damage"
PLAYER_DIRECTION_EVENT = "player_direction"
PLAYER_ATTACK_EVENT = "player_attack"


class SystemProtocol(Protocol):
    def process(self, *args, **kwargs): ...


def add_system(system: SystemProtocol, priority: int = 0):
    esper.add_processor(system, priority)


def remove_system(system_type: type[SystemProtocol]):
    esper.remove_processor(system_type)


def add_component(entity: int, component: Any):
    esper.add_component(entity, component)
    esper.dispatch_event(COMPONENT_ADDED_EVENT, entity, component)


def remove_component(entity: int, component_type: type[Any]):
    component = esper.get_component(component_type)
    esper.remove_component(entity, component_type)
    esper.dispatch_event(COMPONENT_REMOVED_EVENT, entity, component)


def get_component(entity: int, component: type[Any]) -> Any:
    return esper.component_for_entity(entity, component)


def get_components(*component_types: Any) -> list[tuple[int, tuple[Any]]]:
    return esper.get_components(*component_types)


def has_component(entity: int, component: type[Any]) -> bool:
    return esper.has_component(entity, component)


def try_component(entity: int, component: Any) -> Any:
    return esper.try_component(entity, component)


def try_components(entity: int, *components: Any) -> tuple:
    return esper.try_components(entity, *components)


def create_entity(*components: Any) -> int:
    entity = esper.create_entity(*components)
    for component in components:
        esper.dispatch_event(COMPONENT_ADDED_EVENT, entity, component)

    return entity


def delete_entity(entity: int):
    esper.delete_entity(entity)


def set_handler(name: str, func: Callable[..., None]):
    esper.set_handler(name, func)


def remove_handler(name: str, func: Callable[..., None]):
    esper.remove_handler(name, func)


def dispatch_event(name: str, *args):
    esper.dispatch_event(name, *args)


def update(*args, **kwargs):
    esper.process(*args, **kwargs)
