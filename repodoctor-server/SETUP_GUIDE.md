# Руководство по запуску RepoDoctor MCP Server

## Пошаговая инструкция

### 1. Проверьте установку Node.js
```bash
node --version
npm --version
```
Требуется Node.js версии 18 или выше.

### 2. Установите зависимости (уже выполнено)
```bash
cd /Users/alex/Documents/Cline/MCP/repodoctor-server
npm install
npm run build
```

### 3. Добавьте сервер в Cline

#### Способ 1: Через интерфейс Cline
1. Откройте Cline
2. Нажмите на иконку настроек (⚙️)
3. Выберите "MCP Servers"
4. Нажмите "Add Server"
5. Заполните поля:
   - **Name**: `repodoctor`
   - **Command**: `node`
   - **Args**: `/Users/alex/Documents/Cline/MCP/repodoctor-server/build/index.js`
   - **Working Directory**: `/Users/alex/Documents/Cline/MCP/repodoctor-server`

#### Способ 2: Через файл конфигурации
1. Найдите файл конфигурации Cline (обычно в `~/.config/cline/` или `~/Library/Application Support/cline/`)
2. Добавьте в секцию `mcpServers`:
```json
"repodoctor": {
  "command": "node",
  "args": ["/Users/alex/Documents/Cline/MCP/repodoctor-server/build/index.js"],
  "cwd": "/Users/alex/Documents/Cline/MCP/repodoctor-server"
}
```

### 4. Перезапустите Cline
После добавления сервера перезапустите Cline, чтобы изменения вступили в силу.

### 5. Проверьте подключение
После перезапуска Cline должен автоматически подключиться к MCP серверу. Вы увидите уведомление о подключении к серверу `repodoctor`.

## Тестирование

### Проверьте доступные проекты
Спросите у Cline:
```
Какие проекты доступны для поиска по документации?
```

### Выполните поиск
```
Найди информацию об анализаторе в проекте repodoctor
```

### Получите обзор проекта
```
Покажи обзор проекта poseidon
```

## Автоматический запуск (опционально)

Если хотите, чтобы сервер запускался автоматически при загрузке системы:

### На macOS (LaunchAgent)
1. Создайте файл `~/Library/LaunchAgents/repodoctor-mcp.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>repodoctor.mcp.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>node</string>
        <string>/Users/alex/Documents/Cline/MCP/repodoctor-server/build/index.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/alex/Documents/Cline/MCP/repodoctor-server</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

2. Загрузите service:
```bash
launchctl load ~/Library/LaunchAgents/repodoctor-mcp.plist
```

## Отладка

### Проверка запуска сервера
```bash
cd /Users/alex/Documents/Cline/MCP/repodoctor-server
node build/index.js
```
Сервер должен запуститься без ошибок.

### Проверка доступных проектов
Сервер автоматически сканирует директории:
- `/Users/alex/Projects/Внедрейд-2025/data`
- Текущую рабочую директорию
- Поддиректории `./data` и `./vnedraid`

### Логи
Cline показывает логи MCP серверов в консоли разработчика. Откройте Developer Tools (Cmd+Option+I) и проверьте консоль на наличие ошибок.

## Возможные проблемы

### "Command not found: node"
Установите Node.js с официального сайта nodejs.org

### "Permission denied"
```bash
chmod +x /Users/alex/Documents/Cline/MCP/repodoctor-server/build/index.js
```

### "No projects found"
Убедитесь, что у вас есть сгенерированная документация RepoDoctor в директориях с суффиксом `-docs-`

### Cline не видит сервер
1. Проверьте правильность пути к серверу
2. Убедитесь, что сервер компилируется без ошибок
3. Перезапустите Cline
4. Проверьте логи в Developer Tools

## Готово!

После выполнения этих шагов MCP сервер будет работать, и вы сможете задавать вопросы по документации прямо в Cline!
