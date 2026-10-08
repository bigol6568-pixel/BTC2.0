import streamlit as st
import hashlib
import time
import json
import os
import secrets

MAX_SUPPLY = 21000000
GENESIS_REWARD = 50
HALVING_INTERVAL = 21
DIFFICULTY = 3
DB_FILE = "btc_final_v3.json"

def generate_btc_wallet():
    priv = secrets.token_hex(32)
    pub = hashlib.sha256(priv.encode()).hexdigest()
    ripemd = hashlib.sha256(pub.encode()).hexdigest()
    address = "bc1q" + ripemd[:38]
    wif = "5" + hashlib.sha256(priv.encode()).hexdigest()[:50]
    return address, wif

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                d=json.load(f)
                return d["blocks"], d["wallets"], d["priv_keys"], d["mempool"], d["mined"]
        except: pass
    g_hash = hashlib.sha256("BTC 2.0 GENESIS".encode()).hexdigest()
    genesis = [{"number":0,"miner":"Satoshi","hash":g_hash,"prev_hash":"0"*64,"nonce":0,"reward":0,"time":"GENESIS"}]
    return genesis, {}, {}, [], 0

def save_db(b,w,k,m,mi):
    with open(DB_FILE,"w") as f:
        json.dump({"blocks":b,"wallets":w,"priv_keys":k,"mempool":m,"mined":mi},f)

blocks,wallets,priv_keys,mempool,total_mined = load_db()

if "init" not in st.session_state:
    st.session_state.blocks=blocks
    st.session_state.wallets=wallets
    st.session_state.priv_keys=priv_keys
    st.session_state.mempool=mempool
    st.session_state.total_mined=total_mined
    st.session_state.init=True

st.set_page_config(page_title="BTC 2.0 Real", page_icon="₿", layout="wide")
st.title("₿ BTC 2.0 - SAME AS BITCOIN")

total_blocks=len(st.session_state.blocks)-1
halvings=total_blocks//HALVING_INTERVAL
reward=GENESIS_REWARD/(2**halvings)
if reward<1: reward=1
remaining=MAX_SUPPLY-st.session_state.total_mined
next_halving=HALVING_INTERVAL-(total_blocks%HALVING_INTERVAL)

c1,c2,c3,c4=st.columns(4)
c1.metric("Supply Mined", f"{st.session_state.total_mined:,}/21M")
c2.metric("Reward", f"{reward} BTC")
c3.metric("Next Halving", f"{next_halving} blocks")
c4.metric("Height", total_blocks)
st.progress(min((st.session_state.total_mined/MAX_SUPPLY),1.0), text=f"Remaining {remaining:,} BTC 2.0")

if remaining<=0:
    st.error("21M REACHED")
    st.stop()

# Wallet System
st.sidebar.header("👛 BTC Wallet")

if "my_address" not in st.session_state:
    addr,wif = generate_btc_wallet()
    st.session_state.my_address=addr
    st.session_state.my_wif=wif
    st.session_state.wallets[addr]=st.session_state.wallets.get(addr,0)
    st.session_state.priv_keys[addr]=wif

my_address = st.sidebar.text_input("Your BTC Address",
