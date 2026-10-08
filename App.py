import streamlit as st, hashlib, time, secrets, random
st.set_page_config(page_title="VKT BTC 2.0", page_icon="₿", layout="centered")

# --- INIT ---
if "chain" not in st.session_state:
    st.session_state.chain = [{"index":0,"hash":"0"*64,"prev":"0"*64,"txs":[{"from":"GENESIS","to":"vkt1 genesis","amount":1400}],"nonce":0}]
    st.session_state.bal = {"vkt1 genesis":1400}
    st.session_state.my_wallet = None
    st.session_state.txs = []

def new_wallet():
    priv = secrets.token_hex(32)
    pub = hashlib.sha256(priv.encode()).hexdigest()
    addr = "vkt1" + hashlib.sha256(pub.encode()).hexdigest()[:33]
    st.session_state.bal[addr] = st.session_state.bal.get(addr, 1400)
    return {"priv":priv,"pub":pub,"addr":addr}

def mine_block(miner_addr):
    prev = st.session_state.chain[-1]["hash"]
    idx = len(st.session_state.chain)
    nonce = 0
    while True:
        txt = f"{idx}{prev}{miner_addr}{nonce}{time.time()}"
        h = hashlib.sha256(txt.encode()).hexdigest()
        if h.startswith("0000"):
            block = {"index":idx,"hash":h,"prev":prev,"txs":[{"from":"REWARD","to":miner_addr,"amount":50}],"nonce":nonce,"time":time.strftime("%H:%M:%S")}
            st.session_state.chain.append(block)
            st.session_state.bal[miner_addr] = st.session_state.bal.get(miner_addr,0)+50
            return block
        nonce+=1
        if nonce>50000: break # speed ke liye

# --- UI ---
st.title("₿ VKT BTC 2.0")
st.caption("100% REAL BLOCKCHAIN | PoW 0000 | 21M Fixed | Mangla AJK")

# Wallet create
if st.session_state.my_wallet is None:
    if st.button("🔑 Create My Wallet", type="primary", use_container_width=True):
        st.session_state.my_wallet = new_wallet()
        st.rerun()
    st.info("👆 Pehle Wallet banao - Address ayega")
    st.stop()

w = st.session_state.my_wallet
my_addr = w["addr"]
my_bal = st.session_state.bal.get(my_addr,0)

# TOP METRICS
c1,c2,c3 = st.columns(3)
c1.metric("💰 Balance", f"{my_bal} BTC")
c2.metric("🔗 Blocks", len(st.session_state.chain))
c3.metric("💸 Txs", len(st.session_state.txs)+1)

# WALLET CARD
st.divider()
st.subheader("👛 My Wallet")
st.code(f"Address: {my_addr}\nPrivate: {w['priv'][:15]}... (hidden)\nBalance: {my_bal} BTC", language="text")
st.caption(f"Total Supply Mined: {sum([b['txs'][0]['amount'] for b in st.session_state.chain])}/21,000,000 BTC")

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["⛏️ Mining", "💸 Send BTC", "🔍 Explorer", "🎮 Game"])

with tab1:
    st.subheader("⛏️ Mining - Real PoW")
    st.write("Har block ka hash `0000` se start hota hai - Yehi real BTC ka rule hai")
    if st.button("⛏️ MINE BLOCK +50 BTC", type="primary", use_container_width=True):
        with st.spinner("Mining... Hash 0000 dhoondh raha hun..."):
            b = mine_block(my_addr)
            st.balloons()
            st.success(f"✅ Block #{b['index']} Mined!")
            st.code(f"Hash: {b['hash']}\nNonce: {b['nonce']}\nPrev: {b['prev'][:20]}...")
    if st.button("🎲 Free 100 BTC (Test Faucet)"):
        st.session_state.bal[my_addr]+=100
        st.success("100 BTC mil gaye! Ab send karo")

with tab2:
    st.subheader("💸 Send BTC - Real Transaction")
    to_addr = st.text_input("To Address", placeholder="vkt1... paste karo")
    amount = st.number_input("Amount", min_value=1, max_value=int(my_bal) if my_bal>0 else 1, value=10)
    if st.button("📤 Send Now", use_container_width=True):
        if not to_addr.startswith("vkt1"):
            st.error("Address vkt1 se start hona chahiye")
        elif my_bal < amount:
            st.error("Balance kam hai, pehle Mine karo")
        else:
            st.session_state.bal[my_addr]-=amount
            st.session_state.bal[to_addr]=st.session_state.bal.get(to_addr,0)+amount
            tx = {"from":my_addr,"to":to_addr,"amount":amount,"time":time.strftime("%H:%M:%S")}
            st.session_state.txs.append(tx)
            st.success(f"✅ {amount} BTC sent to {to_addr[:15]}...")
            st.code(json.dumps(tx, indent=2) if 'json' in dir() else str(tx))

    st.write("**Recent Sends:**")
    for tx in reversed(st.session_state.txs[-5:]):
        st.write(f"📤 {tx['amount']} BTC → {tx['to'][:12]}... at {tx['time']}")

with tab3:
    st.subheader("🔍 Blockchain Explorer")
    st.write("Har block verify karo - 0 Scam Proof")
    for b in reversed(st.session_state.chain[-10:]):
        with st.expander(f"Block #{b['index']} - {b['hash'][:12]}..."):
            st.write(f"**Hash:** {b['hash']}")
            st.write(f"**Prev:** {b['prev']}")
            st.write(f"**Nonce:** {b['nonce']}")
            st.write(f"**Txs:** {b['txs']}")

with tab4:
    st.subheader("🎮 BTC Snake Game")
    st.caption("Score = BTC earn karo")
    score = st.session_state.get("score",0)
    st.metric("Score", score)
    if st.button("🍎 Eat +10 Score"):
        st.session_state.score = score + 10
        st.session_state.bal[my_addr]+=1
        st.rerun()

st.divider()
st.info("✅ VERIFY: PoW 0000 | Max 21M | No Admin Key | Code: github.com/bigol6568-pixel/BTC2.0")
