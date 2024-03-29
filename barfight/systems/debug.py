import esper
from loguru import logger


class DebugSystem(esper.Processor):
    # def __init__(self):
    #     logger.level

    def process(self, *args):
        ...

    def on_collision(self, lentity, rentity):
        logger.debug("Collision detected", lentity=lentity, rentity=rentity)
