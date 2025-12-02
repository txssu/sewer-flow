# Переменные окружения

## Конфигурация ботов (одна из двух)

- `SF_BOTS_CONFIG_PATH` - путь к JSON-файлу конфига ([схема](#схема-configjson))
- `SF_B64_BOTS_CONFIG` - base64-закодированный JSON конфиг ([схема](#схема-configjson))

## Redis

- `SF_REDIS_HOST` (default: `localhost`)
- `SF_REDIS_PORT` (default: `6379`)
- `SF_REDIS_DB` (default: `0`)

## Схема config.json

```jsonc
{
  "bots": [
    {
      "app": "client1",        // название приложения/стрима
      "platform": "telegram",  // платформа: telegram, tamtam, max
      "token": "BOT_TOKEN"     // токен бота
    }
  ]
}
```
