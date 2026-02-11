import json
import subprocess
import sys
from pathlib import Path
import os

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="Crypto Futures Intel", layout="wide")

st.title("Crypto Futures Intel")
st.caption("BTC / ADA / SOL — Futures Risk-Aware Signal Dashboard")

top1, top2, top3 = st.columns([1, 1, 2])
with top1:
    run_btn = st.button("Analizi Çalıştır", use_container_width=True)
with top2:
    auto = st.toggle("Oto yenile (15 sn)", value=False)
with top3:
    st.info("⚠️ Yatırım tavsiyesi değildir. Futures yüksek risklidir.", icon="⚠️")

def run_engine() -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    p = subprocess.run(
        [sys.executable, "scripts/run_dashboard.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip())
    return json.loads(p.stdout)

def status_badge(status: str):
    if status == "TRADEABLE":
        st.success("TRADEABLE ✅")
    elif status == "CAUTION":
        st.warning("CAUTION ⚠️")
    else:
        st.error("NO_TRADE ⛔")

def action_badge(action: str):
    if action == "LONG":
        st.success("LONG")
    elif action == "SHORT":
        st.warning("SHORT")
    else:
        st.info("NO-TRADE")

def render_card(a: dict):
    st.subheader(a["symbol"])
    status_badge(a["status"])

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Regime:** `{a['regime']['label']}`")
        st.write(f"**Confidence:** `{a['regime']['confidence']}`")
        st.write(f"**Bias:** `{a['bias']}`")
        st.write(f"**Setup:** `{a['setup']}`")
    with c2:
        st.write("**Action**")
        action_badge(a["action"])
        st.write("**Risk**")
        st.write(f"- Leverage cap: **{a['risk']['leverage_cap']}x**")
        st.write(f"- Stop: {a['risk']['stop']}")
        rf = a["risk"].get("red_flags") or []
        st.write(f"- Red flags: {', '.join(rf) if rf else 'yok'}")

    st.write("**Trigger koşulları**")
    for cond in a["trigger"]["conditions"]:
        st.write(f"- {cond}")

    why = a.get("why") or []
    if why:
        st.write("**Why**")
        for w in why:
            st.write(f"- {w}")

    st.caption(f"Timestamp: {a.get('ts','')}")

# first load
if "data" not in st.session_state:
    st.session_state["data"] = None

if run_btn:
    try:
        st.session_state["data"] = run_engine()
    except Exception as e:
        st.error(str(e))
        st.stop()

if auto:
    st.caption("Oto yenile açık. 15 saniyede bir yeniden çalıştır.")
    st.autorefresh(interval=15_000, key="autorefresh")

data = st.session_state.get("data")
if not data:
    st.warning("Analizi görmek için **Analizi Çalıştır** butonuna bas.")
    st.stop()

assets = data.get("assets", [])
cols = st.columns(3)

for i, a in enumerate(assets[:3]):
    with cols[i]:
        render_card(a)

with st.expander("JSON (debug)"):
    st.json(data)
