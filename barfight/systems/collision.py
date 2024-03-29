import esper

from ..components import BoxCollider, Position


class CollisionSystem(esper.Processor):
    def process(self, *args):
        for lentity, (lposition, lcollider) in esper.get_components(Position, BoxCollider):
            for rentity, (rposition, rcollider) in esper.get_components(Position, BoxCollider):
                if lentity == rentity:
                    continue
                x_collision = lposition.position.x < rposition.position.x + rcollider.width and \
                    lposition.position.x + lcollider.width > rposition.position.x
                y_collision = lposition.position.y < rposition.position.y + rcollider.height and \
                    lposition.position.y + lcollider.height > rposition.position.y
                
                if x_collision and y_collision:
                    esper.dispatch_event("collision", lentity, rentity)
