#!/usr/bin/env python3
"""
HarborKey — TokenHarbor Auto-Register Bot.

Automatically creates accounts on tokenharbor.ai and harvests free API keys.
"""
import sys, os
if sys.stdout.encoding != 'utf-8':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    for f in (sys.stdout, sys.stderr):
        try:
            f.reconfigure(encoding='utf-8')
        except Exception:
            pass
import requests, re, json, random, string, uuid, urllib.parse, time, sqlite3
from datetime import datetime, timezone

BASE = "https://tokenharbor.ai"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
ACTION_ID = "6003703e71fc5dc99543154237e9a9267997419301"
ACTION_KEY = "kb59e6b88b9f36883e58e38e7e48870c6"
NEXT_ACTION = "607ec2c1a962aa81ad67a2483c54b0cfadfda875b2"
ROUTER = urllib.parse.quote('["",{"children":["login",{"children":["__PAGE__",{},null,null,0]},null,null,0]},null,null,20]')
DIR = os.path.dirname(os.path.abspath(__file__))
APIKEY_FILE = os.path.join(DIR, "apikeys.txt")
ACCOUNT_FILE = os.path.join(DIR, "accounts.json")
TEST_MODEL = "mimo-v2.5:free"
NINE_ROUTER_DB = os.path.expanduser("~/.9router/db/data.sqlite")

PROXY = os.environ.get("HARBORKEY_PROXY", "")
if not PROXY:
    env_file = os.path.join(DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip().startswith("HARBORKEY_PROXY="):
                    PROXY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
P = {"http": PROXY, "https": PROXY} if PROXY else {}


def rand_pwd():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + '!Aa1'


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] [{level}] {msg}")


def make_signup_body(email, pwd):
    fp = str(uuid.uuid4())
    bd = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    parts = []

    def af(n, v=""):
        parts.append(f'--{bd}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}')

    af("1_$ACTION_REF_1")
    af("1_$ACTION_1:0", json.dumps({"id": ACTION_ID, "bound": "$@1"}))
    af("1_$ACTION_1:1", '["$undefined"]')
    af("1_$ACTION_KEY", ACTION_KEY)
    af("1_device_fingerprint", fp)
    af("1_timezone")
    af("1_next")
    af("1_email", email)
    af("1_password", pwd)
    af("1_invite_code")
    af("0", '["$undefined","$K1"]')
    body = "\r\n".join(parts) + f"\r\n--{bd}--\r\n"
    headers = {
        "Content-Type": f"multipart/form-data; boundary={bd}",
        "Accept": "text/x-component",
        "Next-Action": NEXT_ACTION,
        "Next-Router-State-Tree": ROUTER,
        "Origin": BASE,
        "Referer": f"{BASE}/login",
    }
    return body, headers


def load_accounts():
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE) as f:
            return json.load(f)
    return []


