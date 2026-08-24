# TokenHarbor API — Полная документация

## API Endpoint

```
https://tokenharbor.ai/v1/chat/completions
```

Формат: OpenAI-совместимый (Chat Completions API)

Авторизация:
```
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

---

## Бесплатные модели (работают без баланса)

| Модель | Название | Tier | Tool Call | Stream | Prompt Cache |
|--------|----------|------|-----------|--------|--------------|
| `mimo-v2.5:free` | MiMo V2.5 (Xiaomi) | high | Да | Да | Да |
| `deepseek-v4-flash:free` | DeepSeek V4 Flash | low | Да | Да | Да |
| `qwen3.8-27b:free` | Qwen3.8 27B (Alibaba) | low | Да | Да | Да |

**Важно:** Free модели используют "rolling 7-day allowance" — лимит на 7 дней.
Когда лимит исчерпан, API вернёт rate-limit ошибку. Ключ не блокируется навсегда.

### th-orchestra (НЕ работает без баланса)
Несмотря на цену $0, требует баланс на аккаунте (403 "balance_zero").

---

## Платные модели (нужен баланс)

| Модель | Цена вход/выход ($/1M токенов) | Tier |
|--------|-------------------------------|------|
| `claude-opus-5` | $5 / $25 | high |
| `claude-sonnet-5` | $2 / $10 | mid |
| `claude-fable-5` | $10 / $50 | high |
| `grok-4.6` | $2 / $6 | frontier |
| `kimi-k3` | $3 / $15 | high |
| `glm-5.3` | $2.8 / $8.8 | frontier |
| `mimo-v2.5-pro` | $0.435 / $0.87 | high |
| `mimo-v2.5` | $0.14 / $0.28 | high |
| `deepseek-v4-pro` | $2.4 / $4.8 | high |
| `deepseek-v4-flash` | $0.44 / $1.32 | low |
| `qwen3.8-27b` | $0.35 / $2.1 | low |
| `qwen3.8-max` | $2 / $6 | high |
| `gpt-5.6-luna` | $0.2 / $1.2 | high |
| `gpt-5.6-sol` | $5 / $30 | high |
| `gpt-5.6-terra` | $2 / $12 | high |
| `gemini-3.7-flash` | $0.75 / $3.75 | mid |

---

## Примеры запросов

### 1. Простой запрос

```python
import requests

API_KEY = "thk_live_..."

r = requests.post("https://tokenharbor.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "mimo-v2.5:free",
        "messages": [{"role": "user", "content": "Привет!"}],
        "max_tokens": 200
    })
print(r.json()["choices"][0]["message"]["content"])
```

### 2. System prompt

```python
r = requests.post("https://tokenharbor.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "deepseek-v4-flash:free",
        "messages": [
            {"role": "system", "content": "Ты полезный ассистент. Отвечай на русском."},
            {"role": "user", "content": "Расскажи анекдот"}
        ],
        "max_tokens": 500
    })
```

### 3. Multi-turn (история диалога)

```python
r = requests.post("https://tokenharbor.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "qwen3.8-27b:free",
        "messages": [
            {"role": "user", "content": "Меня зовут Петя"},
            {"role": "assistant", "content": "Привет, Петя!"},
            {"role": "user", "content": "Как меня зовут?"}
        ],
        "max_tokens": 50
    })
```

### 4. Streaming

```python
r = requests.post("https://tokenharbor.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "mimo-v2.5:free",
        "messages": [{"role": "user", "content": "Напиши стих"}],
        "max_tokens": 500,
        "stream": True
    }, stream=True)

for line in r.iter_lines():
    if line:
        text = line.decode("utf-8")
        if text.startswith("data: ") and text != "data: [DONE]":
            import json
            chunk = json.loads(text[6:])
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                print(delta["content"], end="", flush=True)
```

### 5. Tool Call (Function Calling)

```python
r = requests.post("https://tokenharbor.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "mimo-v2.5:free",
        "messages": [{"role": "user", "content": "Какая погода в Москве?"}],
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Получить погоду в городе",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}}
                }
            }
        }],
        "max_tokens": 100
    })

