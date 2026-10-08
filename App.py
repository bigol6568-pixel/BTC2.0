import streamlit as st
import time, hashlib, json

st.set_page_config(page_title="BTC 2.0 - Permanent", layout="centered")

if 'chain' not in st.session_state:
    st.session_state.chain = []

def mk(data="Genesis BTC 2.0", prev="0"):
    return {"index":len(st.session_state.chain)+1,"time":time.time(),"data":data,"prev":prev,"hash":hashlib.sha256(json.dumps({"data":data}).encode()).hexdigest()}

if len(st.session_state.chain)==0:
    st.session_state.chain.append(mk())

st.title("₿ BTC 2.0 PERMANENT")
st.write(f"Blocks: {len(st.session_state.chain)}")

if st.button("⛏️ MINE BTC 2.0 BLOCK", use_container_width=True):
    st.session_state.chain.append(mk(f"BTC 2.0 Block {len(st.session_state.chain)+1} Mined", st.session_state.chain[-1]["hash"]))
    st.rerun()

for b in reversed(st.session_state.chain):
    st.info(f"#{b['index']} - {b['data']} | Hash: {b['hash'][:16]}...")

st.success("● PERMANENT LIVE - Anyone can mine")
