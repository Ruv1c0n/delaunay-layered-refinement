"""Главный модуль приложения.

Точка входа для запуска интерактивной визцализации
послойного сгущения триангуляции Делоне.
"""

from visualization.visualization import DensificationApp

if __name__ == "__main__":
    app = DensificationApp()
    app.run()
