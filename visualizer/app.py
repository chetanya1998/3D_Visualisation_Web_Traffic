# visualizer/app.py – 3D Website Cube + Traffic Inside

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
MEMORY_LIMIT = 2000
sio = socketio.Client()

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
st.set_page_config(page_title="3D Website Cube", layout="wide")
st.title("🧊 3D Cube Radar – Visualizing Website Traffic Internally")

plot_spot = st.empty()
stats_spot = st.empty()
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Main loop
while True:
    while not EVENT_Q.empty():
        evt = EVENT_Q.get()
        st.session_state.df = pd.concat([
            st.session_state.df, pd.json_normalize(evt)
        ], ignore_index=True).iloc[-MEMORY_LIMIT:]

    df = st.session_state.df
    if df.empty:
        st.warning("Waiting for traffic data...")
        time.sleep(1)
        continue

    df["timestamp"] = pd.to_datetime(df["ts"])
    df["url_group"] = df["url"].astype("category").cat.codes

    # Coordinate mapping inside cube
    x = df["url_group"]
    y = (df["timestamp"].astype("int64") / 1e12) % 10  # limit height
    z = df["latitude"] % 10  # normalize to fit cube

    traffic = go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers",
        marker=dict(
            size=4,
            opacity=0.8,
            color=df["label"].map({"human": "green", "bot": "red", "suspect": "yellow"})
        ),
        hovertext=("Label: " + df["label"] +
                   "<br>Page: " + df["url"] +
                   "<br>IP: " + df["ip"]),
        name="Traffic"
    )

    # Create cube frame (a 10x10x10 cube)
    cube_edges = []
    edges = [(0,0,0),(0,0,10),(0,10,0),(10,0,0)]
    for dx in [0,10]:
        for dy in [0,10]:
            for dz in [0,10]:
                cube_edges.append(go.Scatter3d(
                    x=[dx, dx], y=[dy, dy], z=[dz, 10-dz],
                    mode="lines",
                    line=dict(color="lightblue", width=3),
                    showlegend=False
                ))

    fig = go.Figure(data=[traffic] + cube_edges)
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(title="Page Group", range=[-1, 10]),
            yaxis=dict(title="Time Bucket", range=[-1, 10]),
            zaxis=dict(title="Latitude Bucket", range=[-1, 10])
        ),
        height=700
    )

    plot_spot.plotly_chart(fig, use_container_width=True)

    stats_spot.markdown(
        f"📦 Cube Events: {len(df)} — 🟢 Humans: {(df.label == 'human').sum()} | "
        f"🔴 Bots: {(df.label == 'bot').sum()} | 🟡 Suspects: {(df.label == 'suspect').sum()}"
    )

    time.sleep(1)
