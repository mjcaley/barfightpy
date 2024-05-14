from collections import defaultdict
from functools import partial
from math import inf
from typing import Any, Self

import pyglet
from loguru import logger
from pyglet.graphics import Batch, Group
from pyglet.math import Vec2
from pyglet.window import Window, key

from .bundles import add_attack

from . import ecs, events, patch
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


class Line:
    def __init__(self, position: Vec2, direction: Vec2):
        self._position = position
        self._direction = direction.normalize()

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


def line_vs_rect(line: Line, rect: AABB) -> float | bool:
    if line.direction.x == 0:
        t_low_x = -inf
        t_high_x = inf
    else:
        t_low_x = (rect.min_x - line.position.x) / line.direction.x
        t_high_x = (rect.max_x - line.position.x) / line.direction.x
    if line.direction.y == 0:
        t_low_y = -inf
        t_high_y = inf
    else:
        t_low_y = (rect.min_y - line.position.y) / line.direction.y
        t_high_y = (rect.max_y - line.position.y) / line.direction.y

    t_close_x = min(t_low_x, t_high_x)
    t_far_x = max(t_low_x, t_high_x)
    t_close_y = min(t_low_y, t_high_y)
    t_far_y = max(t_low_y, t_high_y)

    t_close = max(t_close_x, t_close_y)
    t_far = min(t_far_x, t_far_y)

    if t_close > t_far:
        return False

    return t_close


# def line_vs_rect(line: Line, rect: AABB) -> float | None:
    # https://noonat.github.io/intersect/#aabb-vs-segment

    # Calculate
    # const scaleX = 1.0 / delta.x;
    # const scaleY = 1.0 / delta.y;
    # const signX = sign(scaleX);
    # const signY = sign(scaleY);
    # const nearTimeX = (this.pos.x - signX * (this.half.x + paddingX) - pos.x) * scaleX;
    # const nearTimeY = (this.pos.y - signY * (this.half.y + paddingY) - pos.y) * scaleY;
    # const farTimeX = (this.pos.x + signX * (this.half.x + paddingX) - pos.x) * scaleX;
    # const farTimeY = (this.pos.y + signY * (this.half.y + paddingY) - pos.y) * scaleY;

    # If the closest time of collision on either axis is further than the far time on the opposite axis, we can’t be colliding
    # if (nearTimeX > farTimeY || nearTimeY > farTimeX) {
    #   return null;
    # }

    # Otherwise find greater near times
    # const nearTime = nearTimeX > nearTimeY ? nearTimeX : nearTimeY;
    # const farTime = farTimeX < farTimeY ? farTimeX : farTimeY;

    # If the near time is greater than or equal to 1, the line starts in front of the nearest edge, but finishes before it reaches it.
    # If the far time is less than or equal to 0, the line starts in front of the far side of the box, and points away from the box.
    # if (nearTime >= 1 || farTime <= 0) {
    #   return null;
    # }

    # If the near time is greater than zero, the segment starts outside and is entering the box. Otherwise, the segment starts inside the box, and is exiting it.
    # const hit = new Hit(this);
    # hit.time = clamp(nearTime, 0, 1);
    # if (nearTimeX > nearTimeY) {
    #     hit.normal.x = -signX;
    #     hit.normal.y = 0;
    # } else {
    #     hit.normal.x = 0;
    #     hit.normal.y = -signY;
    # }
    # hit.delta.x = (1.0 - hit.time) * -delta.x;
    # hit.delta.y = (1.0 - hit.time) * -delta.y;
    # hit.pos.x = pos.x + delta.x * hit.time;
    # hit.pos.y = pos.y + delta.y * hit.time;
    # return hit;
    # }


def line_rect_intersection(line: Line, t: float) -> Vec2:
    return line.position + (line.direction * t)


def distance(point: Vec2, rect: AABB) -> float:
    line = Line(point, point - rect.position.position)
    t = abs(line_vs_rect(line, rect))
    intersection = line_rect_intersection(line, t)

    return intersection.distance(point)


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
    def __init__(self):
        self.handler = key.KeyStateHandler()

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
