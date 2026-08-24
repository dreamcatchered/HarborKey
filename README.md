<div align="center">

# ⚓ HarborKey

**TokenHarbor account auto-registration & free API key harvester**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![GitHub](https://img.shields.io/github/stars/dreamcatchered/HarborKey?style=flat&logo=github)

*Automatically creates accounts on [tokenharbor.ai](https://tokenharbor.ai), harvests free API keys, and verifies them against a free model.*

[English](#-english) · [Русский](#-русский)

</div>

---

<a name="-english"></a>

## English

### What is it?

HarborKey is a CLI tool that automates the entire lifecycle of getting a free API key from **TokenHarbor.ai**:

- Creates a temporary inbox
- Registers an account
- Creates an API key
- Confirms email verification
- Tests the free model endpoint
- *(Optional)* injects keys into [9router](https://9router.com)

### Features

| Feature | Description |
|---------|-------------|
| 🗝️ One-click key | Register a single account + test |
| 📦 Batch mode | Generate `N` accounts with one command |
| 🔍 Key testing | Validate all saved keys against the free model |
| 🔀 9router injection | Auto-add keys to 9router (optional) |
| 🔌 Proxy support | Optional proxy via env var |
| 🧹 Auto-cleanup | Removes site-generated default keys |

### Requirements

- Python 3.8+
- `requests` (installed via requirements)
- Internet access to `tokenharbor.ai`

### Installation

```bash
git clone https://github.com/dreamcatchered/HarborKey.git
cd HarborKey
pip install -r requirements.txt
```

### Usage

#### Interactive menu

```bash
python harborkey.py
```

```
  [1] Create 1 account (+ test + injection)
  [2] Create a batch (N accounts)
  [3] Test all API keys
  [4] List accounts & keys
  [5] Test 1 key (manual input)
  [6] Inject all into 9router
  [7] Show 9router entries
  [0] Exit
```

#### Command line

```bash
# Create 1 account
python harborkey.py 1

# Create 5 accounts
python harborkey.py batch 5

# Create 10 accounts with auto-injection into 9router
python harborkey.py batch 10 --inject

# Test all saved keys
python harborkey.py test

# List accounts
python harborkey.py list
```

> **Windows / PowerShell:** if you see garbled Cyrillic output, run:
> ```powershell
> $env:PYTHONIOENCODING='utf-8'; python harborkey.py
> ```

### Where keys are stored

| File | Contents |
|------|----------|
| `apikeys.txt` | Plain list of all API keys (one per line) |
| `accounts.json` | Full account records (email, password, key, status) |

### Proxy (optional)

If the site blocks requests, set the env var or create a `.env` file:

```
HARBORKEY_PROXY=http://user:pass@ip:port
```

### How a key is created

1. Generate a random temporary inbox (tempmail.lol, fallback to mail.tm)
2. Generate a random password
3. Submit the registration form at `tokenharbor.ai/login`
4. Remove the site's default keys
5. Create a new API key
6. Enable free-model consent
7. Wait for the verification email (up to 90 s) and click the link
8. Test the key against `mimo-v2.5:free`

~30–60 seconds per account.

### Important

- Keys unlock the **free** model `mimo-v2.5:free` (rolling 7-day allowance).
- Keys persist on disk across restarts.
- Read the full API reference in [API_DOCS.md](API_DOCS.md).

### License

[MIT](LICENSE) © dreamcatchered

---

<a name="русский"></a>

## Русский

### Что это?

**HarborKey** — CLI-инструмент, который автоматизирует создание аккаунта на **TokenHarbor.ai** и получение бесплатного API-ключа:

- Создаёт временную почту
- Регистрирует аккаунт
- Создаёт API-ключ
- Подтверждает почту
- Тестирует бесплатную модель
- *(Опционально)* внедряет ключи в [9router](https://9router.com)

### Возможности

| Функция | Описание |
|---------|----------|
| 🗝️ Один ключ | Создать аккаунт и проверить |
| 📦 Пакет | Создать `N` аккаунтов одной командой |
| 🔍 Тест ключей | Проверить все сохранённые ключи |
| 🔄 9router | Авто-внедрение ключей (опционально) |
| 🔌 Временная почта | tempmail.lol, запасной mail.tm |
| 🧹 Очистка | Удаляет лишние ключи сайта |

### Требования

- Python 3.8+
- `pip` (зависимости из requirements.txt)
- Доступ к интернету

### Установка

```bash
git clone https://github.com/dreamcatchered/HarborKey.git
cd HarborKey
pip install -r requirements.txt
```

### Запуск

#### Меню

```bash
python harborkey.py
```

#### Командная строка

```bash
python harborkey.py 1              # создать 1 аккаунт
python harborkey.py batch 5        # создать 5 аккаунтов
python harborkey.py batch 10 --inject   # 10 аккаунтов + 9router
python harborkey.py test           # проверить все ключи
python harborkey.py list           # список аккаунтов
```

> **Windows / PowerShell:** если видишь каракули вместо русского текста:
> ```powershell
> $env:PYTHONIOENCODING='utf-8'; python harborkey.py
> ```

### Где хранятся ключи

| Файл | Что внутри |
|------|------------|
| `apikeys.txt` | Список всех API-ключей (по одному в строке) |
| `accounts.json` | Полная информация об аккаунтах |

### Прокси (если нужно)

Через переменную окружения или файл `.env`:

```
HARBORKEY_PROXY=http://логин:пароль@ip:порт
```

### Как создаётся ключ

1. Генерируется случайная временная почта (tempmail.lol, запасная mail.tm)
2. Генерируется случайный пароль
3. Отправляется форма регистрации на `tokenharbor.ai/login`
4. Удаляются лишние ключи сайта
5. Создаётся API-ключ
6. Включается согласие на бесплатные модели
7. Ожидание письма с подтверждением (до 90 с) и переход по ссылке
8. Проверка ключа через `mimo-v2.5:free`

Примерно 30–60 секунд на один аккаунт.

### Документация API

Полная документация в [API_DOCS.md](API_DOCS.md).

### Лицензия

[MIT](LICENSE)