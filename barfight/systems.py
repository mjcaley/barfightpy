from typing import Any

import pyglet
from loguru import logger
from pyglet.graphics import Batch, Group
from pyglet.math import Vec2
from pyglet.window import Window, key, mouse

from . import ecs, events
from .bundles import add_attack
from .components import (
    Actor,
    ActorState,
    Attack,
    Enemy,
    Health,
    Layer,
    Path,
    PhysicsBody,
    Player,
    Position,
    Shape,
    Sprite,
    Velocity,
)
from .events import (
    AIStateProtocol,
    CollisionProtocol,
    ComponentAddedProtocol,
    ComponentRemovedProtocol,
    DrawProtocol,
    InputProtocol,
    PlayerStateProtocol,
)
from .pathfinding import Pathfinding
from .physics import Arbiter, Body, PhysicsWorld

# region Attack


class AttackSystem(ecs.SystemProtocol, CollisionProtocol):
    def process(self, *args, **kwargs):
        for entity, (attack,) in ecs.get_components(Attack):
            if attack.cleanup:
                ecs.delete_entity(entity)
            else:
                attack.cleanup = True

    def on_collision(self, arbiter: Arbiter): ...

    def on_sensor(self, arbiter: Arbiter):
        health = ecs.try_component(arbiter.first_body.data, Health)
        attack = ecs.try_component(arbiter.second_body.data, Attack)
        if not health and not attack:
            return

        if attack.entity == arbiter.first_body.data:
            return

        health.current -= 10
        logger.debug(
            "Entity {} hit {}", arbiter.first_body.data, arbiter.second_body.data
        )

        ecs.delete_entity(arbiter.second_body.data)


# endregion


# region Debug


class DebugSystem(
    ecs.SystemProtocol,
    ComponentAddedProtocol,
    ComponentRemovedProtocol,
    CollisionProtocol,
):
    def process(self, *args): ...

    def on_collision(self, arbiter: Arbiter):
        lposition, lcollider = ecs.try_components(
            arbiter.first_body.data, Position, PhysicsBody
        )
        lvelocity = ecs.try_component(arbiter.first_body.data, Velocity)

        rposition, rcollider = ecs.try_components(
            arbiter.second_body.data, Position, PhysicsBody
        )
        rvelocity = ecs.try_component(arbiter.second_body.data, Velocity)
        logger.debug(
            "Collision detected - {lentity} [Position {lposition}] [Velocity {lvelocity}] [Collider {lcollider}] : {rentity} [Position {rposition}] [Velocity {rvelocity}] [Collider {rcollider}]",
            lentity=arbiter.first_body.data,
            lposition=lposition,
            lvelocity=lvelocity,
            lcollider=lcollider,
            rentity=arbiter.second_body.data,
            rposition=rposition,
            rvelocity=rvelocity,
            rcollider=rcollider,
        )

    def on_sensor(self, arbiter: Arbiter):
        lposition, lbody = ecs.try_components(
            arbiter.first_body.data, Position, PhysicsBody
        )
        rposition, rbody = ecs.try_components(
            arbiter.second_body.data, Position, PhysicsBody
        )
        logger.debug(
            "Sensor detected - {lentity} {lposition} {lbody} - {rentity} {rposition} {rbody}",
            lentity=arbiter.first_body.data,
            lposition=lposition,
            lbody=lbody,
            rentity=arbiter.second_body.data,
            rposition=rposition,
            rbody=rbody,
        )

    def on_component_added(self, entity: int, component: Any):
        if isinstance(component, PhysicsBody):
            shape = pyglet.shapes.Box(
                component.body.shape.min.x,
                component.body.shape.min.y,
                component.body.shape.max.x - component.body.shape.min.x,
                component.body.shape.max.y - component.body.shape.min.y,
                color=(50, 25, 255),
            )
            ecs.add_component(entity, Shape(shape, Layer.Debug))

    def on_component_removed(self, entity: int, component: Any):
        if isinstance(component, PhysicsBody):
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
        for _, (physics_body, shape) in ecs.get_components(PhysicsBody, Shape):
            shape.shape.x = physics_body.body.rectangle.min.x
            shape.shape.y = physics_body.body.rectangle.min.y
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
    def __init__(
        self, key_handler: key.KeyStateHandler, mouse_handler: mouse.MouseStateHandler
    ):
        self.key_handler = key_handler
        self.mouse_handler = mouse_handler

    def process(self, *_):
        direction = Vec2()
        if self.key_handler[key.W]:
            direction.y += 1
        if self.key_handler[key.S]:
            direction.y -= 1
        if self.key_handler[key.A]:
            direction.x -= 1
        if self.key_handler[key.D]:
            direction.x += 1
        direction.normalize()

        ecs.dispatch_event(events.PLAYER_DIRECTION_EVENT, direction)

    def on_key_down(self, symbol: int, modifiers: int):
        if symbol == key.N:
            ecs.dispatch_event(events.PLAYER_ATTACK_EVENT)


