from typing import Any, Callable, Protocol, Type

import esper

from . import events


class SystemProtocol(Protocol):
    def process(self, *args, **kwargs): ...


def switch_world(name: str):
    esper.switch_world(name)


def delete_world(name: str):
    esper.delete_world(name)


def add_system(system: SystemProtocol, priority: int = 0):
    esper.add_processor(system, priority)


def remove_system(system_type: type[SystemProtocol]):
    esper.remove_processor(system_type)


def add_component(entity: int, component: Any):
    esper.add_component(entity, component)
    esper.dispatch_event(events.COMPONENT_ADDED_EVENT, entity, component)


def remove_component(entity: int, component_type: type[Any]):
    component = esper.get_component(component_type)
    esper.dispatch_event(events.COMPONENT_REMOVED_EVENT, entity, component)
    esper.remove_component(entity, component_type)


def get_component(entity: int, component: type[Any]) -> Any:
    return esper.component_for_entity(entity, component)


def get_components(*component_types: Any) -> list[tuple[int, tuple]]:
    return esper.get_components(*component_types)


def has_component(entity: int, component: type[Any]) -> bool:
    return esper.has_component(entity, component)


def try_component(entity: int, component: Type[Any]) -> Any:
    return esper.try_component(entity, component)


def try_components(entity: int, *components: Any) -> tuple:
    return esper.try_components(entity, *components)


def create_entity(*components: Any) -> int:
    entity = esper.create_entity(*components)
    for component in components:
        esper.dispatch_event(events.COMPONENT_ADDED_EVENT, entity, component)

    return entity


def delete_entity(entity: int):
    for component in esper.components_for_entity(entity):
        esper.dispatch_event(events.COMPONENT_REMOVED_EVENT, entity, component)
    esper.delete_entity(entity)


def entity_exists(entity: int) -> bool:
    return esper.entity_exists(entity)


def add_handlers(system: Any):
    if isinstance(system, events.AIStateProtocol):
        esper.set_handler(events.AI_ATTACK_EVENT, system.on_ai_attack)
        esper.set_handler(events.AI_DIRECTION_EVENT, system.on_ai_direction)
    if isinstance(system, events.CollisionProtocol):
        esper.set_handler(events.COLLISION_EVENT, system.on_collision)
        esper.set_handler(events.SENSOR_EVENT, system.on_sensor)
    if isinstance(system, events.ComponentAddedProtocol):
        esper.set_handler(events.COMPONENT_ADDED_EVENT, system.on_component_added)
    if isinstance(system, events.ComponentRemovedProtocol):
        esper.set_handler(events.COMPONENT_REMOVED_EVENT, system.on_component_removed)
    if isinstance(system, events.DrawProtocol):
        esper.set_handler(events.DRAW_EVENT, system.on_draw)
    if isinstance(system, events.ExitProtocol):
        esper.set_handler(events.EXIT_EVENT, system.on_exit)
    if isinstance(system, events.InputProtocol):
        esper.set_handler(events.KEY_DOWN_EVENT, system.on_key_down)
        esper.set_handler(events.KEY_UP_EVENT, system.on_key_up)
        esper.set_handler(events.MOUSE_DOWN_EVENT, system.on_mouse_down)
        esper.set_handler(events.MOUSE_UP_EVENT, system.on_mouse_up)
    if isinstance(system, events.PlayerStateProtocol):
        esper.set_handler(events.PLAYER_ATTACK_EVENT, system.on_player_attack)
        esper.set_handler(events.PLAYER_DIRECTION_EVENT, system.on_player_direction)
    if isinstance(system, events.PositionChangedProtocol):
        esper.set_handler(events.POSITION_CHANGED_EVENT, system.on_position_changed)


def remove_handlers(system: Any):
    if isinstance(system, events.CollisionProtocol):
        esper.remove_handler(events.COLLISION_EVENT, system.on_collision)
        esper.remove_handler(events.SENSOR_EVENT, system.on_sensor)
    if isinstance(system, events.ComponentAddedProtocol):
        esper.remove_handler(events.COMPONENT_ADDED_EVENT, system.on_component_added)
    if isinstance(system, events.ComponentRemovedProtocol):
        esper.remove_handler(
            events.COMPONENT_REMOVED_EVENT, system.on_component_removed
        )
    if isinstance(system, events.DrawProtocol):
        esper.remove_handler(events.DRAW_EVENT, system.on_draw)
    if isinstance(system, events.ExitProtocol):
        esper.remove_handler(events.EXIT_EVENT, system.on_exit)
    if isinstance(system, events.InputProtocol):
        esper.remove_handler(events.KEY_DOWN_EVENT, system.on_key_down)
        esper.remove_handler(events.KEY_UP_EVENT, system.on_key_up)
    if isinstance(system, events.PlayerStateProtocol):
        esper.remove_handler(events.PLAYER_ATTACK_EVENT, system.on_player_attack)
        esper.remove_handler(events.PLAYER_DIRECTION_EVENT, system.on_player_direction)
    if isinstance(system, events.PositionChangedProtocol):
        esper.remove_handler(events.POSITION_CHANGED_EVENT, system.on_position_changed)


def set_handler(name: str, func: Callable[..., None]):
    esper.set_handler(name, func)


def remove_handler(name: str, func: Callable[..., None]):
    esper.remove_handler(name, func)


def dispatch_event(name: str, *args):
    esper.dispatch_event(name, *args)


def update(*args, **kwargs):
    esper.process(*args, **kwargs)
