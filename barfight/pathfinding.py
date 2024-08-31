from dataclasses import dataclass
from pyglet.math import Vec2

from barfight.physics import PhysicsWorld, Rectangle


@dataclass
class Cell:
    position: Vec2
    walkable: bool = True


class Grid:
    def __init__(self, world: PhysicsWorld, radius: float):
        self.world = world
        self.radius = radius
        self.grid: list[list[Cell]] = self.create_grid()

    def create_grid(self) -> list[list[Cell]]:
        num_x_cells = int((self.world.boundary.max.x - self.world.boundary.min.x) // (self.radius * 2))
        num_y_cells = int((self.world.boundary.max.y - self.world.boundary.min.y) // (self.radius * 2))
        grid = []
        for x in range(num_x_cells):
            line = []
            for y in range(num_y_cells):
                min = Vec2(x * self.radius, y * self.radius)
                max = Vec2(min.x + self.radius, min.y + self.radius)
                center = min + Vec2(self.radius / 2, self.radius / 2)

                walkable = self.world.is_colliding(Rectangle(min, max)) == False
                cell = Cell(center, walkable)
                line.append(cell)
            grid.append(line)

        return grid
    
    def update_collisions(self):
        for line in self.grid:
            for cell in line:
                ...

    # def cell_from_position(position: Vec2) -> tuple[int, int]:
    #     ...