# endregion

# region Movement


class MovementSystem(ecs.SystemProtocol):
    def process(self, dt: float):
        for entity, (_, position, velocity) in ecs.get_components(
            Actor, Position, Velocity
        ):
            change = velocity.direction * velocity.speed * dt
            if change != Vec2(0, 0):
                position.position += velocity.direction * velocity.speed * dt
                ecs.dispatch_event(events.POSITION_CHANGED_EVENT, entity)


# endregion

# region Physics


class PhysicsSystem(
    ecs.SystemProtocol,
    events.ComponentAddedProtocol,
    events.ComponentRemovedProtocol,
    events.PositionChangedProtocol,
):
    def __init__(self, world: PhysicsWorld):
        self.world = world
        self.world.on_collision_callback = self.on_physics_collision
        self.world.position_change_callback = self.on_physics_position_change
        self.world.on_sensor_callback = self.on_physics_sensor

    def process(self, dt: float):
        self.world.step()

    def on_component_added(self, entity: int, component: Any):
        if isinstance(component, PhysicsBody):
            self.world.insert(component.body)

    def on_component_removed(self, entity: int, component: Any):
        if isinstance(component, PhysicsBody):
            self.world.remove(component.body)

    def on_position_changed(self, entity: int):
        position, physics_body = ecs.try_components(entity, Position, PhysicsBody)
        if position and physics_body:
            physics_body.body.rectangle.center = position.position
            self.world.remove(physics_body.body)
            self.world.insert(physics_body.body)

    def on_physics_position_change(self, body: Body):
        position = ecs.get_component(body.data, Position)
        physics_body = ecs.get_component(body.data, PhysicsBody)
        position.position = physics_body.body.rectangle.center

    def on_physics_collision(self, arbiter: Arbiter):
        logger.debug(
            f"{arbiter.first_body.data} collides with {arbiter.second_body.data} first time: {arbiter.is_first_collision}"
        )
        ecs.dispatch_event(events.COLLISION_EVENT, arbiter)

    def on_physics_sensor(self, arbiter: Arbiter):
        ecs.dispatch_event(events.SENSOR_EVENT, arbiter)


# endregion

# region Actor


