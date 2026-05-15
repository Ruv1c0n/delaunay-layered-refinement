def pt_in_tri(px: float, py: float, x1: float, y1: float,
              x2: float, y2: float, x3: float, y3: float) -> bool:
    """Проверяет, находится ли точка внутри треугольника.

    Использует метод знаков векторного произведения (barycentric coordinate method).

    Args:
        px, py: Координаты проверяемой точки.
        x1, y1: Координаты первой вершины треугольника.
        x2, y2: Координаты второй вершины треугольника.
        x3, y3: Координаты третьей вершины треугольника.

    Returns:
        True, если точка лежит внутри или на границе треугольника, иначе False.
    """
    d1 = (px - x2) * (y1 - y2) - (x1 - x2) * (py - y2)
    d2 = (px - x3) * (y2 - y3) - (x2 - x3) * (py - y3)
    d3 = (px - x1) * (y3 - y1) - (x3 - x1) * (py - y1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)
