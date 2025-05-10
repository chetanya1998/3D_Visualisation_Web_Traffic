# train_from_log.py
import pandas as pd
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path
import os

LOG_FILE = Path("access.log")
MODEL_PATH = Path("../backend/models/traffic_rf.pkl")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

data = []
with open(LOG_FILE) as f:
    for line in f:
        try:
            event = json.loads(line)
            data.append({
                "url_len": len(event["url"]),
                "dwell_ms": event["dwell_ms"],
                "has_bot_ua": 1 if "bot" in event["user_agent"].lower() else 0,
                "label": 1 if "bot" in event["user_agent"].lower() else 0  # heuristically assign
            })
        except Exception:
            pass  # skip bad lines

df = pd.DataFrame(data)

if df.empty:
    raise RuntimeError("No valid log lines parsed.")

X = df[["url_len", "dwell_ms", "has_bot_ua"]]
y = df["label"]

model = RandomForestClassifier()
model.fit(X, y)
joblib.dump(model, MODEL_PATH)

print(f"✅ Trained model saved to: {MODEL_PATH}")
