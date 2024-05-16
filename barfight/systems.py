from collections import defaultdict
from functools import partial
from math import inf
from typing import Any, Self

import pyglet
from loguru import logger
from pyglet.graphics import Batch, Group
from pyglet.math import Vec2
from pyglet.window import Window, key

from . import ecs, events, patch
from .bundles import add_attack
from .components import (
    Attack,
    BoxCollider,
    Health,
    Layer,
    Player,
    PlayerState,
    Position,
    Shape,
    Sprite,
    Velocity,
    Wall,
)
from .events import (
    CollisionProtocol,
    ComponentAddedProtocol,
    ComponentRemovedProtocol,
    DrawProtocol,
    InputProtocol,
    PlayerStateProtocol,
)

# region Data


class AABB:
    def __init__(self, entity: int, position: Position, width: float, height: float):
        self._entity = entity
        self._position = position
        self._half_width = width / 2
        self._half_height = height / 2

    def __str__(self) -> str:
        return f"AABB(entity={self._entity}, position={self._position}, width={self._half_width * 2}, height={self._half_height * 2})"

    def __repr__(self) -> str:
        return f"AABB(entity={self._entity}, position={self._position}, width={self._half_width * 2}, height={self._half_height * 2})"

    @classmethod
    def from_entity(cls, entity: int) -> Self:
        if components := ecs.try_components(entity, Position, BoxCollider):
            position, collider = components
            return cls(entity, position, collider.width, collider.height)
        else:
            raise RuntimeError("Missing required components to create instance")

    @property
    def entity(self) -> int:
        return self._entity

    @property
    def low(self) -> Vec2:
        return Vec2(
            self.position.position.x - self._half_width,
            self.position.position.y - self._half_height,
        )

    @property
    def high(self) -> Vec2:
        return Vec2(
            self.position.position.x + self._half_width,
            self.position.position.y + self._half_height,
        )

    @property
    def position(self) -> Position:
        return self._position

    @property
    def min_x(self):
        return self.low.x

    @property
    def max_x(self):
        return self.high.x

    @property
    def min_y(self):
        return self.low.y

    @property
    def max_y(self):
        return self.high.y


class Ray:
    def __init__(self, position: Vec2, direction: Vec2):
        self._position = position
        self._direction = direction.normalize()

    def __str__(self) -> str:
        return f"Ray(position={self._position}, direction={self._direction})"

    def __repr__(self) -> str:
        return f"Ray(position={self._position}, direction={self._direction})"

    @property
    def position(self) -> Vec2:
        return self._position

    @property
    def direction(self) -> Vec2:
        return self._direction


# endregion

# region Attack


class AttackSystem(ecs.SystemProtocol, CollisionProtocol):
    def process(self, *args, **kwargs):
        for entity, (attack,) in ecs.get_components(Attack):
            if attack.cleanup:
                ecs.delete_entity(entity)
            else:
                attack.cleanup = True

    def on_collision(self, source: int, collisions: set[int]):
        if not (attack := ecs.try_component(source, Attack)):
            return

        for target in collisions:
            if attack.entity == target:
                continue
            if health := ecs.try_component(target, Health):
                health.current -= 10
                logger.debug("Entity {} hit {}", source, target)

        ecs.delete_entity(source)


# endregion


# region Collision


def point_rect_collides(point: Vec2, rect: AABB) -> bool:
    return (
        point.x >= rect.low.x
        and point.x <= rect.high.x
        and point.y >= rect.low.y
        and point.y <= rect.high.y
    )


def point_rect_resolve(point: Vec2, rect: AABB) -> Vec2:
    resolutions = [
        Vec2(rect.min_x, 0) - point,
        Vec2(rect.max_x, 0) - point,
        Vec2(0, rect.min_y) - point,
        Vec2(0, rect.max_y) - point,
    ]

    def distance(v: Vec2) -> float:
        return point.distance(v)

    nearest = min(resolutions, key=distance)

    return nearest


def rect_vs_rect(first: AABB, second: AABB) -> bool:
    return (
        first.min_x < second.max_x
        and first.max_x > second.min_x
        and first.min_y < second.max_y
        and first.max_y > second.min_y
    )


def rect_rect_resolve(first: AABB, second: AABB) -> Vec2:
    distance = inf
    nearest = Vec2(0, 0)

    left = abs(first.max_x - second.min_x)
    if left < distance:
        distance = left
        nearest = Vec2(-distance, 0)
    right = abs(first.min_x - second.max_x)
    if right < distance:
        distance = right
        nearest = Vec2(distance, 0)
    up = abs(first.min_y - second.max_y)
    if up < distance:
        distance = up
        nearest = Vec2(0, distance)
    down = abs(first.max_y - second.min_y)
    if down < distance:
        distance = down
        nearest = Vec2(0, -distance)

    return nearest