class ActorSystem(ecs.SystemProtocol, PlayerStateProtocol, AIStateProtocol):
    def process(self, dt: float):
        for _, (actor, position, velocity) in ecs.get_components(
            Actor, Position, Velocity
        ):
            match actor.state:
                case ActorState.Idle:
                    self.idle(actor, position, velocity)
                case ActorState.Walking:
                    self.walking(actor, position, velocity)
                case ActorState.Attacking:
                    self.attacking(dt, actor, position, velocity)

    def idle(self, actor: Actor, position: Position, velocity: Velocity):
        match actor.direction:
            case Vec2(x=0, y=0):
                ...
            case direction:
                actor.state = ActorState.Walking
                actor.facing = actor.direction.x
                velocity.direction = direction
                velocity.speed = actor.max_speed

    def walking(self, actor: Actor, position: Position, velocity: Velocity):
        match actor.direction:
            case Vec2(x=0, y=0):
                actor.state = ActorState.Idle
                velocity.direction = actor.direction
                velocity.speed = 0
            case _:
                actor.facing = actor.direction.x
                velocity.direction = actor.direction

    def attacking(
        self, dt: float, actor: Actor, position: Position, velocity: Velocity
    ):
        match actor.cooldown, actor.direction:
            case cooldown, _ if cooldown > 0:
                actor.cooldown = max(0, actor.cooldown - dt)
            case 0, Vec2(x=0, y=0):
                actor.state = ActorState.Idle
                velocity.direction = actor.direction
                velocity.speed = 0
            case 0, _:
                actor.state = ActorState.Walking
                actor.facing = actor.direction.x
                velocity.direction = actor.direction
                velocity.speed = actor.max_speed

    def _actor_attack(
        self, entity: int, actor: Actor, velocity: Velocity, physics_body: PhysicsBody
    ):
        attack_size = 20
        if actor.facing == 1:
            attack_min = Vec2(
                physics_body.body.shape.max.x,
                physics_body.body.shape.center.y - attack_size / 2,
            )
            attack_max = Vec2(
                physics_body.body.shape.max.x + attack_size,
                physics_body.body.shape.center.y + attack_size / 2,
            )
        else:
            attack_min = Vec2(
                physics_body.body.shape.min.x - attack_size,
                physics_body.body.shape.center.y - attack_size / 2,
            )
            attack_max = Vec2(
                physics_body.body.shape.min.x,
                physics_body.body.shape.center.y + attack_size / 2,
            )

        match actor.state, actor.cooldown:
            case ActorState.Idle | ActorState.Walking, _:
                actor.state = ActorState.Attacking
                velocity.speed = 0
                actor.cooldown = 0.2

                add_attack(entity, attack_min, attack_max)

            case ActorState.Attacking, 0:
                actor.cooldown = 0.2

                add_attack(entity, attack_min, attack_max)

    def on_player_direction(self, direction: Vec2):
        for _, (actor, _) in ecs.get_components(Actor, Player):
            actor.direction = direction

    def on_player_attack(self):
        for entity, (actor, velocity, physics_body, _) in ecs.get_components(
            Actor, Velocity, PhysicsBody, Player
        ):
            self._actor_attack(entity, actor, velocity, physics_body)

    def on_ai_direction(self, target: int, direction: Vec2):
        actor = ecs.get_component(target, Actor)
        actor.direction = direction

    def on_ai_attack(self, target: int):
        if components := ecs.try_components(
            target, Actor, Velocity, PhysicsBody, Enemy
        ):
            actor, velocity, physics_body, _ = components
            self._actor_attack(target, actor, velocity, physics_body)


# endregion

# region AI


class AISystem(ecs.SystemProtocol, AIStateProtocol, InputProtocol):
    def __init__(self, pathfinding: Pathfinding, window: Window):
        self.pathfinding = pathfinding
        self.window = window

    def process(self, dt: float):
        for entity, (_, position, path, actor) in ecs.get_components(
            Enemy, Position, Path, Actor
        ):
            actor_move_distance = actor.max_speed * dt
            if path.path:
                next_path = path.path[0]
                if next_path.distance(position.position) < actor_move_distance:
                    path.path.pop(0)
                else:
                    direction = (next_path - position.position).normalize()
                    ecs.dispatch_event(events.AI_DIRECTION_EVENT, entity, direction)
            else:
                if path.goal.distance(position.position) < actor_move_distance:
                    position.position = path.goal
                    ecs.dispatch_event(events.AI_DIRECTION_EVENT, entity, Vec2())
                    ecs.remove_component(entity, Path)
                else:
                    direction = (path.goal - position.position).normalize()
                    ecs.dispatch_event(events.AI_DIRECTION_EVENT, entity, direction)

    def on_mouse_down(self, x: int, y: int, button: int, modifiers: int):
        logger.debug("Mouse event")
        vx, vy, _, _ = self.window.viewport
        destination = Vec2(vx + x, vy + y)
        for entity, (_, _, position) in ecs.get_components(Enemy, Actor, Position):
            if ecs.has_component(entity, Path):
                continue
            start = position.position
            if path := self.pathfinding.find_path(start, destination):
                positions = [cell.rectangle.center for cell in path]
                ecs.add_component(entity, Path(destination, positions))
                logger.debug(f"Path created for enemy {entity} {positions}")

    def on_ai_direction(self, target: int, direction: Vec2):
        velocity = ecs.get_component(target, Velocity)
        velocity.direction = direction


# endregion
