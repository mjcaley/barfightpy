from .. import ecs
from ..components import Player, PlayerMode


class PlayerSystem(ecs.SystemProtocol):
    def process(self, dt: float):
        for _, (player,) in ecs.get_components(Player):
            if player.expires > 0:
                player.expires = max(0, player.expires - dt)
            if player.mode == PlayerMode.Attacking and player.expires == 0:
                player.mode = PlayerMode.Idle
