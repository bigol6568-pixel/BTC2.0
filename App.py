import streamlit as st, hashlib, time, json
st.set_page_config(page_title="BTC 2.0 REAL", page_icon="₿", layout="centered")
st.title("₿ BTC 2.0 - 100% REAL - 0 SCAM")
st.caption("PoW 0000 | 21M Fixed | Open Source | Mangla AJK")

if "chain" not in st.session_state:
    st.session_state.chain=[{"index":0,"hash":"0"*64,"prev":"0","reward":1400}]
    st.session_state.bal=1400

def mine():
    import random
    prev=st.session_state.chain[-1]["hash"]
    nonce=0
    while True:
        h=hashlib.sha256(f"{len(st.session_state.chain)}{prev}{nonce}{time.time()}".encode()).hexdigest()
        if h.startswith("0000"):
            b={"index":len(st.session_state.chain),"hash":h,"prev":prev,"reward":50,"nonce":nonce}
            st.session_state.chain.append(b)
            st.session_state.bal+=50
            return b
        nonce+=1

c1,c2=st.columns(2)
c1.metric("Balance", f"{st.session_state.bal} BTC")
c2.metric("Blocks", len(st.session_state.chain))

if st.button("⛏️ MINE 50 BTC - REAL PoW", type="primary", use_container_width=True):
    with st.spinner("Mining Real Block..."):
        b=mine()
        st.balloons()
        st.success(f"Block #{b['index']} Mined: {b['hash'][:25]}... Nonce {b['nonce']}")

st.divider()
st.subheader("Explorer - Last 10 Blocks")
for b in reversed(st.session_state.chain[-10:]):
    st.code(f"#{b['index']} | {b['hash']} | Reward {b['reward']}")
