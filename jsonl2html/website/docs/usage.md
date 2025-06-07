---
sidebar_position: 2
---

# Руководство по использованию

## Введение

`jsonl2html` — это утилита для преобразования файлов формата JSONL (JSON Lines) в интерактивный HTML-документ с встроенным анализом Unicode символов.

## Установка

### Из локального репозитория

```bash
# Клонирование и установка
git clone <repository-url>
cd jsonl2html
pip install .
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

## Основные способы использования

### 1. Командная строка (рекомендуется)

После установки доступна команда `jsonl2html`:

```bash
# Простейшая конвертация
jsonl2html data.jsonl
# Создаст файл data.html

# С дополнительными параметрами
jsonl2html data.jsonl --index_column=user_id
jsonl2html data.jsonl --fn_output=report.html
```

### 2. Python модуль

```bash
# Прямой вызов модуля
python -m jsonl2html.convert data.jsonl

# С параметрами
python -m jsonl2html.convert data.jsonl --index_column=id --fn_output=output.html
```

### 3. Программный интерфейс

```python
from jsonl2html import convert_jsonl_to_html

# Базовое использование
convert_jsonl_to_html("data.jsonl")

# Полная настройка
convert_jsonl_to_html(
    fn_input="examples/data.jsonl",
    index_column="user_id",
    fn_output="reports/analysis.html",
    additional_table_content={
        "generated_by": "jsonl2html v0.2.0",
        "source": "user_analytics",
        "date": "2024-01-01"
    }
)
```

## Параметры

### `fn_input` (обязательный)
- **Тип**: `str`
- **Описание**: Путь к входному JSONL файлу
- **Пример**: `"data/users.jsonl"`

### `index_column` (опциональный)
- **Тип**: `str`
- **По умолчанию**: `"auto"`
- **Описание**: Колонка для создания индекса навигации
- **Варианты**:
  - `"auto"` - автоматический выбор подходящей колонки
  - `"column_name"` - конкретное имя колонки
- **Пример**: `"user_id"`, `"timestamp"`

### `fn_output` (опциональный)
- **Тип**: `str`
- **По умолчанию**: `"auto"`
- **Описание**: Путь для сохранения HTML файла
- **Варианты**:
  - `"auto"` - генерируется из имени входного файла
  - `"path/file.html"` - конкретный путь
- **Пример**: `"reports/analysis.html"`

### `additional_table_content` (опциональный)
- **Тип**: `dict`
- **По умолчанию**: `{}`
- **Описание**: Дополнительные метаданные для включения в HTML
- **Пример**:
```python
{
    "generated_by": "Analytics Script",
    "date": "2024-01-01",
    "source": "API Export",
    "version": "1.0"
}
```

## Формат входных данных

### JSONL (JSON Lines)
Каждая строка должна содержать валидный JSON объект:

```jsonl
{"id": 1, "name": "Alice", "email": "alice@example.com"}
{"id": 2, "name": "Bob", "email": "bob@example.com"}
{"id": 3, "name": "Charlie", "email": "charlie@example.com"}
```

### Поддерживаемые типы данных
- Строки (strings)
- Числа (numbers)
- Булевы значения (booleans)
- Массивы (arrays)
- Вложенные объекты (nested objects)
- null значения

## Результат

### HTML файл содержит:
1. **Интерактивное оглавление** с навигацией
2. **Unicode статистику** по блокам символов
3. **Структурированное отображение** каждой JSON записи
4. **Встроенные стили** (самодостаточный файл)
5. **Анализ "плохих" символов** и проблемных строк

### Пример структуры вывода:
```
📊 Unicode Statistics
├── Basic Latin: 1,234 символов
├── Cyrillic: 567 символов
└── Punctuation: 89 символов

📄 Records (3 total)
├── Record 1: {"id": 1, "name": "Alice"}
├── Record 2: {"id": 2, "name": "Bob"}
└── Record 3: {"id": 3, "name": "Charlie"}
```

## Примеры использования

### Анализ логов API
```bash
jsonl2html api_logs.jsonl --index_column=timestamp
```

### Обработка пользовательских данных
```python
convert_jsonl_to_html(
    "users.jsonl",
    index_column="user_id",
    fn_output="user_report.html",
    additional_table_content={"report_type": "user_analysis"}
)
```

### Конвертация экспорта базы данных
```bash
jsonl2html db_export.jsonl --fn_output=database_view.html
```

## Устранение проблем

### Частые ошибки

**Файл не найден**
```
ExceptionFileInput: Input file not found
```
- Проверьте правильность пути к файлу
- Убедитесь, что файл существует

**Неверный формат JSON**
```
json.JSONDecodeError: Expecting ',' delimiter
```
- Проверьте, что каждая строка содержит валидный JSON
- Используйте JSON валидатор для проверки данных

**Проблемы с кодировкой**
- Убедитесь, что файл сохранён в UTF-8
- Проверьте корректность Unicode символов
