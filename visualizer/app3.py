# Real-time 3D Cube Traffic Visualizer with Auto-Refresh & Cube Metrics (app3.py)
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.graph_objects as go
import numpy as np
import time

LOG_PATH = Path(__file__).parent.parent / "logs" / "access.log"

st.set_page_config(layout="wide", page_title="🔲 Real-time 3D Traffic Visualizer")
st.title("🔲 Real-time 3D Cube-Based Website Traffic Classifier")

# Remove meta-refresh!
# st.markdown("""<meta http-equiv="refresh" content="5">""", unsafe_allow_html=True)

# Load logs
def load_logs():
    if not LOG_PATH.exists():
        return pd.DataFrame()
    lines = LOG_PATH.read_text().strip().split("\n")
    data = [json.loads(line) for line in lines if line.strip()]
    return pd.DataFrame(data)

df = load_logs()
if df.empty:
    st.warning("⚠️ No traffic yet. Start simulator and backend.")
    st.stop()

# Preprocessing
df["ts"] = pd.to_datetime(df["ts"])
df["predicted_label"] = df.get("predicted_label", df.get("label", "unknown"))
df["true_label"] = df.get("true_label", df.get("label", "unknown"))
df["site"] = df.get("site", "unknown")
df["cube_id"] = df.get("cube_id", 0)
df["model"] = df.get("model", "N/A")
df["url"] = df.get("url", "")

# Map & Configs
label_color_map = {
    "human": "green", "bot": "red", "naive_bot": "red",
    "stealth_bot": "red", "mimic_bot": "orange", "unknown": "gray"
}
model_pattern_map = {
    0: "Random Forest", 1: "XGBoost", 2: "Logistic Regression", 3: "Isolation Forest"
}
site_offsets = {
    "shop.com":   [0.1, 0.1, 0.1],
    "learn.edu":  [0.6, 0.1, 0.1],
    "gov.in":     [0.1, 0.6, 0.1],
    "bank.net":   [0.6, 0.6, 0.1],
}
cube_size = 0.25

# --- Cube Accuracy & Volume Summary ---
st.subheader("📦 Cube-wise Classification Summary")
summary_data = []
for site, offset in site_offsets.items():
    cube_id = df[df["site"] == site]["cube_id"].mode()[0] if not df[df["site"] == site].empty else 0
    site_df = df[df["site"] == site]
    total = len(site_df)
    correct = (site_df["predicted_label"] == site_df["true_label"]).sum()
    accuracy = (correct / total) if total > 0 else 0
    model = model_pattern_map.get(cube_id, "Unknown")
    summary_data.append({
        "Site": site, "Cube ID": cube_id, "Model": model,
        "Total Hits": total, "Accuracy": f"{accuracy:.2%}"
    })
st.dataframe(pd.DataFrame(summary_data))

# --- Real-time 3D Traffic Cube ---
st.subheader("🧊 Real-time 3D Visualization")

cube_placeholder = st.empty()

site_offsets = {
    "shop.com":   [0.1, 0.1, 0.1],
    "learn.edu":  [0.6, 0.1, 0.1],
    "gov.in":     [0.1, 0.6, 0.1],
    "bank.net":   [0.6, 0.6, 0.1],
}
cube_size = 0.25
label_color_map = {
    "human": "green", "bot": "red", "naive_bot": "red",
    "stealth_bot": "red", "mimic_bot": "orange", "unknown": "gray"
}
model_pattern_map = {
    0: "Random Forest", 1: "XGBoost", 2: "Logistic Regression", 3: "Isolation Forest"
}

