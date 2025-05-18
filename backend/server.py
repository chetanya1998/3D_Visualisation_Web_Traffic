from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from pathlib import Path
from datetime import datetime
import logging, json
from classifier import classify_event

LOG_PATH = Path(__file__).parent.parent / "logs" / "access.log"
LOG_PATH.parent.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger("traffic")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(LOG_PATH))

app = Flask(__name__)
app.config["SECRET_KEY"] = "3d-traffic-visualizer"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

@app.route("/hit", methods=["POST"])
def hit():
    data = request.get_json(force=True)
    ts = datetime.utcnow().isoformat()
    logger.info(json.dumps({**data, "ts": ts}))

    label = classify_event(data)
    enriched = {**data, "ts": ts, "label": label}
    socketio.emit("traffic", enriched, namespace="/vis")
    return jsonify({"status": "ok", "label": label})

@socketio.on("connect", namespace="/vis")
def vis_connect():
    print("✅ visualizer connected")
    return True

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050)
