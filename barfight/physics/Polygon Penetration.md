For polygon collision detection and penetration vector calculation, you'll typically want to use the Separating Axis Theorem (SAT). Here's how you can implement the penetration calculations for different shapes against a polygon:

from dataclasses import dataclass
from typing import Generator, Optional

@dataclass
class Polygon:
    # ... (your existing code) ...

    @collision.register
    def _collision_polygon(self, other: 'Polygon') -> bool:
        # Check bounding box first for early exit
        if not self.bounding_box.collision(other.bounding_box):
            return False
        
        # Check all axes of both polygons
        return not any(self._has_separating_axis(axis, other) 
                      for axis in chain(self.axes(), other.axes()))

    @penetration.register
    def _penetration_polygon(self, other: 'Polygon') -> Optional[Vec2]:
        if not self.collision(other):
            return None

        min_penetration = float('inf')
        min_axis = None

        # Check axes from both polygons
        for axis in chain(self.axes(), other.axes()):
            penetration = self._get_penetration_depth(axis, other)
            if penetration < min_penetration:
                min_penetration = penetration
                min_axis = axis

        return min_axis * min_penetration if min_axis else None

    @penetration.register
    def _penetration_circle(self, circle: Circle) -> Optional[Vec2]:
        # Convert circle to polygon approximation for simplicity
        # Or implement specific circle-polygon collision
        closest_point = self._get_closest_point_to_circle(circle)
        if closest_point:
            to_circle = circle.center - closest_point
            distance = to_circle.length()
            if distance < circle.radius:
                return to_circle.normalize() * (circle.radius - distance)
        return None

    @penetration.register
    def _penetration_rectangle(self, rect: Rectangle) -> Optional[Vec2]:
        # Convert rectangle to polygon and use polygon-polygon penetration
        rect_points = [
            rect.position,
            rect.position + Vec2(rect.size.x, 0),
            rect.position + rect.size,
            rect.position + Vec2(0, rect.size.y)
        ]
        rect_poly = Polygon(rect_points)
        return self._penetration_polygon(rect_poly)

    def _project(self, axis: Vec2) -> tuple[float, float]:
        """Project polygon onto an axis."""
        dots = [vertex.dot(axis) for vertex in self.vertices()]
        return min(dots), max(dots)

    def _has_separating_axis(self, axis: Vec2, other: 'Polygon') -> bool:
        """Check if there's a separation along the given axis."""
        p1_min, p1_max = self._project(axis)
        p2_min, p2_max = other._project(axis)
        return p1_max < p2_min or p2_max < p1_min

    def _get_penetration_depth(self, axis: Vec2, other: 'Polygon') -> float:
        """Calculate penetration depth along an axis."""
        p1_min, p1_max = self._project(axis)
        p2_min, p2_max = other._project(axis)
        return min(p1_max - p2_min, p2_max - p1_min)

    def _get_closest_point_to_circle(self, circle: Circle) -> Optional[Vec2]:
        """Find the closest point on the polygon to a circle's center."""
        closest_point = None
        min_distance = float('inf')

        # Check vertices
        for vertex in self.vertices():
            dist = (vertex - circle.center).length_squared()
            if dist < min_distance:
                min_distance = dist
                closest_point = vertex

        # Check edges
        for edge in self.edges():
            point = edge.closest_point(circle.center)
            dist = (point - circle.center).length_squared()
            if dist < min_distance:
                min_distance = dist
                closest_point = point

        return closest_point

For the OrientedRectangle, you would convert it to a Polygon similarly to the Rectangle case, but applying the rotation transformation to the points.

The key points in this implementation:

For Polygon-Polygon collision:

Use SAT to find the minimum penetration vector
Check axes from both polygons
Return the shortest penetration vector
For Circle-Polygon collision:

Find the closest point on the polygon to the circle
Calculate penetration based on that point and the circle's radius
For Rectangle-Polygon collision:

Convert the rectangle to a polygon
Use polygon-polygon collision detection
For OrientedRectangle-Polygon collision:

Convert the oriented rectangle to a polygon with rotated points
Use polygon-polygon collision detection
You might want to add additional optimizations like:

Caching the axes for static polygons
Using spatial partitioning for better performance with many objects
Adding early-out checks using bounding boxes
Also, you might want to add support for concave polygons by decomposing them into convex polygons first, as this implementation assumes convex polygons.