def ray_vs_rect(ray: Ray, rect: AABB) -> Vec2 | None:
    tmin = -inf
    tmax = inf

    if ray.direction.x != 0:
        tx1 = (rect.min_x - ray.position.x) / ray.direction.x
        tx2 = (rect.max_x - ray.position.x) / ray.direction.x
        tmin = max(tmin, min(tx1, tx2))
        tmax = min(tmax, max(tx1, tx2))
    else:
        if ray.position.x < rect.min_x or ray.position.x > rect.max_x:
            return None

    if ray.direction.y != 0:
        ty1 = (rect.min_y - ray.position.y) / ray.direction.y
        ty2 = (rect.max_y - ray.position.y) / ray.direction.y
        tmin = max(tmin, min(ty1, ty2))
        tmax = min(tmax, max(ty1, ty2))
    else:
        if ray.position.y < rect.min_y or ray.position.y > rect.max_y:
            return None

    if tmax >= tmin >= 0:
        intersection = ray.position + (ray.direction * tmin)
        return intersection
    else:
        return None


def distance(point: Vec2, rect: AABB) -> float | None:
    ray = Ray(point, rect.position.position - point)
    if intersection := ray_vs_rect(ray, rect):
        return intersection.distance(point)
    else:
        return inf


class CollisionSystem(ecs.SystemProtocol):
    def process(self, dt: float):
        collisions = defaultdict(set)

        for lentity, (lpos, lcollider) in ecs.get_components(Position, BoxCollider):
            laabb = AABB(lentity, lpos, lcollider.width, lcollider.height)
            for rentity, (rpos, rcollider) in ecs.get_components(Position, BoxCollider):
                if lentity == rentity:
                    continue
                raabb = AABB(rentity, rpos, rcollider.width, rcollider.height)

                if rect_vs_rect(laabb, raabb):
                    collisions[lentity].add(rentity)
                    collisions[rentity].add(lentity)

        for source, collisions in collisions.items():
            ecs.dispatch_event(events.COLLISION_EVENT, source, collisions)


# endregion

# region Debug


class DebugSystem(
    ecs.SystemProtocol,
    ComponentAddedProtocol,
    ComponentRemovedProtocol,
    CollisionProtocol,
):
    def process(self, *args): ...

    def on_collision(self, source: int, collisions: set[int]):
        lposition, lcollider = ecs.try_components(source, Position, BoxCollider)
        lvelocity = ecs.try_component(source, Velocity)

        for target in collisions:
            rposition, rcollider = ecs.try_components(target, Position, BoxCollider)
            rvelocity = ecs.try_component(target, Velocity)
            logger.debug(
                "Collision detected - {lentity} [Position {lposition}] [Velocity {lvelocity}] [Collider {lcollider}] : {rentity} [Position {rposition}] [Velocity {rvelocity}] [Collider {rcollider}]",
                lentity=source,
                lposition=lposition,
                lvelocity=lvelocity,
                lcollider=lcollider,
                rentity=target,
                rposition=rposition,
                rvelocity=rvelocity,
                rcollider=rcollider,
            )

    def on_component_added(self, entity: int, component: Any):
        if isinstance(component, BoxCollider):
            shape = pyglet.shapes.Box(
                0, 0, component.width, component.height, color=(50, 25, 255)
            )
            shape.anchor_position = (component.width / 2, component.height / 2)
            ecs.add_component(entity, Shape(shape, Layer.Debug))

    def on_component_removed(self, entity: int, component: Any):
        if isinstance(component, BoxCollider):
            ecs.remove_component(entity, Shape)


# endregion

# region Draw


class DrawSystem(ecs.SystemProtocol, DrawProtocol, ComponentAddedProtocol):
    def __init__(self):
        self.game_layer = Group(Layer.Game)
        self.debug_layer = Group(Layer.Debug)
        self.batch = Batch()

    def process(self, *_): ...

    def on_draw(self, window: Window):
        for _, (position, sprite) in ecs.get_components(Position, Sprite):
            sprite.sprite.update(x=position.position.x, y=position.position.y)
        for _, (position, shape) in ecs.get_components(Position, Shape):
            shape.shape.x = position.position.x
            shape.shape.y = position.position.y
        self.batch.draw()

    def on_component_added(self, entity: int, component: ecs.Any):
        if isinstance(component, Sprite):
            component.sprite.batch = self.batch
            match component.layer:
                case Layer.Game:
                    component.sprite.group = self.game_layer
                case Layer.Debug:
                    component.sprite.group = self.debug_layer
        elif isinstance(component, Shape):
            component.shape.batch = self.batch
            match component.layer:
                case Layer.Game:
                    component.shape.group = self.game_layer
                case Layer.Debug:
                    component.shape.group = self.debug_layer


