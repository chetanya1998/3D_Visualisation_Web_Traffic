import requests, time, uuid, random, os, threading

PORT = int(os.getenv("TRAFFIC_API_PORT", 5050))
ENDPOINT = f"http://127.0.0.1:{PORT}/hit"

# Website definitions mapped to cubes
SITES = {
    "shop.com": 0,        # E-Commerce
    "learn.edu": 1,       # Education
    "gov.in": 2,          # Government
    "bank.net": 3         # Financial
}

UA_HUMAN = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3)",
    "Chrome/124.0"
]

UA_BOT = [
    "python-requests/2.31",
    "curl/7.64.1",
    "AdsBot-Google",
    "Mozilla/5.0 (Linux; Android 10)"
]

# Generates a random realistic URL path
def random_path():
    words = ["login", "checkout", "profile", "offers", "dashboard", "verify", "support", "track", "search"]
    return "/" + "/".join(random.choices(words, k=random.randint(1, 3)))

def send_hit(payload):
    try:
        requests.post(ENDPOINT, json=payload, timeout=1)
    except Exception as e:
        print(f"Failed to send: {e}")

def build_payload(site, cube_id, label, ua_type):
    return {
        "session_id": str(uuid.uuid4())[:8],
        "ip": f"203.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "user_agent": random.choice(UA_HUMAN if ua_type == "human" else UA_BOT),
        "url": f"https://{site}{random_path()}",
        "latitude": random.uniform(-60, 60),
        "longitude": random.uniform(-180, 180),
        "dwell_ms": random.randint(300, 7000),
        "cube_id": cube_id,
        "site": site,
        "true_label": label  # <-- changed from "label" to "true_label"
    }

def simulate(site, cube_id):
    while True:
        # Randomly choose a label to simulate
        label = random.choices(["human", "naive_bot", "stealth_bot", "mimic_bot"], weights=[0.5, 0.2, 0.2, 0.1])[0]

        if label == "human":
            ua_type = "human"
        elif label == "mimic_bot":
            ua_type = "human"
        else:
            ua_type = "bot"

        payload = build_payload(site, cube_id, label, ua_type)
        send_hit(payload)
        time.sleep(random.uniform(0.5, 2.5))

if __name__ == "__main__":
    print(f"▶ Simulating multi-site traffic to {ENDPOINT}")

    for site, cube_id in SITES.items():
        t = threading.Thread(target=simulate, args=(site, cube_id))
        t.daemon = True
        t.start()

    while True:
        time.sleep(1)
