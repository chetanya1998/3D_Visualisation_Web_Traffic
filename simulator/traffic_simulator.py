import requests, time, uuid, random, os

PORT = int(os.getenv("TRAFFIC_API_PORT", 5050))
ENDPOINT = f"http://127.0.0.1:{PORT}/hit"
PAGES = ["/", "/pricing", "/cart", "/login"]
UA_HUMAN = ["Mozilla/5.0", "Chrome/124.0"]
UA_BOT = ["python-requests/2.31", "AdsBot-Google"]

def random_hit():
    is_bot = random.random() < 0.3
    return {
        "session_id": str(uuid.uuid4())[:8],
        "ip": f"203.0.{random.randint(0,255)}.{random.randint(0,255)}",
        "url": random.choice(PAGES),
        "user_agent": random.choice(UA_BOT if is_bot else UA_HUMAN),
        "latitude": random.uniform(-60, 60),
        "longitude": random.uniform(-180, 180),
        "dwell_ms": random.randint(500, 8000)
    }

if __name__ == "__main__":
    print(f"▶ Firing traffic at {ENDPOINT}")
    while True:
        try:
            requests.post(ENDPOINT, json=random_hit(), timeout=1)
        except:
            pass
        time.sleep(1/60)
