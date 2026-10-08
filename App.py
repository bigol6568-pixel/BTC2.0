import streamlit as st
import hashlib
import time
import secrets

st.set_page_config(page_title="Bitcoin 2.0", page_icon="₿", layout="wide")

# --- BTC RULES ---
MAX_SUPPLY = 21000000
START_REWARD = 50
HALVING = 21

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def new_address():
    rnd = secrets.token_hex(16)
    h = sha256(rnd)
    addr = "bc1q" + h[:38]
    priv = "5" + sha256(h)[:50]
    return addr, priv

# --- INIT ---
if "chain" not in st.session_state:
    st.session_state.chain = []
    st.session_state.balances = {}
    st.session_state.mined = 0
    genesis_addr, genesis_priv = new_address()
    st.session_state.my_addr = genesis_addr
    st.session_state.my_priv = genesis_priv
    st.session_state.balances[genesis_addr] = 0

# --- CALCULATIONS ---
height = len(st.session_state.chain)
halvings = height // HALVING
reward = START_REWARD / (2 ** halvings)
if reward < 1:
    reward = 1
left = MAX_SUPPLY - st.session_state.mined

# --- UI ---
st.title("₿ BITCOIN 2.0 - Same as Real BTC")
st.write("Real Bitcoin jaisa - 21M Supply | Halving | bc1q Address | Private Key")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Block Height", height)
c2.metric("Mined", f"{st.session_state.mined} / 21M")
c3.metric("Reward", f"{reward} BTC")
c4.metric("Left", f"{left:,}")

st.progress(st.session_state.mined / MAX_SUPPLY if MAX_SUPPLY > 0 else 0, text=f"{left:,} BTC mining ke liye baki")

if left <= 0:
    st.error("21 MILLION REACHED - Mining Band - Jaise Real BTC me")
    st.stop()

# Sidebar Wallet
st.sidebar.header("₿ My Bitcoin Wallet")
my_addr = st.sidebar.text_input("Your Address (bc1q...)", value=st.session_state.my_addr)

if my_addr not in st.session_state.balances:
    st.session_state.balances[my_addr] = 0

st.sidebar.metric("Balance", f"{st.session_state.balances.get(my_addr,0)} BTC")
st.sidebar.text_area("Address (Public):", value=my_addr, height=68)
st.sidebar.text_area("Private Key WIF (Secret):", value=st.session_state.my_priv, height=80)
st.sidebar.warning("Private Key kisi ko mat do!")

if st.sidebar.button("Generate New Wallet"):
    addr, priv = new_address()
    st.session_state.my_addr = addr
    st.session_state.my_priv = priv
    st
