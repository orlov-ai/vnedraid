# jsonl2html - Project Documentation

## Обзор проекта - общее назначение и функциональность

`jsonl2html` — это утилита и Python-пакет, предназначенный для преобразования файлов формата JSONL (JSON Lines) в единый, самодостаточный HTML-файл. Основная цель проекта — предоставить удобный интерактивный интерфейс для просмотра, навигации и анализа данных из JSONL-файлов непосредственно в браузере.

Ключевая функциональность включает:
*   **Конвертация JSONL в HTML**: Преобразование каждой строки JSON в структурированный и читаемый HTML-блок.
*   **Интерактивный просмотр**: Полученный HTML-файл позволяет легко перемещаться между записями.
*   **Анализ символов Unicode**: Утилита анализирует использование символов Unicode в исходном файле, генерирует статистику по блокам Unicode и выявляет "плохие" (нестандартные) символы.
*   **Генерация оглавления**: На основе анализа создается сводное оглавление в формате Markdown, которое встраивается в итоговый HTML-документ для быстрой навигации по статистическим данным.

Проект может использоваться как утилита командной строки для быстрой конвертации файлов, так и в качестве библиотеки в других Python-проектах.

## Архитектура - структура проекта и основные компоненты

Проект `jsonl2html` организован как стандартный Python-пакет с четким разделением логики, тестов и конфигурации.

*   **Исходный код (`jsonl2html/`)**: Основная директория, содержащая всю логику приложения.
    *   `convert.py`: Ядро утилиты, отвечающее за процесс конвертации.
    *   `create_table_of_content.py`: Модуль для анализа данных и генерации оглавления.
    *   `__init__.py`: Точка входа в пакет, определяющая публичный API и версию.
*   **Тесты (`tests/`)**: Директория с модульными тестами для проверки корректности работы ключевых функций. Используется `pytest` для запуска тестов.
*   **Конфигурационные файлы**:
    *   `pyproject.toml`: Стандартный файл для конфигурации сборки проекта и управления метаданными (имя, версия, зависимости).
    *   `requirements.txt`: Список внешних Python-зависимостей для установки через `pip`.
*   **Документация**:
    *   `ReadMe.md`: Основной файл с описанием проекта, инструкциями по установке и использованию.

Процесс работы утилиты выглядит следующим образом:
1.  Скрипт `convert.py` читает входной JSONL-файл.
2.  Он передает данные в модуль `create_table_of_content.py` для сбора статистики по символам Unicode и генерации оглавления в Markdown.
3.  `convert.py` обрабатывает каждую JSON-строку, форматируя ее в HTML.
4.  Все сгенерированные компоненты (оглавление, HTML-представление данных, стили, скрипты) объединяются в один самодостаточный HTML-файл.

## Основные модули - описание ключевых частей

*   **`jsonl2html/convert.py`**
    *   **Назначение:** Основной модуль, выполняющий преобразование JSONL в HTML. Он управляет всем процессом: чтение файла, вызов модуля анализа, форматирование данных и запись итогового HTML-файла. Использует библиотеку `fire` для создания интерфейса командной строки. Определяет кастомное исключение `ExceptionFileInput` для обработки ошибок ввода.

*   **`jsonl2html/create_table_of_content.py`**
    *   **Назначение:** Специализированный модуль для анализа содержимого JSONL-файла. Его главная задача — собрать статистику по использованию символов Unicode, сгруппировать их по блокам, рассчитать метрики по некорректным символам и строкам и сгенерировать на основе этих данных оглавление в формате Markdown. Для обработки данных используется библиотека `pandas`.

*   **`jsonl2html/__init__.py`**
    *   **Назначение:** Инициализационный файл пакета. Он делает функцию `convert_jsonl_to_html` доступной для импорта напрямую из пакета (`from jsonl2html import convert_jsonl_to_html`) и определяет версию пакета (`__version__`).

*   **`tests/test_create_table_content.py`**
    *   **Назначение:** Модульные тесты для `create_table_of_content.py`. Проверяют корректность генерации ссылок, сбора статистики и формирования итогового оглавления, обеспечивая надежность работы аналитического компонента.

## Граф зависимостей - как модули связаны друг с другом

Модули проекта взаимодействуют друг с другом и с внешними библиотеками следующим образом:

