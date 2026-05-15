from typing import List, Set, Tuple


def trailing_zeros(n: int) -> int:
    """Вычисляет количество конечных нулевых битов в числе (степень двойки).

    Args:
        n: Целое число.

    Returns:
        Количество нулей в конце двоичного представления. 
        Для 0 возвращает 60 (условно бесконечность).
    """
    if n == 0:
        return 60
    return (n & -n).bit_length() - 1


def get_insertion_order(u: int, v: int) -> List[Tuple[int, int]]:
    """Вычисляет строгий порядок вставки точек для послойного сгущения.

    Формирует змейковидный (boustrophedon) обход сетки от внутренних 
    ячеек к границам с учетом иерархических слоев.

    Args:
        u: Параметр сетки по оси X (определяет ширину W = 2u + 1).
        v: Параметр сетки по оси Y (определяет высоту H = 2v + 1).

    Returns:
        Список кортежей (cx, cy) - координат ячеек в порядке их обработки.
    """
    W = 2 * u + 1
    H = 2 * v + 1
    max_layer = min(u, v)
    order: List[Tuple[int, int]] = []
    added: Set[Tuple[int, int]] = set()

    for layer in range(max_layer, -1, -1):
        s = 1 << layer
        s2 = 1 << (layer + 1)

        xs = list(range(0, W, s))
        ys = list(range(0, H, s))

        int_xs = [x for x in xs if x % s2 != 0]
        int_ys = [y for y in ys if y % s2 != 0]

        xbound_xs = [x for x in xs if x % s2 == 0]
        xbound_ys = int_ys

        ybound_xs = int_xs
        ybound_ys = [y for y in ys if y % s2 == 0]

        # Внутренние точки
        for i, y in enumerate(reversed(int_ys)):
            row_x = int_xs if i % 2 == 0 else list(reversed(int_xs))
            for x in row_x:
                if (x, y) not in added:
                    order.append((x, y))
                    added.add((x, y))

        # Граница по X
        for i, x in enumerate(xbound_xs):
            col_y = xbound_ys if i % 2 == 0 else list(reversed(xbound_ys))
            for y in col_y:
                if (x, y) not in added:
                    order.append((x, y))
                    added.add((x, y))

        # Граница по Y
        for i, x in enumerate(reversed(ybound_xs)):
            col_y = list(reversed(ybound_ys)) if i % 2 == 0 else ybound_ys
            for y in col_y:
                if (x, y) not in added:
                    order.append((x, y))
                    added.add((x, y))

        # Угловые точки (пересечение границ)
        corner_xs = xbound_xs
        corner_ys = ybound_ys
        for i, x in enumerate(corner_xs):
            col_y = corner_ys if i % 2 == 0 else list(reversed(corner_ys))
            for y in col_y:
                if (x, y) not in added:
                    order.append((x, y))
                    added.add((x, y))

    return order
