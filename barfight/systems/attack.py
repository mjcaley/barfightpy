from loguru import logger

from .. import ecs
from ..components import Attack, Health, Player
from . import protocols
from .collision import AABB


class AttackSystem(ecs.SystemProtocol, protocols.CollisionProtocol):
    def process(self, *args, **kwargs):
        for entity, (attack,) in ecs.get_components(Attack):
            match attack.active:
                case True:
                    attack.active = False
                case False:
                    ecs.remove_component(entity, Attack)

    def on_collision(self, source: AABB, collisions: list[AABB]):
        if not (attack := ecs.try_component(source.entity, Attack)):
            return

        for target in collisions:
            if attack.entity == target.entity:
                continue
            if health := ecs.try_component(target.entity, Health):
                health.current -= 10
                logger.debug("Entity {} hit {}", source.entity, target.entity)

        ecs.delete_entity(source.entity)
