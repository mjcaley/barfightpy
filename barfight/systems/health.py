from loguru import logger

from .. import ecs
from ..components import Health


class HealthSystem(ecs.SystemProtocol):
    def process(self, *args, **kwargs):
        for entity, (health,) in ecs.get_components(Health):
            if health.current <= 0:
                logger.debug("Entity {} died", entity)
                ecs.delete_entity(entity)
