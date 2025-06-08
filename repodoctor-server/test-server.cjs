#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 Тестирование RepoDoctor MCP Server...\n');

// Проверка Node.js версии
const nodeVersion = process.version;
console.log(`📦 Node.js версия: ${nodeVersion}`);

const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
if (majorVersion < 18) {
    console.error('❌ Требуется Node.js версии 18 или выше');
    process.exit(1);
}
console.log('✅ Node.js версия подходит\n');

// Проверка файлов
const requiredFiles = [
    'build/index.js',
    'package.json',
    'tsconfig.json'
];

console.log('📁 Проверка файлов:');
for (const file of requiredFiles) {
    try {
        require('fs').accessSync(path.join(__dirname, file));
        console.log(`✅ ${file}`);
    } catch (err) {
        console.log(`❌ ${file} - не найден`);
        process.exit(1);
    }
}
console.log();

// Тестирование запуска сервера
console.log('🚀 Тестирование запуска сервера...');
const serverPath = path.join(__dirname, 'build', 'index.js');

const child = spawn('node', [serverPath], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
});

let output = '';
let errorOutput = '';

child.stdout.on('data', (data) => {
    output += data.toString();
});

child.stderr.on('data', (data) => {
    errorOutput += data.toString();
});

// Завершаем процесс через 3 секунды
setTimeout(() => {
    child.kill('SIGTERM');
}, 3000);

child.on('close', (code, signal) => {
    if (signal === 'SIGTERM') {
        console.log('✅ Сервер запустился успешно (завершён принудительно)');
    } else if (code === 0) {
        console.log('✅ Сервер завершился корректно');
    } else {
        console.log(`❌ Сервер завершился с кодом ${code}`);
    }
    
    if (output) {
        console.log('\n📝 Вывод сервера:');
        console.log(output);
    }
    
    if (errorOutput) {
        console.log('\n⚠️ Ошибки:');
        console.log(errorOutput);
    }
    
    console.log('\n🎉 Тестирование завершено!');
    console.log('\n📖 Следующие шаги:');
    console.log('1. Откройте Cline');
    console.log('2. Перейдите в настройки (⚙️)');
    console.log('3. Выберите "MCP Servers"');
    console.log('4. Добавьте новый сервер:');
    console.log(`   Name: repodoctor`);
    console.log(`   Command: node`);
    console.log(`   Args: ${serverPath}`);
    console.log(`   Working Directory: ${__dirname}`);
    console.log('5. Перезапустите Cline');
    console.log('6. Попробуйте спросить: "Какие проекты доступны для поиска?"');
});

child.on('error', (err) => {
    console.log(`❌ Ошибка запуска: ${err.message}`);
    process.exit(1);
});
