from typing import List, Tuple

from geometry.triangle import Triangle
from geometry.point import Point


class DelaunayTriangulation:
    """Класс для построения триангуляции Делоне методом Бойера-Ватсона.

    Attributes:
        triangles (List[Triangle]): Текущий список треугольников.
        points (List[Point]): Список добавленных реальных точек.
        pid_counter (int): Счетчик для выдачи уникальных id точкам.
        width (float): Ширина рабочей области.
        height (float): Высота рабочей области.
    """

    def __init__(self, width: float, height: float):
        """Инициализирует триангуляцию с супер-треугольником.

        Args:
            width: Ширина рабочей области.
            height: Высота рабочей области.
        """
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []
        self.pid_counter = 0
        self.width = width
        self.height = height

        margin = max(width, height)
        p1 = Point(-margin, -margin, -1)
        p2 = Point(width + margin, -margin, -2)
        p3 = Point(width / 2, height + margin, -3)
        self.triangles.append(Triangle(p1, p2, p3))

    def insert_point(self, p: Point):
        """Вставляет точку в текущую триангуляцию.

        Выполняет алгоритм Бойера-Ватсона: находит плохие треугольники,
        формирует многоугольник пустоты и перестраивает триангуляцию.

        Args:
            p: Точка для добавления.
        """
        self.points.append(p)
        bad_triangles = [
            tri for tri in self.triangles if tri.contains_point_in_circircumcircle(p)]

        polygon: List[Tuple[Point, Point]] = []
        for tri in bad_triangles:
            for i in range(3):
                edge = (tri.points[i], tri.points[(i + 1) % 3])
                shared = any(
                    edge[0] in other.points and edge[1] in other.points
                    for other in bad_triangles if other != tri
                )
                if not shared:
                    polygon.append(edge)

        for tri in bad_triangles:
            self.triangles.remove(tri)

        for edge in polygon:
            self.triangles.append(Triangle(edge[0], edge[1], p))
