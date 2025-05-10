import joblib, os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "traffic_rf.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception:
    model = None
    print("⚠️ No ML model found – using fallback rule")

import pandas as pd
...

def classify_event(event: dict) -> str:
    if model:
        try:
            df_feat = pd.DataFrame([{
                "url_len": len(event["url"]),
                "dwell_ms": event["dwell_ms"],
                "has_bot_ua": 1 if "bot" in event["user_agent"].lower() else 0
            }])
            pred = model.predict(df_feat)[0]
            return "bot" if pred == 1 else "human"
        except Exception:
            return "suspect"
    return "bot" if "bot" in event["user_agent"].lower() else "human"

