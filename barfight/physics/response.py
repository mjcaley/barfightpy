from dataclasses import dataclass

from .body import Body


@dataclass
class Arbiter:
    first_body: Body
    second_body: Body
    is_first_collision: bool = False
