# visualizer/app.py – 3D Cube View for Website Traffic

import os, time, threading
import pandas as pd
import plotly.graph_objects as go
import socketio
import streamlit as st
from queue import Queue, Empty

API_PORT = int(os.getenv("TRAFFIC_API_PORT", 5050))
SOCKET_URL = f"http://127.0.0.1:{API_PORT}"
NAMESPACE = "/vis"
EVENT_Q = Queue()
MEMORY_LIMIT = 3000
sio = socketio.Client()

# WebSocket listener
@sio.on("traffic", namespace=NAMESPACE)
def on_traffic(data):
    EVENT_Q.put(data)

def socket_thread():
    try:
        sio.connect(SOCKET_URL, namespaces=[NAMESPACE])
        sio.wait()
    except Exception as e:
        print("❌ WS connection failed:", e)

threading.Thread(target=socket_thread, daemon=True).start()

# Streamlit layout
st.set_page_config(page_title="Bot Radar", layout="wide")
st.title("🧊 Web-Traffic Analyzer: Real-Time Bot vs Human Traffic")

plot_spot = st.empty()
stats_spot = st.empty()
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Main loop
while True:
    # Ingest new events
    while not EVENT_Q.empty():
        evt = EVENT_Q.get()
        st.session_state.df = pd.concat([
            st.session_state.df, pd.json_normalize(evt)
        ], ignore_index=True).iloc[-MEMORY_LIMIT:]

    df = st.session_state.df
    if df.empty:
        st.warning("Waiting for real-time traffic …")
        time.sleep(1)
        continue

    df["timestamp"] = pd.to_datetime(df["ts"])
    df["url_group"] = df["url"].astype("category").cat.codes

    # Layout cube base position
    df["x"] = df["url_group"] % 3
    df["y"] = df["label"].map({"bot": 0, "human": 1, "suspect": 2})
    df["z"] = df["latitude"]  # gives vertical dispersion

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=df["x"],
        y=df["y"],
        z=df["z"],
        mode='markers',
        marker=dict(
            size=5,
            color=df["label"].map({"bot": "red", "human": "green", "suspect": "yellow"}),
            opacity=0.7
        ),
        text=("Label: " + df["label"] +
              "<br>URL: " + df["url"] +
              "<br>IP: " + df["ip"] +
              "<br>UA: " + df["user_agent"]),
        hoverinfo='text'
    ))

    # Add cube wireframe manually (visual box)
    fig.add_trace(go.Mesh3d(
        x=[0, 2, 2, 0, 0, 2, 2, 0],
        y=[0, 0, 2, 2, 0, 0, 2, 2],
        z=[-60, -60, 60, 60, -60, -60, 60, 60],
        i=[0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 6],
        j=[1, 2, 3, 2, 5, 3, 0, 5, 6, 7, 4, 2],
        k=[2, 3, 0, 5, 6, 0, 4, 6, 7, 4, 5, 1],
        opacity=0.1,
        color='blue',
        showscale=False
    ))

    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis=dict(title='Web Pages'),
            yaxis=dict(title='Label Layer (0=Bot, 1=Human, 2=Suspect)'),
            zaxis=dict(title='Latitude'),
        )
    )

    plot_spot.plotly_chart(fig, use_container_width=True)

    stats_spot.markdown(
        f"🔍 **{len(df)} Events** — 🟢 Humans: {(df.label == 'human').sum()} | "
        f"🔴 Bots: {(df.label == 'bot').sum()} | 🟡 Suspect: {(df.label == 'suspect').sum()}"
    )

    time.sleep(7)
