import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from matplotlib.patches import Circle, Polygon, Rectangle
import numpy as np
import random
import os

from geometry.point import Point
from geometry.utils import pt_in_tri
from triangulation.delaunay_triangulation import DelaunayTriangulation
from triangulation.utils import trailing_zeros, get_insertion_order


class DensificationApp:
    """Интерактивное приложение для визуализации послойного сгущения триангуляции.

    Attributes:
        fig (plt.Figure): Объект фигуры Matplotlib.
        ax (plt.Axes): Объект осей для отрисовки.
        triangulation (DelaunayTriangulation): Ядро триангуляции.
        unprocessed_points (list): Точки, ожидающие добавления.
        queue (list): Очередь точек в текущем порядке вставки.
        processed_cells (dict): Словарь обработанных ячеек сетки и их порядковые номера.
        _hover_patch (Polygon): Полигон подсветки треугольника при наведении.
        _hover_circle (Circle): Описанная окружность подсвеченного треугольника.
    """

    def __init__(self):
        """Инициализирует интерфейс, виджеты и запускает приложение."""
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.25)

        self.ax.set_xlim(0, 800)
        self.ax.set_ylim(600, 0)
        self.ax.set_aspect('equal', adjustable='box')

        self._init_widgets()

        self.triangulation = DelaunayTriangulation(800, 600)
        self.unprocessed_points: list = []
        self.queue: list = []
        self.processed_cells: dict = {}
        self.step_counter = 1
        self.is_playing = False
        self.show_circumcircles = False
        self.grid_params = None

        self.u = 4
        self.v = 2

        self.timer = self.fig.canvas.new_timer(interval=50)
        self.timer.add_callback(self.make_step)

        # Hover и статистика
        self._hover_patch = None
        self._hover_circle = None

        self.info_text = self.fig.text(
            0.98, 0.97, "", va="top", ha="right",
            fontsize=9, color="black", fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.4",
                      fc="white", ec="gray", alpha=0.85)
        )

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def _init_widgets(self):
        """Инициализирует и размещает виджеты управления в нижней панели."""
        ax_step = plt.axes([0.05, 0.05, 0.08, 0.06])
        ax_play = plt.axes([0.14, 0.05, 0.08, 0.06])
        ax_reset = plt.axes([0.23, 0.05, 0.08, 0.06])
        ax_rand = plt.axes([0.35, 0.05, 0.12, 0.06])
        ax_gen = plt.axes([0.48, 0.05, 0.12, 0.06])
        ax_load = plt.axes([0.61, 0.05, 0.12, 0.06])
        ax_circ = plt.axes([0.78, 0.05, 0.17, 0.06])
        ax_speed = plt.axes([0.25, 0.15, 0.50, 0.03])

        self.btn_step = Button(ax_step, 'Шаг')
        self.btn_play = Button(ax_play, 'Старт')
        self.btn_reset = Button(ax_reset, 'Сбросить')
        self.btn_rand = Button(ax_rand, 'Случайные')
        self.btn_gen = Button(ax_gen, 'Создать файл')
        self.btn_load = Button(ax_load, 'Загрузить файл')
        self.btn_circ = Button(ax_circ, 'Окружности')
        self.speed_slider = Slider(
            ax_speed, 'Скорость (мс)', 10, 500, valinit=50, valstep=10)

        self.btn_step.on_clicked(self.make_step)
        self.btn_play.on_clicked(self.toggle_play)
        self.btn_reset.on_clicked(self.reset)
        self.btn_rand.on_clicked(self.gen_random)
        self.btn_gen.on_clicked(self.generate_sample_file)
        self.btn_load.on_clicked(self.load_from_file)
        self.btn_circ.on_clicked(self.toggle_circumcircles)
        self.speed_slider.on_changed(self.update_speed)

    def update_speed(self, val):
        """Обновляет интервал таймера автопроигрывания."""
        self.timer.interval = self.speed_slider.val

    def reset(self, event=None):
        """Сбрасывает триангуляцию и состояние приложения к начальному."""
        self.is_playing = False
        self.timer.stop()
        self.btn_play.label.set_text('Старт')
        self.triangulation = DelaunayTriangulation(800, 600)
        self.unprocessed_points = []
        self.queue = []
        self.processed_cells = {}
        self.step_counter = 1
        self.show_circumcircles = False
        self.grid_params = None
        self._hover_patch = None
        self._hover_circle = None
        self.ax.clear()
        self.ax.set_xlim(0, 800)
        self.ax.set_ylim(600, 0)
        self.info_text.set_text("")
        self.fig.canvas.draw_idle()

    def on_click(self, event):
        """Обработчик клика по холсту. Добавляет точку по координатам клика."""
        if event.inaxes != self.ax or event.ydata is None:
            return
        if event.xdata < 0 or event.xdata > 800 or event.ydata < 0 or event.ydata > 600:
            return
        p = Point(event.xdata, event.ydata, self.triangulation.pid_counter)
        self.triangulation.pid_counter += 1
        self.unprocessed_points.append(p)
        self.rebuild_queue()
        self.redraw()

    def gen_random(self, event=None):
        """Генерирует 150 случайных точек и запускает перестроение."""
        self.reset()
        for _ in range(150):
            x = random.uniform(10, 790)
            y = random.uniform(10, 590)
            p = Point(x, y, self.triangulation.pid_counter)
            self.triangulation.pid_counter += 1
            self.unprocessed_points.append(p)
        self.rebuild_queue()
        self.redraw()

    def generate_sample_file(self, event=None):
        """Создает текстовый файл со случайными точками, равномерно распределенными по сетке."""
        fname = "sample_points.txt"
        with open(fname, "w") as f:
            for cx in range(9):
                for cy in range(5):
                    x_min_cell = cx * (800 / 9)
                    x_max_cell = (cx + 1) * (800 / 9)
                    y_min_cell = cy * (600 / 5)
                    y_max_cell = (cy + 1) * (600 / 5)
                    x = random.uniform(x_min_cell + 5, x_max_cell - 5)
                    y = random.uniform(y_min_cell + 5, y_max_cell - 5)
                    f.write(f"{x:.2f} {y:.2f}\n")
        print(f"Файл {fname} создан в директории: {os.getcwd()}")

    def load_from_file(self, event=None):
        """Загружает точки из текстового файла. Если файла нет - генерирует его."""
        fname = "sample_points.txt"
        if not os.path.exists(fname):
            self.generate_sample_file()
        self.reset()
        with open(fname, 'r') as f:
            for line in f:
                x, y = map(float, line.split())
                p = Point(x, y, self.triangulation.pid_counter)
                self.triangulation.pid_counter += 1
                self.unprocessed_points.append(p)
        self.rebuild_queue()
        self.redraw()

    def rebuild_queue(self):
        """Перестраивает очередь добавления точек на основе иерархии сетки."""
        if not self.unprocessed_points:
            self.queue = []
            return

        xmin, xmax = 0, 800
        ymin, ymax = 0, 600

        dx = xmax / (2*self.u + 1)
        dy = ymax / (2*self.v + 1)
        self.grid_params = (xmin, xmax, ymin, ymax, dx, dy)

        points_in_cells = {}
        for p in self.unprocessed_points:
            cx = int(p.x / dx)
            cy = int(p.y / dy)
            cx = max(0, min(cx, 2*self.u))
            cy = max(0, min(cy, 2*self.v))

            p.cx = cx
            p.cy = cy
            zx = trailing_zeros(cx)
            zy = trailing_zeros(cy)
            p.layer = min(zx, zy, self.u, self.v)
            points_in_cells.setdefault((cx, cy), []).append(p)

        master_order = get_insertion_order(self.u, self.v)
        self.queue = []
        for cx, cy in master_order:
            if (cx, cy) in points_in_cells:
                for p in points_in_cells[(cx, cy)]:
                    self.queue.append(p)

    def toggle_play(self, event=None):
        """Включает/выключает автоматическое проигрывание шагов."""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.label.set_text('Пауза')
            self.timer.start()
        else:
            self.btn_play.label.set_text('Старт')
            self.timer.stop()

    def make_step(self, event=None):
        """Выполняет один шаг алгоритма: извлекает точку из очереди и вставляет в триангуляцию."""
        if not self.queue:
            if self.is_playing:
                self.toggle_play()
            return
        p = self.queue.pop(0)
        self.unprocessed_points.remove(p)
        self.triangulation.insert_point(p)

        cell = (p.cx, p.cy)
        if cell not in self.processed_cells:
            self.processed_cells[cell] = self.step_counter
            self.step_counter += 1
        self.redraw()

    def toggle_circumcircles(self, event):
        """Переключает режим отображения описанных окружностей для всех треугольников."""
        self.show_circumcircles = not self.show_circumcircles
        self.redraw()

    def _on_motion(self, event):
        """Обработчик движения мыши. Обеспечивает hover-эффект треугольника и его окружности."""
        if event.inaxes is not self.ax or event.ydata is None:
            if self._hover_patch or self._hover_circle:
                if self._hover_patch:
                    self._hover_patch.remove()
                    self._hover_patch = None
                if self._hover_circle:
                    self._hover_circle.remove()
                    self._hover_circle = None
                self.fig.canvas.draw_idle()
            return

        px, py = event.xdata, event.ydata
        found_tri = None

        for tri in self.triangulation.triangles:
            if not tri.has_super_vertex():
                p1, p2, p3 = tri.points
                if pt_in_tri(px, py, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y):
                    found_tri = tri
                    break

        if self._hover_patch:
            self._hover_patch.remove()
            self._hover_patch = None
        if self._hover_circle:
            self._hover_circle.remove()
            self._hover_circle = None

        if found_tri:
            p1, p2, p3 = found_tri.points
            verts = [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)]

            patch = Polygon(verts, closed=True,
                            facecolor="#14970854", edgecolor="#34f722",
                            linewidth=2, zorder=10)
            self.ax.add_patch(patch)
            self._hover_patch = patch

            if found_tri.cc_r < 1000:
                circle = Circle((found_tri.cc_x, found_tri.cc_y), found_tri.cc_r,
                                fill=False, edgecolor='#ff0000',
                                linewidth=1.5, linestyle='--', zorder=10)
                self.ax.add_patch(circle)
                self._hover_circle = circle

        self.fig.canvas.draw_idle()

    def redraw(self):
        """Полная перерисовка холста: сетка, треугольники, точки, статистика."""
        self._hover_patch = None
        self._hover_circle = None

        self.ax.clear()
        self.ax.set_xlim(0, 800)
        self.ax.set_ylim(600, 0)

        if self.grid_params:
            xmin, xmax, ymin, ymax, dx, dy = self.grid_params
            for (cx, cy), step_num in self.processed_cells.items():
                rect = Rectangle((xmin + cx*dx, ymin + cy*dy), dx, dy,
                                 facecolor='lightgray', edgecolor='gray', alpha=0.5, zorder=1)
                self.ax.add_patch(rect)
                self.ax.text(xmin + cx*dx + dx/2, ymin + cy*dy + dy/2, str(step_num),
                             ha='center', va='center', color='black', fontsize=8, zorder=2)

            for i in range(2*self.u + 2):
                self.ax.axvline(xmin + i*dx, color='lightgray',
                                linestyle='--', linewidth=0.5, zorder=0)
            for i in range(2*self.v + 2):
                self.ax.axhline(ymin + i*dy, color='lightgray',
                                linestyle='--', linewidth=0.5, zorder=0)

        cmap = plt.cm.plasma
        max_layer = max(
            (p.layer for p in self.triangulation.points if p.id >= 0), default=1)

        for tri in self.triangulation.triangles:
            if not tri.has_super_vertex():
                layer = max(p.layer for p in tri.points)
                color = cmap(layer / max(max_layer, 1))
                verts = [[p.x, p.y] for p in tri.points]
                poly = Polygon(verts, closed=True, facecolor=color,
                               edgecolor='black', alpha=0.4, linewidth=1, zorder=3)
                self.ax.add_patch(poly)
            else:
                real_pts = [p for p in tri.points if p.id >= 0]
                if len(real_pts) == 2:
                    self.ax.plot([real_pts[0].x, real_pts[1].x], [real_pts[0].y, real_pts[1].y],
                                 color='black', linewidth=1.5, zorder=3)

        if self.queue:
            qx = [p.x for p in self.queue]
            qy = [p.y for p in self.queue]
            self.ax.scatter(qx, qy, color='gray', s=15, zorder=4)

        proc_pts = [p for p in self.triangulation.points if p.id >= 0]
        if proc_pts:
            p_x = [p.x for p in proc_pts]
            p_y = [p.y for p in proc_pts]
            p_layers = [p.layer for p in proc_pts]
            self.ax.scatter(p_x, p_y, c=p_layers, cmap=cmap, edgecolors='black',
                            s=30, zorder=5, vmin=0, vmax=max(max_layer, 1))

        if self.show_circumcircles:
            for tri in self.triangulation.triangles:
                if not tri.has_super_vertex() and tri.cc_r < 1000:
                    circle = Circle((tri.cc_x, tri.cc_y), tri.cc_r, fill=False,
                                    edgecolor='purple', linestyle='--', linewidth=1, zorder=6)
                    self.ax.add_patch(circle)

        self.ax.set_title(f"Послойное сгущение (В очереди: {len(self.queue)})")

        n_proc = len(proc_pts)
        n_tri = len(
            [t for t in self.triangulation.triangles if not t.has_super_vertex()])

        stats = (
            f"В очереди  : {len(self.queue)}\n"
            f"Вставлено  : {n_proc}\n"
            f"Треуг.     : {n_tri}\n"
            f"Ячеек готов: {len(self.processed_cells)}"
        )
        self.info_text.set_text(stats)

        self.fig.canvas.draw_idle()

    def run(self):
        """Запускает главный цикл приложения Matplotlib."""
        plt.show()
