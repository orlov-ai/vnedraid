---
sidebar_position: 0
---

# API Overview

## Основные модули

Проект `jsonl2html` предоставляет простой и эффективный API для конвертации JSONL файлов в HTML.

### Публичный API

#### `convert_jsonl_to_html()`
Основная функция для конвертации, доступная через импорт пакета:

```python
from jsonl2html import convert_jsonl_to_html

convert_jsonl_to_html(
    fn_input="data.jsonl",
    index_column="auto",
    fn_output="auto",
    additional_table_content={}
)
```

### Внутренние модули

- **[convert.py](./convert)** - Основной модуль конвертации
- **[create_table_of_content.py](./create-table-of-content)** - Анализ и генерация оглавления

## Быстрый старт

### Минимальный пример

```python
from jsonl2html import convert_jsonl_to_html

# Простейшее использование
convert_jsonl_to_html("input.jsonl")
# Создаст файл input.html
```

### Полный пример с параметрами

```python
from jsonl2html import convert_jsonl_to_html

convert_jsonl_to_html(
    fn_input="data/export.jsonl",
    index_column="id",
    fn_output="reports/analysis.html",
    additional_table_content={
        "generated_by": "jsonl2html",
        "date": "2024-01-01",
        "source": "api_export"
    }
)
```

## CLI интерфейс

После установки пакета доступна консольная команда:

```bash
# Базовое использование
jsonl2html data.jsonl

# С параметрами
jsonl2html data.jsonl --index_column=user_id --fn_output=report.html
```

## Особенности API

1. **Автоматические имена файлов**: При `fn_output="auto"` имя генерируется из входного файла
2. **Умная индексация**: `index_column="auto"` автоматически выбирает подходящую колонку
3. **Самодостаточный HTML**: Результат не требует внешних файлов
4. **Unicode анализ**: Встроенная аналитика символов и блоков Unicode