# endregion

# region Health


class HealthSystem(ecs.SystemProtocol):
    def process(self, *args, **kwargs):
        for entity, (health,) in ecs.get_components(Health):
            if health.current <= 0:
                logger.debug("Entity {} died", entity)
                ecs.delete_entity(entity)


# endregion

# region Input


class InputSystem(ecs.SystemProtocol, InputProtocol):
    def __init__(self, handler: key.KeyStateHandler):
        self.handler = handler

    def process(self, *_):
        direction = Vec2()
        if self.handler[key.W]:
            direction.y += 1
        if self.handler[key.S]:
            direction.y -= 1
        if self.handler[key.A]:
            direction.x -= 1
        if self.handler[key.D]:
            direction.x += 1
        direction.normalize()

        for _, (player,) in ecs.get_components(Player):
            player.direction = direction

    def on_key_down(self, symbol: int, modifiers: int):
        if symbol == key.N:
            ecs.dispatch_event(events.PLAYER_ATTACK_EVENT)

    def on_key_up(self, symbol: int, modifiers: int): ...


# endregion

# region Movement


class MovementSystem(ecs.SystemProtocol, CollisionProtocol):
    def process(self, dt: float):
        for entity, (_, position, velocity) in ecs.get_components(
            Player, Position, Velocity
        ):
            position.position += velocity.direction * velocity.speed * dt

    def on_collision(self, source: int, collisions: set[int]):
        if not ecs.has_component(source, Player):
            return

        laabb = AABB.from_entity(source)
        raabbs = sorted(
            (AABB.from_entity(target) for target in collisions),
            key=partial(distance, laabb.position.position),
        )

        # collisions.sort(key=partial(distance, source.position.position))
        for target in raabbs:
            if not ecs.has_component(target.entity, Wall):
                continue
            if rect_vs_rect(laabb, target):
                resolve = rect_rect_resolve(laabb, target)
                laabb.position.position += resolve


# endregion

# region Player


class PlayerSystem(ecs.SystemProtocol, PlayerStateProtocol):
    def process(self, dt: float):
        for entity, (player, position, velocity) in ecs.get_components(
            Player, Position, Velocity
        ):
            match player.state:
                case PlayerState.Idle:
                    self.idle(player, position, velocity)
                case PlayerState.Walking:
                    self.walking(player, position, velocity)
                case PlayerState.Attacking:
                    self.attacking(dt, player, position, velocity)

    def idle(self, player: Player, position: Position, velocity: Velocity):
        match player.direction:
            case Vec2(0, 0):
                ...
            case direction:
                player.state = PlayerState.Walking
                player.facing = player.direction.x
                velocity.direction = direction
                velocity.speed = player.max_speed

    def walking(self, player: Player, position: Position, velocity: Velocity):
        match player.direction:
            case Vec2(0, 0):
                player.state = PlayerState.Idle
                velocity.direction = player.direction
                velocity.speed = 0
            case _:
                player.facing = player.direction.x
                velocity.direction = player.direction

    def attacking(
        self, dt: float, player: Player, position: Position, velocity: Velocity
    ):
        match player.cooldown, player.direction:
            case cooldown, _ if cooldown > 0:
                player.cooldown = max(0, player.cooldown - dt)
            case 0, Vec2(0, 0):
                player.state = PlayerState.Idle
                velocity.direction = player.direction
                velocity.speed = 0
            case 0, _:
                player.state = PlayerState.Walking
                player.facing = player.direction.x
                velocity.direction = player.direction
                velocity.speed = player.max_speed

    def on_player_attack(self):
        for entity, (player, position, velocity, collider) in ecs.get_components(
            Player, Position, Velocity, BoxCollider
        ):
            attack_pos = Vec2(position.position.x, position.position.y)
            attack_size = 20
            if player.facing == 1:
                attack_pos.x += collider.width / 2 + attack_size / 2
            else:
                attack_pos.x -= collider.width / 2 + attack_size / 2

            match player.state, player.cooldown:
                case PlayerState.Idle | PlayerState.Walking, _:
                    player.state = PlayerState.Attacking
                    velocity.speed = 0
                    player.cooldown = 0.2

                    add_attack(entity, attack_pos, attack_size)

                case PlayerState.Attacking, 0:
                    player.cooldown = 0.2

                    add_attack(entity, attack_pos, attack_size)


# endregion
