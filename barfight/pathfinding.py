import heapq
from collections import defaultdict
from dataclasses import dataclass
from math import inf
from typing import Iterator

from pyglet.math import Vec2

from .constants import CHARACTER_LAYER
from .physics import PhysicsWorld, Rectangle


@dataclass(unsafe_hash=True)
class Cell:
    rectangle: Rectangle
    colliding: bool = False


class Grid:
    def __init__(self, world: PhysicsWorld, radius: float):
        self.world = world
        self.radius = radius
        self.grid: list[list[Cell]] = self.create_grid()
        self.update_collisions()

    def __getitem__(self, key):
        return self.grid[key]

    def create_grid(self) -> list[list[Cell]]:
        num_x_cells = int(
            (self.world.boundary.max.x - self.world.boundary.min.x) // (self.radius * 2)
        )
        num_y_cells = int(
            (self.world.boundary.max.y - self.world.boundary.min.y) // (self.radius * 2)
        )
        grid = []
        for x in range(num_x_cells):
            line = []
            for y in range(num_y_cells):
                rect = Rectangle(
                    Vec2(x * (self.radius * 2), y * (self.radius * 2)),
                    Vec2(
                        x * (self.radius * 2) + (self.radius * 2),
                        y * (self.radius * 2) + (self.radius * 2),
                    ),
                )
                cell = Cell(rect)
                line.append(cell)
            grid.append(line)

        return grid

    def update_collisions(self):
        for line in self.grid:
            for cell in line:
                cell.colliding = self.world.is_colliding_with(
                    cell.rectangle, CHARACTER_LAYER
                )

    def coord_from_position(self, position: Vec2) -> tuple[int, int]:
        x = int(position.x // (self.radius * 2))
        y = int(position.y // (self.radius * 2))

        return x, y

    def coord_from_cell(self, cell: Cell) -> tuple[int, int]:
        return self.coord_from_position(cell.rectangle.center)

    def cell_from_position(self, position: Vec2) -> Cell:
        x, y = self.coord_from_position(position)

        return self.grid[x][y]


class Pathfinding:
    def __init__(self, grid: Grid):
        self.grid = grid

    def neighbours(self, cell: Cell) -> Iterator[Cell]:
        x, y = self.grid.coord_from_cell(cell)
        for nx in range(max(0, x - 1), min(len(self.grid.grid), x + 2)):
            for ny in range(max(0, y - 1), min(len(self.grid[nx]), y + 2)):
                if nx == x and ny == y:
                    continue
                try:
                    cell = self.grid[nx][ny]
                    if not cell.colliding:
                        yield cell
                except IndexError:
                    continue

    def heuristic(self, cell: Cell, goal: Cell) -> float:
        return abs(cell.rectangle.center.x - goal.rectangle.center.x) + abs(
            cell.rectangle.center.y - goal.rectangle.center.y
        )

    def find_path(self, start: Vec2, end: Vec2) -> list[Cell] | None:
        start_cell = self.grid.cell_from_position(start)
        goal_cell = self.grid.cell_from_position(end)
        open_set: list[tuple[int, Cell]] = []
        heapq.heappush(open_set, (0, id(start_cell), start_cell))

        g_score = defaultdict(lambda: inf, {start_cell: 0.0})
        f_score = defaultdict(
            lambda: inf, {start_cell: self.heuristic(start_cell, goal_cell)}
        )

        came_from: dict[Cell, Cell] = {}

        while open_set:
            _, _, current = heapq.heappop(open_set)

            # Goal reached, reconstruct path
            if current == goal_cell:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_cell)
                return list(reversed(path))

            for neighbour in self.neighbours(current):
                cost = g_score[current] + 1
                if neighbour not in g_score:
                    came_from[neighbour] = current
                    g_score[neighbour] = cost
                    f_score[neighbour] = cost + self.heuristic(neighbour, goal_cell)

                    if all(neighbour != item[2] for item in open_set):
                        heapq.heappush(
                            open_set, (f_score[neighbour], id(neighbour), neighbour)
                        )

        return None
