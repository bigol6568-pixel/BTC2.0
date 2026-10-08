import streamlit as st, json
from wallet import create_new_wallet, export_wallet_json, import_wallet_from_json, get_short
from blockchain import Blockchain
from transaction import create_transaction

st.set_page_config(page_title="VKT BTC 2.0", page_icon="₿", layout="wide")
st.title("₿ VKT BTC 2.0 - REAL BLOCKCHAIN")
st.caption("PoW 0000 | 21M Fixed | Open Source | Separate Files | 0 Scam")

# Session
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.balances = {"GENESIS":1400}
    st.session_state.wallets = []
    st.session_state.current_wallet = None
    st.session_state.txs = []

bc = st.session_state.blockchain
balances = st.session_state.balances

# SIDEBAR - WALLET MANAGEMENT
st.sidebar.title("👛 Wallet Manager")

if st.sidebar.button("➕ New Wallet Create", use_container_width=True):
    w = create_new_wallet()
    st.session_state.wallets.append(w)
    st.session_state.current_wallet = w
    balances[w["address"]] = balances.get(w["address"], 1400)
    st.sidebar.success(f"Created: {get_short(w['address'])}")

if len(st.session_state.wallets)>0:
    addrs = [w["address"] for w in st.session_state.wallets]
    sel = st.sidebar.selectbox("Select Wallet", addrs, format_func=get_short)
    for w in st.session_state.wallets:
        if w["address"]==sel:
            st.session_state.current_wallet=w

# Export / Import
st.sidebar.divider()
st.sidebar.subheader("📤 Export / Import")

if st.session_state.current_wallet:
    json_data = export_wallet_json(st.session_state.current_wallet)
    st.sidebar.download_button("📥 Export Wallet JSON", json_data, file_name=f"{st.session_state.current_wallet['address']}.json", use_container_width=True)
    with st.sidebar.expander("🔑 Show Private Key"):
        st.code(st.session_state.current_wallet["private_key"])
        st.code(st.session_state.current_wallet["address"])

uploaded = st.sidebar.file_uploader("📤 Import Wallet JSON", type=["json"])
if uploaded:
    data = uploaded.read().decode()
    w = import_wallet_from_json(data)
    if w:
        st.session_state.wallets.append(w)
        st.session_state.current_wallet=w
        balances[w["address"]]=balances.get(w["address"], w.get("balance",0))
        st.sidebar.success("Wallet Imported!")
    else:
        st.sidebar.error("Invalid JSON")

# MAIN
if not st.session_state.current_wallet:
    st.info("👈 Sidebar se **New Wallet Create** dabao - Phir sab options ayenge!")
    st.stop()

cw = st.session_state.current_wallet
my_addr = cw["address"]
my_bal = balances.get(my_addr,0)

c1,c2,c3,c4 = st.columns(4)
c1.metric("💰 Balance", f"{my_bal} BTC")
c2.metric("🔗 Blocks", len(bc.chain))
c3.metric("💸 Txs", len(st.session_state.txs))
c4.metric("🏦 Supply", f"{bc.mined}/21M")

tab1, tab2, tab3 = st.tabs(["⛏️ Mining", "💸 Send BTC", "🔍 Explorer"])

with tab1:
    st.subheader("⛏️ Mining - Real PoW 0000")
    if st.button("⛏️ MINE BLOCK (+50 BTC)", type="primary", use_container_width=True):
        with st.spinner("Mining block... finding 0000 hash..."):
            block = bc.mine(my_addr)
            if block:
                balances[my_addr]=balances.get(my_addr,0)+50
                st.balloons()
                st.success(f"Mined Block #{block['index']}")
                st.code(f"Hash: {block['hash']}\nNonce: {block['nonce']}\nPrev: {block['prev_hash'][:20]}...")
            else:
                st.error("Max supply reached!")

with tab2:
    st.subheader("💸 Send BTC")
    to_addr = st.text_input("To Address (vkt1...)", placeholder="vkt1...")
    amount = st.number_input("Amount", min_value=1, value=10, max_value=int(my_bal) if my_bal>0 else 1)
    if st.button("📤 Send Now", use_container_width=True):
        ok, result = create_transaction(my_addr, to_addr, amount, balances)
        if ok:
            st.session_state.txs.append(result)
            st.success(f"✅ Sent {amount} BTC to {get_short(to_addr)}")
            st.json(result)
        else:
            st.error(result)
    st.divider()
    st.write("**Recent Transactions**")
    for tx in reversed(st.session_state.txs[-10:]):
        st.write(f"📤 {tx['amount']} BTC | {get_short(tx['from'])} → {get_short(tx['to'])} | {tx['time']}")

with tab3:
    st.subheader("🔍 Blockchain Explorer - Verify Karo")
    for b in reversed(bc.chain[-10:]):
        with st.expander(f"Block #{b['index']} - {b['hash'][:16]}..."):
            st.json(b)
