# pyproject.toml

## Назначение

Файл `pyproject.toml` является стандартным файлом конфигурации для Python-проектов, определённым в PEP 518. Он используется для указания зависимостей сборочной системы, а также для хранения метаданных проекта (согласно PEP 621), таких как имя, версия, автор и зависимости времени выполнения. Этот файл позволяет создавать и распространять пакет с помощью стандартных инструментов, таких как `pip` и `build`.

## Основные компоненты

В данном конфигурационном файле используются следующие секции (таблицы TOML) для определения параметров проекта:

*   **`[build-system]`**: Определяет инструменты, необходимые для сборки пакета.
    *   `requires`: Список зависимостей, которые должны быть установлены в окружении для сборки проекта. В данном случае это `setuptools` и `wheel`.
    *   `build-backend`: Указывает на Python-объект, который инструменты сборки будут использовать для выполнения процесса сборки.

*   **`[project]`**: Содержит основные метаданные проекта, которые будут отображаться на PyPI и использоваться менеджерами пакетов.
    *   `name`: Имя пакета (`jsonl2html`).
    *   `version`: Текущая версия пакета (`0.2.0`).
    *   `description`: Краткое описание проекта.
    *   `readme`: Путь к файлу с подробным описанием проекта (`README.md`).
    *   `requires-python`: Минимально необходимая версия Python (`>=3.6`).
    *   `authors`: Список авторов проекта.
    *   `license`: Информация о лицензии проекта (MIT).
    *   `classifiers`: Список классификаторов для PyPI, помогающих пользователям находить проект.

*   **`[project.scripts]`**: Определяет точки входа для консольных скриптов. При установке пакета создаётся исполняемый файл.
    *   `jsonl2html = "jsonl2html.convert:main_bash_entry_point"`: Создаёт команду `jsonl2html`, которая при вызове исполняет функцию `main_bash_entry_point` из модуля `jsonl2html.convert`.

*   **`[project.urls]`**: Секция для указания полезных ссылок, связанных с проектом.
    *   `"Homepage"`: Ссылка на домашнюю страницу проекта на GitHub.
    *   `"Bug Tracker"`: Ссылка на систему отслеживания ошибок проекта.

*   **`[tool.setuptools]`**: Секция для конфигурации, специфичной для `setuptools`.
    *   `package-data`: Указывает, какие не-кодовые файлы должны быть включены в пакет. В данном случае это файл шаблона `html_template.html`.

*   **`[tool.setuptools.dynamic]`**: Позволяет `setuptools` получать метаданные из других файлов динамически.
    *   `dependencies`: Указывает, что зависимости времени выполнения должны быть загружены из файла `requirements.txt`.

## Зависимости

### Зависимости сборки

*   `setuptools>=42`: Набор инструментов для разработки и распространения пакетов Python.
*   `wheel`: Стандарт для формата бинарной дистрибуции Python-пакетов.

### Зависимости проекта (Runtime)

Загружаются из файла `requirements.txt`:

*   `fire==0.7.0`: Библиотека для автоматического создания интерфейсов командной строки (CLI) из любого Python-объекта. Используется для обработки аргументов командной строки для утилиты `jsonl2html`.
*   `tabulate==0.9.0`: Библиотека для создания и форматирования таблиц в различных форматах. Вероятно, используется для преобразования данных из JSONL в табличный вид перед генерацией HTML.

## Архитектурные решения

*   **Стандартизация по PEP 517/518/621**: Использование `pyproject.toml` для декларативного определения метаданных и зависимостей сборки является современным стандартом в экосистеме Python. Это отделяет конфигурацию сборки от исполняемого кода (`setup.py`).
*   **Разделение зависимостей**: Зависимости времени выполнения вынесены в отдельный файл `requirements.txt`. Это распространённый паттерн, который позволяет использовать один и тот же файл как для установки пакета, так и для настройки локального окружения разработки (`pip install -r requirements.txt`).
*   **Включение не-кодовых данных**: Проект включает в себя файл HTML-шаблона (`html_template.html`) как данные пакета. Это позволяет утилите использовать внутренний шаблон для генерации HTML-файлов, не завися от его наличия во внешней файловой системе.
*   **Точка входа (Entry Point)**: Проект определяет консольный скрипт `jsonl2html`, что делает его удобной утилитой командной строки для конечного пользователя.

## API/Интерфейсы

Данный файл определяет один публичный интерфейс — консольную команду.

*   **Команда**: `jsonl2html`
    *   **Сигнатура**: `jsonl2html [АРГУМЕНТЫ]`
    *   **Описание**: При установке пакета создаётся исполняемый файл `jsonl2html`, который является точкой входа в приложение. Он вызывает функцию `main_bash_entry_point` в модуле `jsonl2html.convert`. Аргументы, передаваемые в командной строке, обрабатываются библиотекой `fire`.

## Примеры использования

1.  **Сборка пакета из исходного кода:**
    ```bash
    # Установка сборочных зависимостей
    pip install build

    # Сборка пакета
    python -m build
    ```
    Эта команда создаст дистрибутивы (sdist и wheel) в директории `dist/`.

2.  **Установка пакета в окружение:**
    ```bash
    # Установка из локального каталога
    pip install .

    # Или установка из собранного wheel-файла
    pip install dist/jsonl2html-0.2.0-py3-none-any.whl
    ```

3.  **Использование утилиты после установки:**
    ```bash
    # Вызов утилиты из командной строки
    jsonl2html --input_file data.jsonl --output_file report.html
    ```
    (Примечание: конкретные флаги и аргументы зависят от реализации функции `main_bash_entry_point`).