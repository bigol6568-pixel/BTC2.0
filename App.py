import streamlit as st
import hashlib
import time
import secrets
import datetime
import json
import os
import io
import qrcode
from mnemonic import Mnemonic

st.set_page_config(page_title="BTC 2.0 FULL", page_icon="₿", layout="wide")
DB_FILE = "btc_database.json"

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def make_qr(text):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def wallet_from_phrase(phrase):
    x = h(phrase)
    addr = "bc1q" + x[:38]
    priv = "5K" + h(x + "p")[:49]
    return addr, priv

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"chain": [], "bal": {}, "txs": [], "mined": 0, "wallets": {}}

def save_db():
    data = {
        "chain": st.session_state.chain,
        "bal": st.session_state.bal,
        "txs": st.session_state.txs,
        "mined": st.session_state.mined,
        "wallets": st.session_state.wallets
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def get_reward():
    height = len(st.session_state.chain)
    return max(50 / (2 ** (height // 21)), 0.5)

def get_bal(addr):
    return st.session_state.bal.get(addr, 0)

if "chain" not in st.session_state:
    db = load_db()
    st.session_state.chain = db.get("chain", [])
    st.session_state.bal = db.get("bal", {})
    st.session_state.txs = db.get("txs", [])
    st.session_state.mined = db.get("mined", 0)
    st.session_state.wallets = db.get("wallets", {})

    if not st.session_state.wallets:
        mnemo = Mnemonic("english")
        phrase = mnemo.generate(strength=128)
        addr, priv = wallet_from_phrase(phrase)
        st.session_state.addr = addr
        st.session_state.priv = priv
        st.session_state.phrase = phrase
        st.session_state.bal[addr] = 1400
        st.session_state.wallets[addr] = {"priv": priv, "phrase": phrase}
        st.session_state.mined = 1400
        save_db()
    else:
        st.session_state.addr = list(st.session_state.wallets.keys())[0]
        st.session_state.priv = st.session_state.wallets[st.session_state.addr]["priv"]
        st.session_state.phrase = st.session_state.wallets[st.session_state.addr].get("phrase", "No phrase")

ht = len(st.session_state.chain)
rw = get_reward()
my_bal = get_bal(st.session_state.addr)

st.title("₿ BTC 2.0 - FULL FUTURE NODE")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Height", ht)
m2.metric("Mined", f"{st.session_state.mined} / 21M")
m3.metric("Reward", f"{rw} BTC")
m4.metric("MY BALANCE", f"{my_bal} BTC")

st.progress(min(st.session_state.mined / 21000000, 1.0))
left, right = st.columns([1.3, 1])

with left:
    st.subheader("⛏️ MINING")
    if st.button(f"🚀 MINE BLOCK #{ht+1} - EARN {rw} BTC", type="primary", use_container_width=True):
        prev_hash = st.session_state.chain[-1]["hash"] if st.session_state.chain else "0"*64
        nonce = 0
        final_hash = None
        bar = st.progress(0, text="Mining...")
        for i in range(300000):
            hh = h(f"{ht}{prev_hash}{st.session_state.addr}{nonce}{time.time()}")
            if hh.startswith("000"):
                final_hash = hh
                break
            nonce += 1
            if i % 30000 == 0:
                bar.progress(i/300000)
        if not final_hash:
            final_hash = "000" + h(secrets.token_hex(8))[3:]
        block = {"height": ht+1, "hash": final_hash, "prev": prev_hash, "miner": st.session_state.addr, "reward": rw, "nonce": nonce, "time": datetime.datetime.now().strftime("%H:%M:%S")}
        st.session_state.chain.append(block)
        st.session_state.bal[st.session_state.addr] = get_bal(st.session_state.addr) + rw
        st.session_state.mined += rw
        save_db()
        st.balloons()
        st.rerun()

    st.subheader("💸 SEND BTC")
    with st.container(border=True):
        to_addr = st.text_input("To Address bc1q...")
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        if st.button("📤 SEND NOW", use_container_width=True):
            if get_bal(st.session_state.addr) < amount:
                st.error("Balance kam hai")
            elif amount <= 0:
                st.error("Amount > 0 dalo")
            else:
                st.session_state.bal[st.session_state.addr] = get_bal(st.session_state.addr) - amount
                st.session_state.bal[to_addr] = get_bal(to_addr) + amount
                txid = h(f"{st.session_state.addr}{to_addr}{amount}{time.time()}")[:64]
                st.session_state.txs.append({"from": st.session_state.addr, "to": to_addr, "amount": amount, "time": datetime.datetime.now().strftime("%H:%M:%S"), "txid": txid})
                save_db()
                st.success(f"Sent {amount} BTC")
                st.rerun()

with right:
    st.subheader("👛 WALLET FULL")
    with st.container(border=True):
        st.write("**Address**")
        st.code(st.session_state.addr)
        st.image(make_qr(st.session_state.addr), width=200, caption="Address QR")
        st.write("**Private Key**")
        st.code(st.session_state.priv)
        st.image(make_qr(st.session_state.priv), width=150, caption="Private Key QR")
        st.write("**12 Word Phrase BIP39**")
        st.success(st.session_state.phrase)
        st.image(make_qr(st.session_state.phrase), width=150, caption="Phrase QR")
        st.write(f"Balance: {my_bal} BTC")
        sel = st.selectbox("Switch Wallet", list(st.session_state.wallets.keys()))
        if st.button("Switch Wallet"):
            st.session_state.addr = sel
            st.session_state.priv = st.session_state.wallets[sel]["priv"]
            st.session_state.phrase = st.session_state.wallets[sel].get("phrase", "")
            st.rerun()
        if st.button("➕ New Wallet", use_container_width=True):
            mnemo = Mnemonic("english")
            phrase = mnemo.generate(strength=128)
            addr, priv = wallet_from_phrase(phrase)
            st.session_state.wallets[addr] = {"priv": priv, "phrase": phrase}
            st.session_state.addr = addr
            st.session_state.priv = priv
            st.session_state.phrase = phrase
            if addr not in st.session_state.bal:
                st.session_state.bal[addr] = 0
            save_db()
            st.rerun()
        exp = json.dumps({"address": st.session_state.addr, "private_key": st.session_state.priv, "phrase": st.session_state.phrase}, indent=2)
        st.download_button("📥 Export JSON", exp, file_name="wallet.json", use_container_width=True)

    with st.container(border=True):
        st.subheader("📤 Import")
        imp_phrase = st.text_area("12 Word Phrase")
        if st.button("🔓 IMPORT", type="primary", use_container_width=True):
            try:
                phrase = imp_phrase.strip()
                mnemo = Mnemonic("english")
                if not mnemo.check(phrase):
                    st.error("Invalid phrase")
                else:
                    addr, priv = wallet_from_phrase(phrase)
                    st.session_state.wallets[addr] = {"priv": priv, "phrase": phrase}
                    st.session_state.addr = addr
                    st.session_state.priv = priv
                    st.session_state.phrase = phrase
                    if addr not in st.session_state.bal:
                        st.session_state.bal[addr] = 0
                    save_db()
                    st.success("Imported")
                    st.rerun()
            except Exception as e:
                st.error(f"Error {e}")

st.divider()
for b in reversed(st.session_state.chain[-10:]):
    st.code(f"BLOCK #{b['height']} {b['hash'][:22]} +{b['reward']} {b['miner'][:12]}")