def draw_cube_figure(df):
    df_sorted = df.sort_values("ts", ascending=False).head(300).reset_index(drop=True)
    fig = go.Figure()
    x, y, z, color, text = [], [], [], [], []

    for _, row in df_sorted.iterrows():
        offset = site_offsets.get(row["site"], [0.1, 0.1, 0.1])
        px = np.random.uniform(offset[0], offset[0]+cube_size)
        py = np.random.uniform(offset[1], offset[1]+cube_size)
        pz = np.random.uniform(offset[2], offset[2]+cube_size)
        x.append(px)
        y.append(py)
        z.append(pz)
        color.append(label_color_map.get(row["predicted_label"], "gray"))
        text.append(
            f"<b>Type:</b> {row['predicted_label']}<br>"
            f"<b>Site:</b> {row['site']}<br>"
            f"<b>Endpoint:</b> {row['url']}<br>"
            f"<b>Model:</b> {model_pattern_map.get(row['cube_id'], 'Unknown')}"
        )

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=4, color=color, opacity=0.8),
        text=text,
        hoverinfo="text",
        name="Traffic"
    ))

    # Draw small cubes and labels
    def draw_cube(fig, offset, label, color="lightblue", model="Model"):
        s = cube_size
        v = [[0,0,0],[s,0,0],[s,s,0],[0,s,0],
             [0,0,s],[s,0,s],[s,s,s],[0,s,s]]
        v = [[vx+offset[0], vy+offset[1], vz+offset[2]] for vx,vy,vz in v]
        edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
        for e in edges:
            fig.add_trace(go.Scatter3d(
                x=[v[e[0]][0], v[e[1]][0]],
                y=[v[e[0]][1], v[e[1]][1]],
                z=[v[e[0]][2], v[e[1]][2]],
                mode='lines',
                line=dict(color=color, width=6),
                showlegend=False
            ))
        # Add site label above the cube
        fig.add_trace(go.Scatter3d(
            x=[offset[0]+s/2], y=[offset[1]+s/2], z=[offset[2]+s+0.06],
            mode='text',
            text=[f"{label}<br>{model}"],
            textfont=dict(size=14, color=color),
            showlegend=False
        ))

    for site, offset in site_offsets.items():
        cube_id = df[df["site"] == site]["cube_id"].mode()[0] if not df[df["site"] == site].empty else 0
        model = model_pattern_map.get(cube_id, "Unknown")
        draw_cube(fig, offset, site, model=model)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=650
    )
    return fig

# --- Live update loop for the cube only ---
while True:
    # Reload logs for new traffic
    df = load_logs()
    if df.empty:
        break
    df["ts"] = pd.to_datetime(df["ts"])
    df["predicted_label"] = df.get("predicted_label", df.get("label", "unknown"))
    df["true_label"] = df.get("true_label", df.get("label", "unknown"))
    df["site"] = df.get("site", "unknown")
    df["cube_id"] = df.get("cube_id", 0)
    df["model"] = df.get("model", "N/A")
    df["url"] = df.get("url", "")

    fig = draw_cube_figure(df)
    cube_placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.5)

# --- Cube stats summary table ---
summary_rows = []
for site, offset in site_offsets.items():
    cube_id = df[df["site"] == site]["cube_id"].mode()[0] if not df[df["site"] == site].empty else 0
    model = model_pattern_map.get(cube_id, "Unknown")
    site_df = df[df["site"] == site]
    total = len(site_df)
    n_human = (site_df["predicted_label"] == "human").sum()
    n_bot = (site_df["predicted_label"] == "bot").sum()
    n_naive_bot = (site_df["predicted_label"] == "naive_bot").sum()
    n_stealth_bot = (site_df["predicted_label"] == "stealth_bot").sum()
    n_mimic_bot = (site_df["predicted_label"] == "mimic_bot").sum()
    summary_rows.append({
        "Site": site,
        "Model": model,
        "Total Hits": total,
        "Human Hits": n_human,
        "Bot Hits": n_bot,
        "Naive Bots": n_naive_bot,
        "Stealth Bots": n_stealth_bot,
        "Mimic Bots": n_mimic_bot
    })
st.subheader("📊 Live Website Traffic & Model Table")
st.dataframe(pd.DataFrame(summary_rows))

