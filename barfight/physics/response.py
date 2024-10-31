from dataclasses import dataclass

from .body import Body


@dataclass(frozen=True)
class Arbiter:
    first_body: Body
    second_body: Body
    is_first_collision: bool = False
