import streamlit as st
import hashlib
import time
import json
import os

# --- File se data load karo taake band na ho ---
DB_FILE = "btc_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"blocks": [], "wallets": {}}

def save_data(blocks, wallets):
    with open(DB_FILE, "w") as f:
        json.dump({"blocks": blocks, "wallets": wallets}, f)

data = load_data()

if "blocks" not in st.session_state:
    st.session_state.blocks = data["blocks"]
if "wallets" not in st.session_state:
    st.session_state.wallets = data["wallets"]

st.set_page_config(page_title="BTC 2.0 PERMANENT", page_icon="₿")
st.title("₿ BTC 2.0 PERMANENT")
st.caption("PERMANENT LIVE - Anyone can mine")

# --- Wallet System ---
st.sidebar.header("👛 My Wallet")
wallet_address = st.sidebar.text_input("Apna Wallet Name Likho", value="bigol_wallet", placeholder="jaise: Ali_Wallet")

if wallet_address not in st.session_state.wallets:
    st.session_state.wallets[wallet_address] = 0

balance = st.session_state.wallets[wallet_address]
st.sidebar.metric("Your Balance", f"{balance} BTC 2.0")

st.write(f"**Blocks:** {len(st.session_state.blocks)}")
st.write(f"**Your Wallet:** `{wallet_address}` | **Balance:** `{balance} BTC 2.0`")

# --- Mining ---
REWARD = 10 # Har block pe 10 BTC 2.0

if st.button(f"⛏️ MINE BTC 2.0 BLOCK (+{REWARD} BTC)", use_container_width=True):
    prev_hash = st.session_state.blocks[-1]["hash"] if st.session_state.blocks else "0"*64
    block_num = len(st.session_state.blocks) + 1

    block_data = f"{block_num}{prev_hash}{wallet_address}{time.time()}"
    block_hash = hashlib.sha256(block_data.encode()).hexdigest()

    new_block = {
        "number": block_num,
        "miner": wallet_address,
        "hash": block_hash,
        "prev_hash": prev_hash,
        "time": time.strftime("%H:%M:%S %d-%m-%Y")
    }

    st.session_state.blocks.append(new_block)
    st.session_state.wallets[wallet_address] += REWARD

    save_data(st.session_state.blocks, st.session_state.wallets)

    st.success(f"Block #{block_num} Mined! +{REWARD} BTC 2.0 Added to {wallet_address}")
    st.balloons()
    time.sleep(1)
    st.rerun()

# --- Transaction (BTC bhejo) ---
st.sidebar.divider()
st.sidebar.header("💸 Send BTC 2.0")
to_address = st.sidebar.text_input("Kisko bhejna hai?")
amount = st.sidebar.number_input("Kitna bhejna hai?", min_value=1, step=1)

if st.sidebar.button("Send"):
    if to_address == "":
        st.sidebar.error("Wallet name likho!")
    elif amount > st.session_state.wallets[wallet_address]:
        st.sidebar.error("Balance kam hai!")
    else:
        if to_address not in st.session_state.wallets:
            st.session_state.wallets[to_address] = 0
        st.session_state.wallets[wallet_address] -= amount
        st.session_state.wallets[to_address] += amount
        save_data(st.session_state.blocks, st.session_state.wallets)
        st.sidebar.success(f"{amount} BTC {to_address} ko bhej diya!")
        st.rerun()

# --- Blockchain Display ---
st.divider()
for block in reversed(st.session_state.blocks[-50:]): # Last 50 blocks
    st.info(f"**#{block['number']} - Mined by: {block['miner']} | +{REWARD} BTC**\n\nHash: {block['hash'][:20]}...\n\nTime: {block['time']}")

st.divider()
st.write("### 🏆 Top Miners (Rich List)")
sorted_wallets = sorted(st.session_state.wallets.items(), key=lambda x: x[1], reverse=True)
for name, bal in sorted_wallets[:10]:
    st.write(f"**{name}**: {bal} BTC 2.0")
