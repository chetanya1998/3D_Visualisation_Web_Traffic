import requests, time, uuid, random, os, threading

PORT = int(os.getenv("TRAFFIC_API_PORT", 5050))
ENDPOINT = f"http://127.0.0.1:{PORT}/hit"

PAGES = ["/", "/pricing", "/cart", "/login", "/product", "/search?q=shoes", "/about"]
UA_HUMAN = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Chrome/124.0"
]
UA_BOT_NAIVE = ["python-requests/2.31", "curl/7.64.1"]
UA_BOT_STEALTH = ["AdsBot-Google", "Mozilla/5.0 (Linux; Android 10)"]

def send_hit(data):
    try:
        requests.post(ENDPOINT, json=data, timeout=1)
    except:
        pass

def build_payload(ip, ua, url, label):
    return {
        "session_id": str(uuid.uuid4())[:8],
        "ip": ip,
        "url": url,
        "user_agent": ua,
        "latitude": random.uniform(-60, 60),
        "longitude": random.uniform(-180, 180),
        "dwell_ms": random.randint(500, 8000),
        "label": label
    }

# Behaviors
def human_user():
    while True:
        ip = f"203.0.{random.randint(0,255)}.{random.randint(0,255)}"
        ua = random.choice(UA_HUMAN)
        session_pages = random.choices(PAGES, k=random.randint(2, 5))
        for page in session_pages:
            data = build_payload(ip, ua, page, "human")
            send_hit(data)
            time.sleep(random.uniform(2.0, 5.0))

def naive_bot():
    while True:
        ip = f"198.51.{random.randint(0,255)}.{random.randint(0,255)}"
        ua = random.choice(UA_BOT_NAIVE)
        page = random.choice(PAGES)
        data = build_payload(ip, ua, page, "naive_bot")
        send_hit(data)
        time.sleep(random.uniform(0.2, 0.5))

def stealth_bot():
    while True:
        ip = f"192.0.{random.randint(0,255)}.{random.randint(0,255)}"
        ua = random.choice(UA_BOT_STEALTH)
        page = random.choice(PAGES)
        data = build_payload(ip, ua, page, "stealth_bot")
        send_hit(data)
        time.sleep(random.uniform(1.0, 3.0))

def mimic_bot():
    while True:
        ip = f"198.18.{random.randint(0,255)}.{random.randint(0,255)}"
        ua = random.choice(UA_HUMAN)
        session_pages = random.choices(PAGES, k=random.randint(3, 6))
        for page in session_pages:
            data = build_payload(ip, ua, page, "mimic_bot")
            send_hit(data)
            time.sleep(random.uniform(1.5, 4.0))

if __name__ == "__main__":
    print(f"▶ Simulating evolving traffic at {ENDPOINT}")

    behaviors = [human_user, naive_bot, stealth_bot, mimic_bot]
    for behavior in behaviors:
        t = threading.Thread(target=behavior)
        t.daemon = True
        t.start()

    while True:
        time.sleep(1)