def save_accounts(data):
    with open(ACCOUNT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_keys():
    if os.path.exists(APIKEY_FILE):
        with open(APIKEY_FILE) as f:
            return [l.strip() for l in f if l.strip()]
    return []


def save_key(key):
    with open(APIKEY_FILE, "a") as f:
        f.write(f"{key}\n")


def inject_to_9router(api_key, email, user_id=""):
    parent_dir = os.path.dirname(NINE_ROUTER_DB)
    if not os.path.exists(parent_dir):
        return False, "9router not installed (no ~/.9router/db directory)"
    try:
        conn = sqlite3.connect(NINE_ROUTER_DB)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM providerConnections WHERE provider='tokenbor'")
        count = cur.fetchone()[0]
        conn_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        label = f"{email.split('@')[0][:6]} #{count + 1}"
        data = json.dumps({
            "defaultModel": "mimo-v2.5:free",
            "apiKey": api_key,
            "testStatus": "active",
            "providerSpecificData": {
                "prefix": "tokenbor",
                "apiType": "chat",
                "baseUrl": "https://tokenharbor.ai/v1",
                "nodeName": "tokenbor",
            },
        })
        cur.execute(
            "INSERT INTO providerConnections (id, provider, authType, name, email, priority, isActive, data, createdAt, updatedAt) "
            "VALUES (?, 'tokenbor', 'api_key', ?, ?, 0, 1, ?, ?, ?)",
            (conn_id, label, email, data, now, now),
        )
        conn.commit()
        conn.close()
        return True, label
    except Exception as e:
        return False, str(e)[:60]


def inject_show_9router():
    parent_dir = os.path.dirname(NINE_ROUTER_DB)
    if not os.path.exists(parent_dir):
        print("\n  9router не установлен — нет директории ~/.9router/db/")
        return []
    try:
        conn = sqlite3.connect(NINE_ROUTER_DB)
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, isActive FROM providerConnections WHERE provider='tokenbor'")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def test_free_model(api_key):
    try:
        r = requests.post(
            f"{BASE}/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=30,
            json={"model": TEST_MODEL, "messages": [{"role": "user", "content": "say ok"}], "max_tokens": 20},
        )
        if r.status_code == 200:
            reply = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return True, f"200 OK - {reply[:30]}"
        return False, f"{r.status_code} - {r.text[:60]}"
    except Exception as e:
        return False, f"ERR - {str(e)[:50]}"


def create_temp_email():
    """Creates a temporary inbox via tempmail.lol, falling back to mail.tm."""
    try:
        r = requests.post("https://api.tempmail.lol/v2/inbox/create", timeout=15)
        if r.status_code == 201 and "address" in r.json():
            d = r.json()
            return d["address"], d.get("token", ""), "tempmail.lol"
    except Exception:
        pass

    try:
        base = "https://api.mail.tm"
        login = ''.join(random.choices(string.ascii_lowercase, k=8))
        dom_r = requests.get(f"{base}/domains", timeout=10)
        if dom_r.status_code != 200:
            return None, None, None
        domain = dom_r.json()['hydra:member'][0]['domain']
        email = f"{login}@{domain}"
        password = rand_pwd()
        requests.post(f"{base}/accounts", json={"address": email, "password": password}, timeout=10)
        t_r = requests.post(f"{base}/token", json={"address": email, "password": password}, timeout=10)
        token = t_r.json().get("token", "") if t_r.status_code == 200 else ""
        return email, token, "mail.tm"
    except Exception:
        return None, None, None


def poll_messages(email_token, source, max_wait=90):
    """Polls the inbox and clicks the verification link if present."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            if source == "mail.tm" and email_token:
                r = requests.get(
                    "https://api.mail.tm/messages",
                    headers={"Authorization": f"Bearer {email_token}"},
                    timeout=10,
                )
                if r.status_code == 200:
                    for msg in r.json().get("hydra:member", []):
                        body = msg.get("text", "") + "\n" + msg.get("html", "")
                        links = re.findall(r'https://tokenharbor\.ai/verify-email\?[^\s"<>]+', body)
                        if links:
                            requests.get(links[0], timeout=15, allow_redirects=True)
                            return True
            else:
                r = requests.get(f"https://api.tempmail.lol/v2/inbox?token={email_token}", timeout=10)
                for em in r.json().get("emails", []):
                    body = em.get("body", "") or em.get("text", "")
                    links = re.findall(r'https://tokenharbor\.ai/verify-email\?[^\s"<>]+', body)
                    if links:
                        requests.get(links[0], timeout=15, allow_redirects=True)
                        return True
        except Exception:
            pass
        time.sleep(8)
    return False


def register_one():
    log("Создаю временную почту...")
    email, email_token, source = create_temp_email()
    if not email:
        log("Не удалось создать почту", "ERROR")
        return None, "failed to create temp email"
    log(f"Email: {email} (source: {source or 'tempmail.lol'})")
    pwd = rand_pwd()
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    log("Загружаю страницу регистрации...")
    for attempt in range(5):
        try:
            s.get(f"{BASE}/login", proxies=P or None, timeout=20)
            break
        except Exception:
            log(f"  Повтор {attempt + 1}/5...", "WARN")
            time.sleep(3)
    else:
        return None, "не удалось загрузить страницу"

    log("Отправляю регистрацию...")
    body, headers = make_signup_body(email, pwd)
    for attempt in range(5):
        try:
            r = s.post(f"{BASE}/login", data=body, headers=headers, proxies=P or None, timeout=25)
            break
        except Exception:
            log(f"  Повтор {attempt + 1}/5...", "WARN")
            time.sleep(3)
    else:
        return None, "ошибка сети после 5 попыток"

    if "human check" in r.text.lower() or "captcha" in r.text.lower():
        log("CAPTCHA detected — подождите и попробуйте позже", "WARN")
        return None, "captcha"

    if "signedIn" not in r.text:
        errors = re.findall(r'"error":"([^"]+)"', r.text)
        err = errors[0] if errors else f"HTTP {r.status_code}"
        log(f"Регистрация НЕ УДАЛАСЬ: {err}", "ERROR")
        return None, err

    uid = re.findall(r'"userId":\s*"([^"]+)"', r.text)
    log(f"Регистрация OK — userId: {uid[0] if uid else '?'}")

    log("Удаляю лишние ключи...")
    try:
        r2 = s.get(f"{BASE}/api/keys", headers={"Accept": "application/json"}, proxies=P or None, timeout=15)
        for k in r2.json().get("keys", []):
            s.delete(f"{BASE}/api/keys/{k['id']}", proxies=P or None, timeout=10)
    except Exception as e:
        log(f"  Ошибка при очистке ключей: {e}", "WARN")

    log("Создаю API ключ...")
    r3 = s.post(
        f"{BASE}/api/keys",
        json={"label": f"harborkey-{random.randint(100, 999)}"},
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        proxies=P or None,
        timeout=15,
    )
    if r3.status_code != 201:
        log(f"Создание ключа НЕ УДАЛОСЬ: {r3.status_code}", "ERROR")
        return None, f"key create failed {r3.status_code}"
    key = r3.json().get("plaintext")
    if not key:
        log("Нет plaintext в ответе", "ERROR")
        return None, "no plaintext"
    log(f"Ключ создан: {key[:35]}...")

    log("Подтверждаю согласие на free модели...")
    rc = s.post(
        f"{BASE}/api/me/privacy",
        json={"free_models_enabled": True},
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        proxies=P or None,
        timeout=10,
    )
    consent_ok = rc.status_code == 200 and '"ok":true' in rc.text
    log(f"Согласие: {'Y' if consent_ok else 'N'} ({rc.status_code})")

    log("Жду письмо подтверждения (макс 90с)...")
    verified = poll_messages(email_token, source)
    log(f"Почта {'подтверждена' if verified else 'НЕ подтверждена (таймаут)'}")

    return {
        "email": email,
        "password": pwd,
        "userId": uid[0] if uid else "",
        "api_key": key,
        "email_token": email_token,
        "verified": verified,
        "consent": consent_ok,
        "source": source or "tempmail.lol",
    }, None


def run_batch(n, inject=False):
    success = 0
    consecutive_failures = 0
    for i in range(n):
        print(f"\n  [{i + 1}/{n}] " + "=" * 40)
        for attempt in range(5):
            try:
                account, err = register_one()
                if account:
                    accounts = load_accounts()
                    accounts.append(account)
                    save_accounts(accounts)
                    save_key(account["api_key"])
                    success += 1
                    consecutive_failures = 0
                    log("Тест free модели...")
                    ok, info = test_free_model(account["api_key"])
                    log(f"Тест {TEST_MODEL}: {'ОК' if ok else 'ПРОВАЛ'} {info}")
                    account["test_result"] = info
                    v = "Y" if account.get("verified") else "N"
                    c = "Y" if account.get("consent") else "N"
                    t = "Y" if ok else "N"
                    print(f"  РЕЗУЛЬТАТ: {account['email']} [verify:{v}] [consent:{c}] [model:{t}]")
                    if inject:
                        injected, msg = inject_to_9router(account["api_key"], account["email"], account.get("userId", ""))
                        log(f"{'Внедрено' if injected else 'Пропущено'}: {msg}")
                    save_accounts(accounts)
                    break
                else:
                    consecutive_failures += 1
                    wait = min(15 * consecutive_failures, 60)
                    log(f"Попытка {attempt + 1}: {err[:50]} — жду {wait}с...", "WARN")
                    time.sleep(wait)
            except Exception as e:
                consecutive_failures += 1
                log(f"Попытка {attempt + 1}: {str(e)[:50]}", "ERROR")
                time.sleep(min(10 * consecutive_failures, 30))
        if i < n - 1:
            wait = random.randint(15, 30)
            log(f"Пауза {wait}с между аккаунтами...", "INFO")
            time.sleep(wait)
    return success


def cmd_create_one(inject=True):
    print(f"\n{'=' * 50}\n  Создать 1 аккаунт + тест {TEST_MODEL}\n{'=' * 50}")
    account, err = register_one()
    if not account:
        print(f"\n  ОШИБКА: {err}")
        return
    accounts = load_accounts()
    accounts.append(account)
    save_accounts(accounts)
    save_key(account["api_key"])
    print()
    log(f"Тест {TEST_MODEL}...")
    ok, info = test_free_model(account["api_key"])
    log(f"Тест: {'ОК' if ok else 'ПРОВАЛ'} {info}")
    v = "Y" if account.get("verified") else "N"
    t = "Y" if ok else "N"
    print(f"\n  Email:    {account['email']}")
    print(f"  Password: {account['password']}")
    print(f"  Key:      {account['api_key'][:35]}...")
    print(f"  Verify:   {v} | Model: {t}")
    if inject:
        ans = input("\n  Внедрить в 9router? (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            injected, msg = inject_to_9router(account["api_key"], account["email"], account.get("userId", ""))
            print(f"  {'OK' if injected else 'SKIP'}: {msg}")


def cmd_test_all():
    keys = load_keys()
    if not keys:
        print("\n  Нет ключей в apikeys.txt")
        return
    print(f"\n  Тестирую {len(keys)} ключей...")
    ok = 0
    for i, k in enumerate(keys):
        valid, info = test_free_model(k)
        print(f"  {'OK' if valid else 'FAIL'} [{i + 1}] {k[:35]}... -> {info}")
        if valid:
            ok += 1
    print(f"\n  {ok}/{len(keys)} рабочих")


def cmd_test_one():
    key = input("\n  Введите ключ: ").strip()
    if not key:
        print("  Пусто")
        return
    valid, info = test_free_model(key)
    print(f"  {'OK' if valid else 'FAIL'} {info}")


def cmd_inject_all():
    accounts = load_accounts()
    if not accounts:
        print("\n  Нет аккаунтов")
        return
    print(f"\n  Внедряю {len(accounts)} аккаунтов...")
    ok = 0
    for a in accounts:
        injected, msg = inject_to_9router(a["api_key"], a["email"], a.get("userId", ""))
        if injected:
            ok += 1
        print(f"  {'OK' if injected else 'SKIP'} {a['email']} -> {msg}")
    print(f"\n  {ok}/{len(accounts)} внедрено")


def cmd_list():
    accounts = load_accounts()
    keys = load_keys()
    print(f"\n  Аккаунты: {len(accounts)} | Ключи: {len(keys)}")
    for i, a in enumerate(accounts):
        print(f"  [{i + 1}] {a['email']} | {a.get('api_key', '?')[:35]}... | verified:{a.get('verified', '?')}")


def cmd_9router_list():
    rows = inject_show_9router()
    if not rows and not os.path.exists(os.path.dirname(NINE_ROUTER_DB)):
        return
    print(f"\n  Записи tokenbor в 9router: {len(rows)}")
    for r in rows:
        print(f"  {r[0][:8]} | {r[1]} | {r[2]} | active={r[3]}")


def menu():
    print(f"""
  HarborKey — TokenHarbor Auto-Register
  Модель: {TEST_MODEL}

  [1] Создать 1 аккаунт (+ тест + инъекция)
  [2] Создать пакет (N аккаунтов)
  [3] Тест всех API ключей
  [4] Список аккаунтов и ключей
  [5] Тест 1 ключа (ввод)
  [6] Внедрить все в 9router
  [7] Показать записи 9router
  [0] Выход""")


def main():
    args = sys.argv[1:]
    if not args:
        while True:
            menu()
            choice = input("  Выбор: ").strip()
            if choice == "1":
                cmd_create_one()
            elif choice == "2":
                n = input("  Количество: ").strip()
                inj = input("  Внедрить в 9router? (y/n): ").strip().lower()
                if n.isdigit() and int(n) > 0:
                    ok = run_batch(int(n), inject=inj in ("y", "yes"))
                    print(f"\n  Готово: {ok}/{int(n)}")
            elif choice == "3":
                cmd_test_all()
            elif choice == "4":
                cmd_list()
            elif choice == "5":
                cmd_test_one()
            elif choice == "6":
                cmd_inject_all()
            elif choice == "7":
                cmd_9router_list()
            elif choice == "0":
                print("  Пока!")
                break
            else:
                print("  Неверный выбор")
    elif args[0] == "1":
        cmd_create_one("--no-inject" not in args)
    elif args[0] == "batch":
        n = int(args[1]) if len(args) > 1 else 5
        inject = "--inject" in args
        ok = run_batch(n, inject=inject)
        print(f"\n  Готово: {ok}/{n}")
    elif args[0] == "test":
        cmd_test_all()
    elif args[0] == "list":
        cmd_list()
    elif args[0] == "inject":
        cmd_inject_all()
    elif args[0] == "9router":
        cmd_9router_list()
    else:
        print(f"Использование: {sys.argv[0]} [1|batch N [--inject]|test|list|inject|9router]")


if __name__ == "__main__":
    main()