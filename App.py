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
    # BTC like address from private key
    pub = hashlib.sha256(priv.encode()).hexdigest()
    ripemd = hashlib.sha256(pub.encode()).hexdigest()
    address = "bc1q" + ripemd[:38] # BTC Bech32 like
    wif = "5" + hashlib.sha256(priv.encode()).hexdigest()[:50]
    return address, wif, priv

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                d=json.load(f)
                return d["blocks"], d["wallets"], d["keys"], d["mempool"], d["mined"]
        except: pass
    g_hash = hashlib.sha256("BTC 2.0 GENESIS".encode()).hexdigest()
    genesis = [{"number":0,"miner":"Satoshi","hash":g_hash,"prev_hash":"0"*64,"nonce":0,"reward":0,"time":"GENESIS"}]
    return genesis, {}, {}, [], 0

def save_db(b,w,k,m,mi):
    with open(DB_FILE,"w") as f:
        json.dump({"blocks":b,"wallets":w,"keys":k,"mempool":m,"mined":mi},f)

blocks,wallets,keys,mempool,total_mined = load_db()

if "init" not in st.session_state:
    st.session_state.blocks=blocks
    st.session_state.wallets=wallets
    st.session_state.keys=keys
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
    st.error("21M REACHED - NO MORE BTC LIKE REAL BITCOIN")
    st.stop()

# Wallet System Like Real BTC
st.sidebar.header("👛 BTC Wallet - Like Real BTC")

if "my_address" not in st.session_state:
    addr,wif,priv = generate_btc_wallet()
    st.session_state.my_address=addr
    st.session_state.my_wif=wif
    st.session_state.my_priv=priv
    st.session_state.wallets[addr]=st.session_state.wallets.get(addr,0)
    st.session_state.keys[addr]=wif

my_address = st.sidebar.text_input("Your BTC Address", value=st.session_state.my_address)

if my_address not in st.session_state.wallets:
    st.session_state.wallets[my_address]=0

st.sidebar.info(f"**Address:**\n{my_address}\n\n**Private Key (SECRET - Kisi ko mat dena):**\n{st.session_state.keys.get(my_address, st.session_state.my_wif)}")
st.sidebar.metric("Balance", f"{st.session_state.wallets[my_address]:,.2f} BTC 2.0")

if st.sidebar.button("Generate NEW Wallet (Like New BTC Wallet)"):
    addr,wif,priv = generate_btc_wallet()
    st.session_state.my_address=addr
    st.session_state.my_wif=wif
    st.session_state.wallets[addr]=0
    st.session_state.keys[addr]=wif
    save_db(st.session_state.blocks, st.session_state.wallets, st.session_state.keys, st.session_state.mempool, st.session_state.total_mined)
    st.rerun()

# Send
st.sidebar.divider()
st.sidebar.subheader("Send BTC")
to = st.sidebar.text_input("To bc1q Address")
amt = st.sidebar.number_input("Amount", min_value=0.0, step=1.0)
if st.sidebar.button("Send"):
    if to not in st.session_state.wallets:
        st.session_state.wallets[to]=0
    if amt > st.session_state.wallets[my_address]:
        st.sidebar.error("Low Balance")
    else:
        st.session_state.wallets[my_address]-=amt
        st.session_state.wallets[to]+=amt
        st.session_state.mempool.append({"from":my_address[:15]+"...","to":to[:15]+"...","amount":amt,"time":time.strftime("%H:%M:%S")})
        save_db(st.session_state.blocks, st.session_state.wallets, st.session_state.keys, st.session_state.mempool, st.session_state.total_mined)
        st.sidebar.success("Sent!")
        st.rerun()

# Mining
if st.button(f"⛏️ MINE BLOCK - EARN {reward} BTC", use_container_width=True, type="primary"):
    with st.spinner("POW Mining..."):
        prev=st.session_state.blocks[-1]["hash"]
        nonce=0
        while True:
            h=hashlib.sha256(f"{total_blocks+1}{prev}{my_address}{nonce}{time.time()}".encode()).hexdigest()
            if h.startswith("0"*DIFFICULTY): break
            nonce+=1
        block={"number":total_blocks+1,"miner":my_address,"hash":h,"prev_hash":prev,"nonce":nonce,"reward":reward,"time":time.strftime("%H:%M:%S %d-%m-%Y")}
        st.session_state.blocks.append(block)
        st.session_state.wallets[my_address]+=reward
        st.session_state.total_mined+=reward
        save_db(st.session_state.blocks, st.session_state.wallets, st.session_state.keys, st.session_state.mempool, st.session_state.total_mined)
        st.success(f"MINED #{block['number']} Hash {h} Nonce {nonce}")
        st.balloons()
        time.sleep(1)
        st.rerun()

# Explorer
l,r=st.columns([2,1])
with l:
    st.subheader("Blockchain")
    for b in reversed(st.session_state.blocks[-15:]):
        st.code(f"Block #{b['number']} | Miner {b['miner'][:20]}... | {b['reward']} BTC\nHash {b['hash']}\nNonce {b['nonce']} Time {b['time']}")

with r:
    st.subheader("Rich List")
    for i,(a,b) in enumerate(sorted(st.session_state.wallets.items(), key=lambda x:x[1], reverse=True)[:15],1):
        st.write(f"{i}. {a[:12]}... : {b:.2f} BTC")
    st.write(f"**Max Supply:** 21M\n**Halving:** Every {HALVING_INTERVAL}\n**Reward Now:** {reward}\n**Difficulty:** {DIFFICULTY}\n**Wallets:** BTC bech32 bc1q...")