*   **`jsonl2html/convert.py`** (основной конвертер)
    *   **Внутренние зависимости:**
        *   `create_table_of_content`: Используется для генерации оглавления.
    *   **Внешние зависимости:**
        *   `sys`, `pathlib`, `json`, `logging`, `base64`, `typing` (стандартная библиотека)
        *   `fire`: Для создания интерфейса командной строки.

*   **`jsonl2html/create_table_of_content.py`** (генератор оглавления)
    *   **Внешние зависимости:**
        *   `json`, `typing` (стандартная библиотека)
        *   `pandas`: Для анализа данных и вычисления статистики.
        *   `unicode_stats.aggregation`, `unicode_stats.block_rules`: Для работы со статистикой Unicode.

*   **`jsonl2html/__init__.py`** (точка входа пакета)
    *   **Внутренние зависимости:**
        *   `convert`: Импортирует основную функцию для предоставления ее в публичном API.

*   **`tests/test_create_table_content.py`** (модуль тестов)
    *   **Внутренние зависимости:**
        *   `jsonl2html.create_table_of_content`: Импортирует тестируемые функции.
    *   **Внешние зависимости:**
        *   `pytest`, `unittest.mock`: Для тестирования.
        *   `pandas`: Для создания тестовых данных.

## Точки входа - entry points и основные API

Проект предоставляет две основные точки входа:

1.  **Интерфейс командной строки (CLI)**
    *   **Описание:** Основной способ использования утилиты. Запускается через `convert.py`. Благодаря библиотеке `fire`, функции модуля становятся доступны как команды.
    *   **Пример вызова:**
        ```bash
        python -m jsonl2html.convert <path_to_input.jsonl> <path_to_output.html>
        ```

2.  **Программный интерфейс (API)**
    *   **Описание:** Проект можно использовать как библиотеку в других Python-приложениях. Основная функция `convert_jsonl_to_html` доступна для импорта.
    *   **Компонент:** `convert_jsonl_to_html` в `jsonl2html/__init__.py`.
    *   **Пример использования:**
        ```python
        from jsonl2html import convert_jsonl_to_html

        convert_jsonl_to_html('input.jsonl', 'output.html')
        ```

## Структура файлов - навигация по документации

*   `jsonl2html/__init__.py`: Определяет публичный API пакета и его версию.
*   `jsonl2html/convert.py`: Основной скрипт, преобразующий JSONL в самодостаточный HTML-файл.
*   `jsonl2html/create_table_of_content.py`: Модуль для анализа статистики по символам Unicode и генерации оглавления.
*   `tests/__init__.py`: Инициализационный файл, который помечает директорию `tests` как пакет Python.
*   `tests/test_create_table_content.py`: Модульные тесты для проверки корректности генерации оглавления.
*   `pyproject.toml`: Файл конфигурации для сборки проекта и управления метаданными согласно PEP 518 и PEP 621.
*   `requirements.txt`: Список внешних Python-библиотек, необходимых для работы проекта.
*   `ReadMe.md`: Основная документация проекта с описанием, инструкциями по установке и использованию.

## Структура документации

Документация организована по структуре исходного проекта. Каждый файл имеет соответствующую документацию:

├── [ReadMe.md](ReadMe.md.md)
├── **jsonl2html/**
│   ├── [__init__.py](jsonl2html/__init__.py.md)
│   ├── [convert.py](jsonl2html/convert.py.md)
│   └── [create_table_of_content.py](jsonl2html/create_table_of_content.py.md)
├── [pyproject.toml](pyproject.toml.md)
├── [requirements.txt](requirements.txt.md)
└── **tests/**
    ├── [__init__.py](tests/__init__.py.md)
    └── [test_create_table_content.py](tests/test_create_table_content.py.md)

## Граф зависимостей

Подробный анализ зависимостей между модулями доступен в файле [dependencies.md](dependencies.md).

## Навигация

- **Основные компоненты**: [__init__.py](jsonl2html/__init__.py.md), [__init__.py](tests/__init__.py.md)
- **Конфигурационные файлы**: [pyproject.toml](pyproject.toml.md)
- **Тестовые файлы**: [__init__.py](tests/__init__.py.md), [test_create_table_content.py](tests/test_create_table_content.py.md)

---

*Документация сгенерирована автоматически с помощью LLM анализа кода*
