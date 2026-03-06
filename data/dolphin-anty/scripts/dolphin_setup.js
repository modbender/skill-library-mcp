/**
 * Dolphin Anty — настройка API-токена
 * 
 * Использование:
 *   node dolphin_setup.js --token <API_TOKEN>
 * 
 * Где взять токен:
 *   1. Откройте https://dolphin-anty.com/panel
 *   2. Войдите в аккаунт
 *   3. Перейдите в раздел API (левое меню)
 *   4. Нажмите "Generate token", задайте имя и срок действия
 *   5. Скопируйте токен (показывается ОДИН РАЗ!)
 *   6. Выполните: node dolphin_setup.js --token <полученный_токен>
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const TOKEN_FILE = path.join(__dirname, '..', '.token');
const { argv } = process;

function getArg(name) {
  const idx = argv.indexOf(name);
  if (idx !== -1 && idx + 1 < argv.length) return argv[idx + 1];
  return null;
}

function apiCall(method, url, body, headers) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const isHttps = u.protocol === 'https:';
    const transport = isHttps ? https : http;
    
    const opts = {
      hostname: u.hostname,
      port: u.port || (isHttps ? 443 : 80),
      path: u.pathname + u.search,
      method: method,
      headers: headers || {},
      timeout: 15000,
    };
    
    const req = transport.request(opts, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, data: data }); }
      });
    });
    
    req.on('error', (err) => reject(err));
    req.on('timeout', () => { req.destroy(); reject(new Error('Таймаут')); });
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function main() {
  const token = getArg('--token');
  
  if (!token) {
    console.log(`
╔════════════════════════════════════════════════════════╗
║          Настройка Dolphin Anty API-токена             ║
╚════════════════════════════════════════════════════════╝

Использование:
  node dolphin_setup.js --token <API_TOKEN>

Где взять токен:
  1. Откройте https://dolphin-anty.com/panel
  2. Войдите в аккаунт
  3. Перейдите в раздел «API» (левое меню)
  4. Нажмите «Generate token»
  5. Скопируйте токен (показывается ОДИН РАЗ!)
  6. Вставьте сюда: node dolphin_setup.js --token ваш_токен
    `);
    process.exit(1);
  }

  console.log('🔑 Проверяю токен...');

  // 1. Verify token against cloud API
  try {
    const res = await apiCall('GET', 'https://dolphin-anty-api.com/browser_profiles?limit=1', null, {
      'Authorization': 'Bearer ' + token,
    });
    
    if (res.data.success === false || res.status === 401) {
      console.error('❌ Токен невалидный! Проверьте, правильно ли скопировали.');
      console.error('   Ответ API:', JSON.stringify(res.data));
      process.exit(1);
    }
    
    const total = res.data.total || res.data.data?.length || 0;
    console.log(`✅ Токен валидный! Профилей в аккаунте: ${total}`);
  } catch (err) {
    console.error('⚠️ Не удалось проверить токен онлайн:', err.message);
    console.log('   Сохраняю токен и пробую локально...');
  }

  // 2. Save token to file
  fs.writeFileSync(TOKEN_FILE, token, 'utf8');
  console.log(`💾 Токен сохранён: ${TOKEN_FILE}`);

  // 3. Register token with local API
  try {
    const res = await apiCall('POST', 'http://localhost:3001/v1.0/auth/login-with-token', 
      { token: token },
      { 'Content-Type': 'application/json' }
    );
    
    if (res.data.success !== false) {
      console.log('✅ Локальный API авторизован!');
    } else {
      console.log('⚠️ Локальный API ответ:', JSON.stringify(res.data));
      console.log('   Убедитесь, что Dolphin Anty запущен.');
    }
  } catch (err) {
    console.log('⚠️ Dolphin Anty не запущен (localhost:3001 недоступен).');
    console.log('   Токен сохранён — при следующем запуске скриптов он будет использован.');
  }

  console.log('\n🎉 Готово! Теперь можно использовать:');
  console.log('   node dolphin_profiles.js list');
  console.log('   node dolphin_profiles.js status');
  console.log('   node dolphin_automate.js --profile-id <ID> --task warmup');
}

main();
