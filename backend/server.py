from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from pathlib import Path
from datetime import datetime
import logging, json

from classifier import classify_event
from utils import get_cube_id_from_ip  # Assume you have this helper

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

    # Use cube_id from payload or calculate from IP
    cube_id = int(data.get("cube_id", get_cube_id_from_ip(data.get("ip", "0.0.0.0"))))

    predicted_label = classify_event(data, cube_id)
    true_label = data.get("label", "unknown")

    enriched = {
        **data,
        "ts": ts,
        "cube_id": cube_id,
        "predicted_label": predicted_label,
        "true_label": true_label
    }

    logger.info(json.dumps(enriched))
    socketio.emit("traffic", enriched, namespace="/vis")
    return jsonify({"status": "ok", "predicted_label": predicted_label})

@socketio.on("connect", namespace="/vis")
def vis_connect():
    print("✅ visualizer connected")
    return True

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050)
