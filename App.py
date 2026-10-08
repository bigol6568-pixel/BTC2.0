import streamlit as st
import hashlib, time, secrets, datetime, json, os, io, qrcode, random
from mnemonic import Mnemonic

st.set_page_config(page_title="BTC 2.0 GAME", page_icon="🎮", layout="wide")
DB_FILE = "btc_full_db.json"

def h(s): return hashlib.sha256(s.encode()).hexdigest()
def make_qr(t):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(t); qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()
def wallet_from_phrase(p):
    x = h(p); return "bc1q"+x[:38], "5K"+h(x+"pk")[:49]
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"chain":[],"bal":{},"txs":[],"mined":0,"wallets":{},"chat":[]}
def save_db():
    d={"chain":st.session_state["chain"],"bal":st.session_state["bal"],"txs":st.session_state["txs"],"mined":st.session_state["mined"],"wallets":st.session_state["wallets"],"chat":st.session_state["chat"]}
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
def get_reward(): return max(50/(2**(len(st.session_state["chain"])//21)),0.5)
def get_bal(a): return st.session_state["bal"].get(a,0)

if "chain" not in st.session_state:
    db=load_db()
