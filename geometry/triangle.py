import math

from geometry.point import Point


class Triangle:
    """Класс, представляющий треугольник с вычисленной описанной окружностью.

    Attributes:
        points (List[Point]): Список из трех вершин треугольника.
        cc_x (float): Координата X центра описанной окружности.
        cc_y (float): Координата Y центра описанной окружности.
        cc_r (float): Радиус описанной окружности.
    """

    def __init__(self, p1: Point, p2: Point, p3: Point):
        """Инициализирует треугольник и вычисляет его описанную окружность.

        Args:
            p1: Первая вершина.
            p2: Вторая вершина.
            p3: Третья вершина.
        """
        self.points = [p1, p2, p3]
        self.cc_x = 0.0
        self.cc_y = 0.0
        self.cc_r = float('inf')
        self.calc_circumcircle()

    def calc_circumcircle(self):
        """Вычисляет центр и радиус описанной окружности вокруг треугольника.

        Использует аналитическую формулу на основе определителя.
        Если точки вырождены (лежат на одной прямой), радиус устанавливается как бесконечность.
        """
        p1, p2, p3 = self.points
        ax, ay = p1.x, p1.y
        bx, by = p2.x, p2.y
        cx, cy = p3.x, p3.y

        D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(D) < 1e-8:
            self.cc_x, self.cc_y, self.cc_r = 0, 0, float('inf')
        else:
            ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2)
                  * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / D
            uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2)
                  * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / D
            self.cc_x = ux
            self.cc_y = uy
            self.cc_r = math.hypot(ux - ax, uy - ay)

    def contains_point_in_circircumcircle(self, p: Point) -> bool:
        """Проверяет, лежит ли точка внутри описанной окружности треугольника.

        Args:
            p: Проверяемая точка.

        Returns:
            True, если точка лежит внутри (с учетом погрешности 1e-5), иначе False.
        """
        dist = math.hypot(p.x - self.cc_x, p.y - self.cc_y)
        return dist < self.cc_r + 1e-5

    def has_super_vertex(self) -> bool:
        """Проверяет, принадлежит ли треугольник супер-треугольнику (id < 0).

        Returns:
            True, если хотя бы одна вершина имеет отрицательный id, иначе False.
        """
        return any(p.id < 0 for p in self.points)
