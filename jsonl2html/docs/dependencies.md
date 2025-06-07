# Граф зависимостей проекта jsonl2html

## Обзор зависимостей

Данный файл содержит анализ зависимостей между файлами проекта.

## Зависимости по файлам

### ReadMe.md

*Нет внешних зависимостей*

### jsonl2html/__init__.py

**Импортирует:**
- `convert`

### jsonl2html/convert.py

**Импортирует:**
- `base64`
- `create_table_of_content`
- `fire`
- `json`
- `logging`
- `pathlib`
- `sys`
- `typing`

### jsonl2html/create_table_of_content.py

**Импортирует:**
- `json`
- `pandas`
- `typing`
- `unicode_stats.aggregation`
- `unicode_stats.block_rules`

### pyproject.toml

*Нет внешних зависимостей*

### requirements.txt

*Нет внешних зависимостей*

### tests/__init__.py

*Нет внешних зависимостей*

### tests/test_create_table_content.py

**Импортирует:**
- `json`
- `jsonl2html.create_table_of_content`
- `pandas`
- `pytest`
- `unittest.mock`

## Обратные зависимости

*Какие файлы используют данный модуль:*

### convert

**Используется в:**
- [jsonl2html/__init__.py](jsonl2html/__init__.py.md)

### sys

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)

### pathlib

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)

### json

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)
- [jsonl2html/create_table_of_content.py](jsonl2html/create_table_of_content.py.md)
- [tests/test_create_table_content.py](tests/test_create_table_content.py.md)

### fire

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)

### create_table_of_content

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)

### logging

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)

### base64

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)

### typing

**Используется в:**
- [jsonl2html/convert.py](jsonl2html/convert.py.md)
- [jsonl2html/create_table_of_content.py](jsonl2html/create_table_of_content.py.md)

### pandas

**Используется в:**
- [jsonl2html/create_table_of_content.py](jsonl2html/create_table_of_content.py.md)
- [tests/test_create_table_content.py](tests/test_create_table_content.py.md)

### unicode_stats.aggregation

**Используется в:**
- [jsonl2html/create_table_of_content.py](jsonl2html/create_table_of_content.py.md)

### unicode_stats.block_rules

**Используется в:**
- [jsonl2html/create_table_of_content.py](jsonl2html/create_table_of_content.py.md)

### unittest.mock

**Используется в:**
- [tests/test_create_table_content.py](tests/test_create_table_content.py.md)

### jsonl2html.create_table_of_content

**Используется в:**
- [tests/test_create_table_content.py](tests/test_create_table_content.py.md)

### pytest

**Используется в:**
- [tests/test_create_table_content.py](tests/test_create_table_content.py.md)

