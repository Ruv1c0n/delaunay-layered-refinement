# Delaunay Layered Refinement

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/UI-Matplotlib-11557C?logo=matplotlib&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Интерактивное приложение для визуализации **послойного сгущения триангуляции Делоне**: точки добавляются в триангуляцию в оптимальном порядке вставки, с подсветкой треугольников и их описанных окружностей при наведении.

## Структура

```
delaunay-layered-refinement/
├── geometry/                  # Точки, треугольники, геометрические утилиты
│   ├── point.py
│   ├── triangle.py
│   └── utils.py
├── triangulation/             # Ядро: триангуляция Делоне, порядок вставки
│   ├── delaunay_triangulation.py
│   └── utils.py
├── visualization/             # Интерактивное приложение (Matplotlib)
│   └── visualization.py
├── main.py                    # Точка входа
└── sample_points.txt          # Пример набора точек
```

## Запуск

```bash
pip install matplotlib numpy
python main.py
```

## Скриншоты

> TODO: добавить скриншоты интерфейса (главное окно с триангуляцией, подсветка треугольника и описанной окружности, очередь вставки точек).

## License

MIT
