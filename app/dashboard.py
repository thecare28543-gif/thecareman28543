import time
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Tool Dashboard", page_icon="🛠️", layout="wide")

TOOLS = [
    {"slot": "A1", "name": "Adjustable Wrench", "status": "Present"},
    {"slot": "A2", "name": "Screwdriver Set", "status": "Present"},
    {"slot": "A3", "name": "Digital Multimeter", "status": "Borrowed"},
    {"slot": "A4", "name": "Combination Pliers", "status": "Present"},
    {"slot": "B1", "name": "Wire Stripper", "status": "Present"},
    {"slot": "B2", "name": "Soldering Iron", "status": "Missing"},
    {"slot": "B3", "name": "Hex Key Set", "status": "Present"},
    {"slot": "B4", "name": "Measuring Tape", "status": "Present"},
    {"slot": "C1", "name": "Hammer", "status": "Present"},
    {"slot": "C2", "name": "Utility Knife", "status": "Present"},
    {"slot": "C3", "name": "Spirit Level", "status": "Misplaced"},
    {"slot": "C4", "name": "Cordless Drill", "status": "Present"},
]

st.markdown("""
<style>
.stApp { background: radial-gradient(900px 400px at 85% -10%, #18324a, transparent 60%), #0B1220; }
.card { background:#111C2E; border:1px solid #263650; border-radius:16px; padding:18px; margin-bottom:12px; }
.tool { background:#16233A; border-radius:12px; padding:14px; min-height:90px; border-left:4px solid #2DD4BF; }
.tool.Missing { border-left-color:#FB7185; }.tool.Borrowed { border-left-color:#38BDF8; }.tool.Misplaced { border-left-color:#FBBF24; }
.slot { color:#8DA2B8; font-size:12px; font-weight:700; }.name { color:#E7EEF6; font-weight:600; margin:6px 0; }
.status { color:#8DA2B8; font-size:12px; }.metric { font-size:30px; font-weight:800; color:#2DD4BF; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🛠️ Tool Monitoring Dashboard")
st.caption("Streamlit deployment-ready demo • YOLOv8 integration can be connected when the missing app modules are added")

present = sum(t["status"] == "Present" for t in TOOLS)
missing = sum(t["status"] == "Missing" for t in TOOLS)
borrowed = sum(t["status"] == "Borrowed" for t in TOOLS)
misplaced = sum(t["status"] == "Misplaced" for t in TOOLS)

c1, c2, c3, c4 = st.columns(4)
for col, label, value, color in [
    (c1, "Total Slots", len(TOOLS), "#38BDF8"),
    (c2, "Present", present, "#2DD4BF"),
    (c3, "Missing", missing, "#FB7185"),
    (c4, "Borrowed", borrowed, "#38BDF8"),
]:
    col.markdown(f'<div class="card"><div style="color:#8DA2B8">{label}</div><div class="metric" style="color:{color}">{value}</div></div>', unsafe_allow_html=True)

left, right = st.columns([0.65, 0.35])
with left:
    st.subheader("📋 Tool Status")
    cols = st.columns(4)
    for i, tool in enumerate(TOOLS):
        with cols[i % 4]:
            st.markdown(f'<div class="tool {tool["status"]}"><div class="slot">{tool["slot"]}</div><div class="name">{tool["name"]}</div><div class="status">{tool["status"]}</div></div>', unsafe_allow_html=True)

    st.subheader("📈 Usage Analytics")
    usage = pd.DataFrame({"tool": [t["name"] for t in TOOLS[:6]], "uses": [12, 9, 8, 6, 5, 3]})
    fig = go.Figure(go.Bar(x=usage["tool"], y=usage["uses"], marker_color="#2DD4BF"))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=80), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#E7EEF6", xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🔔 Recent Alerts")
    if missing:
        st.error("Soldering Iron (B2) is missing")
    if misplaced:
        st.warning("Spirit Level (C3) is misplaced")
    if borrowed:
        st.info("Digital Multimeter (A3) is borrowed")
    st.subheader("📊 Fleet Health")
    st.progress(present / len(TOOLS), text=f"{present / len(TOOLS):.0%} present")
    st.caption(f"Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}")

if st.toggle("Auto-refresh", value=False):
    time.sleep(10)
    st.rerun()