tool_call = r.json()["choices"][0]["message"]["tool_calls"][0]
print(tool_call["function"]["name"])      # get_weather
print(tool_call["function"]["arguments"]) # {"city": "Moscow"}
```

---

## Примеры ответов

### Ответ mimo-v2.5:free

```json
{
  "id": "chatcmpl-1fc922827bf14db799d5d0a40caeb6d6",
  "object": "chat.completion",
  "created": 1787502976,
  "model": "mimo-v2.5",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Привет! Я MiMo — чат-бот, разработанный командой Xiaomi LLM Core Team, с окном контекста в 1 миллион токенов.",
      "reasoning_content": "The user is asking me to introduce myself..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 266,
    "completion_tokens": 68,
    "total_tokens": 334,
    "prompt_tokens_details": {"cached_tokens": 192},
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 192
  }
}
```

### Ответ deepseek-v4-flash:free

```json
{
  "id": "chatcmpl-f3202c1f769e463092e3dafb3fdd1179",
  "object": "chat.completion",
  "created": 1787503200,
  "model": "deepseek-v4-flash",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Привет! Я DeepSeek — последняя версия модели от компании DeepSeek, и я здесь, чтобы помочь тебе с любыми вопросами!",
      "reasoning_content": "The user asks in Russian..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 93,
    "total_tokens": 193
  }
}
```

### Ответ qwen3.8-27b:free

```json
{
  "id": "chatcmpl-a25b40ca79d245a88c3ac55d883cd0f3",
  "object": "chat.completion",
  "created": 1787503300,
  "model": "qwen3.8-27b",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Привет, я Qwen — большая языковая модель, разработанная лабораторией Tongyi Lab Alibaba Group.",
      "reasoning_content": "We need answer in Russian..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 64,
    "completion_tokens": 177,
    "total_tokens": 241
  }
}
```

### Ответ Tool Call

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "model": "mimo-v2.5",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_af15b4aa9f43419cab8637b5",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"city\": \"Moscow\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

### Streaming chunk

```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1787503400,"model":"mimo-v2.5","choices":[{"index":0,"delta":{"content":"Привет"},"finish_reason":null}]}
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1787503400,"model":"mimo-v2.5","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}
data: [DONE]
```

---

## Заголовки ответа (X-Th-*)

| Заголовок | Пример | Описание |
|-----------|--------|----------|
| `X-Th-Request-Id` | `chatcmpl-1fc92282...` | Уникальный ID запроса |
| `X-Th-Route-Decision` | `{"model":"mimo-v2.5","tier":"high","cache_hit":false}` | Маршрутизация |
| `X-Th-Steering-Applied` | `none` | Применённый steering |
| `X-Th-Upstream-Model` | `mimo-v2.5` | Фактическая upstream модель |

---

## Список моделей (endpoint)

```
GET https://tokenharbor.ai/v1/models
Authorization: Bearer <API_KEY>
```

Ответ:
```json
{
  "object": "list",
  "data": [
    {
      "id": "mimo-v2.5:free",
      "object": "model",
      "created": 1700000000,
      "owned_by": "xiaomi-mimo",
      "label": "MiMo V2.5 (Free)",
      "blurb": "Free-tier only — uses your rolling 7-day allowance...",
      "tier": "high",
      "pricing": {"input_usd_per_1m": 0, "output_usd_per_1m": 0},
      "supports_prompt_cache": true,
      "tool_call": true,
      "function_call": true
    }
  ]
}
```

---

## Лимиты и ограничения

### Free модели
- **Rolling 7-day allowance** — лимит токенов на 7 дней (точный лимит не указан в API)
- Когда лимит исчерпан: rate-limit ошибка (не 403 balance_zero)
- Ключ НЕ блокируется навсегда, лимит обновляется каждые 7 дней

### Rate limit по IP
- После ~10-20 быстрых запросов подряд IP временно блокируется (ConnectTimeout)
- Блокировка проходит через несколько минут
- Рекомендация: 5-10 запросов в минуту на один IP

### Rate limit по регистрации
- После ~3 быстрых регистраций появляется CAPTCHA
- Рекомендация: пауза 15-30 секунд между регистрациями

### Prompt Cache
- `mimo-v2.5:free`: 192 токенов системного промпта кэшируются автоматически
- `deepseek-v4-flash:free`: поддерживает prompt cache
- `qwen3.8-27b:free`: поддерживает prompt cache

---

## Ошибки

### 403 balance_zero
```json
{"error":{"message":"Your Token Harbor balance is at $0. Top up at https://tokenharbor.ai/dashboard to keep using paid models.","type":"balance_zero","code":"balance_zero"}}
```
Причина: попытка использовать платную модель без баланса.

### 404 model_not_found
```json
{"error":{"message":"Model 'gpt-4' is not available. Browse models at...","type":"model_not_found","code":"model_not_found"}}
```
Причина: модель не существует на платформе.

### 401 invalid_api_key
```json
{"error":{"message":"Invalid or revoked API key. Rotate your key at https://tokenharbor.ai/dashboard.","type":"invalid_api_key","code":"invalid_api_key"}}
```
Причина: ключ неверный или отозван.

---

## Особенности моделей

### mimo-v2.5:free
- Разработчик: Xiaomi LLM Core Team
- Контекст: 1,000,000 токенов
- Tier: high (приоритетная маршрутизация)
- Имеет `reasoning_content` в ответе (chain-of-thought)
- Prompt cache: 192 токенов кэшируются

### deepseek-v4-flash:free
- Разработчик: DeepSeek
- Tier: low
- Имеет `reasoning_content` в ответе
- Меньше prompt_tokens на тот же запрос (~100 vs ~266 у mimo)

### qwen3.8-27b:free
- Разработчик: Tongyi Lab, Alibaba Group
- Tier: low
- Имеет `reasoning_content` в ответе
- Самый компактный по prompt_tokens (~64 на простой запрос)

---

## Все ключи

См. файл `apikeys.txt` в корне проекта.
