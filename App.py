import streamlit as st, hashlib, time, secrets, datetime, json, os, io
import qrcode
from mnemonic import Mnemonic
import bip32utils
import hashlib
from bech32 import bech32_encode, convertbits

st.set_page_config(page_title="BTC 2.0 REAL BIP39", page_icon="₿", layout="wide")
DB_FILE = "btc_database.json"

def h(s): return hashlib.sha256(s.encode()).hexdigest()

def make_qr(text):
    qr=qrcode.QRCode(version=1,box_size=6,border=2)
    qr.add_data(text); qr.make(fit=True)
    img=qr.make_image(fill='black',back_color='white')
    buf=io.BytesIO(); img.save(buf,format="PNG")
    return buf.getvalue()

def bip39_to_btc_address(mnemonic_phrase):
    # BIP39 -> Seed
    mnemo = Mnemonic("english")
    seed = mnemo.to_seed(mnemonic_phrase, passphrase="")

    # BIP32 Root
    root_key = bip32utils.BIP32Key.fromEntropy(seed)

    # BIP84 Path: m/84'/0'/0'/0/0 (Native SegWit bc1q)
    # 84' = 0x80000000 + 84
    purpose = root_key.ChildKey(84 + bip32utils.BIP32_HARDEN)
    coin = purpose.ChildKey(0 + bip32utils.BIP32_HARDEN)
    account = coin.ChildKey(0 + bip32utils.BIP32_HARDEN)
    change = account.ChildKey(0)
    addr_key = change.ChildKey(0)

    # Get pubkey and create bc1q address
    pubkey = addr_key.PublicKey()
    # HASH160
    sha = hashlib.sha256(pubkey).digest()
    import hashlib
    try:
        rip = hashlib.new('ripemd160', sha).digest()
    except:
        from Crypto.Hash import RIPEMD160
        rip = RIPEMD160.new(sha).digest()

    # bech32 encode bc1q
    hrp = "bc"
    witver = 0
    data = convertbits(rip, 8, 5)
    bech32_addr = bech32_encode(hrp, [witver] + data)

    # Private Key WIF
    wif = addr_key.WalletImportFormat()

    return bech32_addr, wif

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE,"r") as f: return json.load(f)
        except: pass
    return {"chain":[],"bal":{},"txs":[],"mined":0,"wallets":{}}

def save_db():
    data={"chain":st.session_state.chain,"bal":st.session_state.bal,"txs":st.session_state.txs,"mined":st.session_state.mined,"wallets":st.session_state.wallets}
    with open(DB_FILE,"w") as f: json.dump(data,f)

if "chain" not in st.session_state:
    db=load_db()
    st.session_state.chain=db.get("chain",[]); st.session_state.bal=db.get("bal",{}); st.session_state.txs=db.get("txs",[]); st.session_state.mined=db.get("mined",0); st.session_state.wallets=db.get("wallets",{})
    if not st.session_state.wallets:
        mnemo = Mnemonic("english")
        phrase = mnemo.generate(strength=128) # 12 words
        addr, wif = bip39_to_btc_address(phrase)
        st.session_state.addr=addr; st.session_state.priv=wif; st.session_state.phrase=phrase
        st.session_state.bal[addr]=0; st.session_state.wallets[addr]={"priv":wif,"phrase":phrase}
        save_db()
    else:
        st.session_state.addr=list(st.session_state.wallets.keys())[0]
        st.session_state.priv=st.session_state.wallets[st.session_state.addr]["priv"]
        st.session_state.phrase=st.session_state.wallets[st.session_state.addr].get("phrase","old")

def rew
