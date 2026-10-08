import streamlit as st
import hashlib, time, secrets, datetime, json, os, io, qrcode
from mnemonic import Mnemonic

st.set_page_config(page_title="BTC 2.0 FULL", page_icon="₿", layout="wide")
DB_FILE = "btc_full_db.json"

# --- FUNCTIONS ---
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def make_qr(t):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(t); qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()
def wallet_from_phrase(p):
    x = h(p); return "bc1q"+x[:38], "5K"+h(x+"pk")[:49]
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"chain":[],"bal":{},"txs":[],"mined":0,"wallets":{},"chat":[]}
def save_db():
    d={"chain":st.session_state["chain"],"bal":st.session_state["bal"],"txs":st.session_state["txs"],"mined":st.session_state["mined"],"wallets":st.session_state["wallets"],"chat":st.session_state["chat"]}
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
def get_reward(): return max(50/(2**(len(st.session_state["chain"])//21)),0.5)
def get_bal(a): return st.session_state["bal"].get(a,0)

# --- LOAD ---
if "chain" not in st.session_state:
    db=load_db()
    st.session_state["chain"]=db.get("chain",[]); st.session_state["bal"]=db.get("bal",{}); st.session_state["txs"]=db.get("txs",[]); st.session_state["mined"]=db.get("mined",0); st.session_state["wallets"]=db.get("wallets",{}); st.session_state["chat"]=db.get("chat",[])
    if not st.session_state["wallets"]:
        m=Mnemonic("english"); ph=m.generate(strength=128); addr,pk=wallet_from_phrase(ph)
        st.session_state["addr"]=addr; st.session_state["pkey"]=pk; st.session_state["phrase"]=ph; st.session_state["bal"][addr]=1400; st.session_state["wallets"][addr]={"pkey":pk,"phrase":ph}; st.session_state["mined"]=1400; save_db()
    else:
        first=list(st.session_state["wallets"].keys())[0]; st.session_state["addr"]=first; st.session_state["pkey"]=st.session_state["wallets"][first]["pkey"]; st.session_state["phrase"]=st.session_state["wallets"][first].get("phrase","")
if "user_name" not in st.session_state: st.session_state["user_name"]=""

# --- LOGIN ---
if st.session_state["user_name"]=="":
    st.title("₿ BTC 2.0 - FULL NODE LOGIN")
    st.markdown("### Pehle naam likho - Phir Mining + Chat dono khulega")
    name=st.text_input("Aapka naam? (Ali, VKT)")
    if st.button("🚀 START BTC 2.0", type="primary", use_container_width=True):
        if name.strip()!="":
            st.session_state["user_name"]=name.strip(); st.rerun()
    st.stop()

ht=len(st.session_state["chain"]); rw=get_reward(); my_bal=get_bal(st.session_state["addr"])

st.markdown("<style>.stApp{background:#0b141a;}.msg-me{background:#005c4b;color:white;padding:8px 12px;border-radius:8px 0 8px 8px;margin:4px 0;max-width:75%;float:right;clear:both;}.msg-other{background:#202c33;color:white;padding:8px 12px;border-radius:0 8px 8px 8px;margin:4px 0;max-width:75%;float:left;clear:both;}.time{font-size:10px;color:#8696a0;text-align:right;}</style>", unsafe_allow_html=True)

st.title(f"₿ BTC 2.0 FULL - {st.session_state['user_name']}")
c1,c2,c3,c4=st.columns(4); c1.metric("Height",ht); c2.metric("Mined",f'{st.session_state["mined"]} / 21M'); c3.metric("Reward",f"{rw} BTC"); c4.metric("YOUR BALANCE",f"{my_bal} BTC")
st.progress(min(st.session_state["mined"]/21000000,1.0))

tab1, tab2, tab3 = st.tabs(["⛏️ MINING & SEND", "👛 WALLET (QR)", "💬 LIVE CHAT - LOG APAS ME"])

with tab1:
    l,r=st.columns([1.2,1])
    with l:
        st.subheader("⛏️ MINING ENGINE")
        if st.button(f"🚀 MINE BLOCK #{ht+1} - EARN {rw} BTC", type="primary", use_container_width=True):
            prev=st.session_state["chain"][-1]["hash"] if st.session_state["chain"] else "0"*64; nonce=0; final=None
            bar=st.progress(0,text="Mining...")
            for i in range(200000):
                hh=h(f"{ht}{prev}{st.session_state['addr']}{nonce}{time.time()}")
                if hh.startswith("000"): final=hh; break
                nonce+=1
                if i%40000==0: bar.progress(i/200000)
            if not final: final="000"+h(secrets.token_hex(8))[3:]
            block={"height":ht+1,"hash":final,"prev":prev,"miner":st.session_state["addr"],"reward":rw,"nonce":nonce,"time":datetime.datetime.now().strftime("%H:%M:%S")}
            st.session_state["chain"].append(block); st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])+rw; st.session_state["mined"]+=rw
            now=datetime.datetime.now().strftime("%I:%M %p")
            st.session_state["chat"].append({"user":"⛏️ SYSTEM","text":f"{st.session_state['user_name']} ne Block #{ht+1} mine kiya +{rw} BTC","time":now})
            save_db(); st.balloons(); st.rerun()

        st.subheader("💸 SEND BTC")
        with st.container(border=True):
            to_addr=st.text_input("To Address bc1q..."); amount=st.number_input("Amount BTC", min_value=0.0, step=1.0)
            if st.button("📤 SEND NOW", use_container_width=True):
                if get_bal(st.session_state["addr"])<amount: st.error("Balance kam hai")
                elif amount<=0: st.error("Amount > 0")
                else:
                    st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])-amount; st.session_state["bal"][to_addr]=get_bal(to_addr)+amount
                    txid=h(f"{st.session_state['addr']}{to_addr}{amount}{time.time()}")[:64]
                    st.session_state["txs"].append({"from":st.session_state["addr"],"to":to_addr,"amount":amount,"time":datetime.datetime.now().strftime("%H:%M:%S"),"txid":txid}); save_db(); st.success(f"Sent {amount} BTC - TXID: {txid[:12]}.."); st.rerun()

        st.subheader("📜 Last Blocks")
        for b in reversed(st.session_state["chain"][-8:]):
            st.code(f"#{b['height']} {b['hash'][:24]} +{b['reward']} {b['miner'][:10]}..")

    with r:
        with st.container(border=True):
            st.write(f"**Miner:** {st.session_state['user_name']}"); st.write(f"**Address:** {st.session_state['addr'][:20]}.."); st.write(f"**Balance:** {my_bal} BTC")

with tab2:
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Address"); st.code(st.session_state["addr"]); st.image(make_qr(st.session_state["addr"]),width=250,caption="Address QR")
        st.subheader("Private Key"); st.code(st.session_state["pkey"]); st.image(make_qr(st.session_state["pkey"]),width=200,caption="Private Key QR")
    with c2:
        st.subheader("12 Word Phrase (BIP39)"); st.success(st.session_state["phrase"]); st.image(make_qr(st.session_state["phrase"]),width=250,caption="Phrase QR - BlueWallet Import")
        st.divider()
        if st.button("➕ New Wallet (1400 BTC Free)", use_container_width=True):
            m=Mnemonic("english"); ph=m.generate(strength=128); addr,pk=wallet_from_phrase(ph)
            st.session_state["wallets"][addr]={"pkey":pk,"phrase":ph}; st.session_state["addr"]=addr; st.session_state["pkey"]=pk; st.session_state["phrase"]=ph
            if addr not in st.session_state["bal"]: st.session_state["bal"][addr]=0
            save_db(); st.rerun()
        st.download_button("📥 Export Wallet JSON", json.dumps({"address":st.session_state["addr"],"pkey":st.session_state["pkey"],"phrase":st.session_state["phrase"],"balance":my_bal},indent=2), file_name="btc_wallet.json", use_container_width=True)

with tab3:
    st.subheader("🌍 BTC 2.0 Public Chat - Sab log yahan baat karte hain")
    st.caption("Yahan likho to sabko dikhega. /mine likho to mining bhi hogi chat se!")

    box=st.container(height=400)
    with box:
        for m in st.session_state["chat"][-100:]:
            if "SYSTEM" in m["user"]:
                st.markdown(f"<div style='background:#182533;color:#25D366;text-align:center;padding:6px;border-radius:8px;margin:6px auto;max-width:80%;font-size:13px;'>{m['text']} - {m['time']}</div>", unsafe_allow_html=True)
            elif m["user"]==st.session_state["user_name"]:
                st.markdown(f"<div class='msg-me'>{m['text']}<div class='time'>{m['time']} ✅✅</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='msg-other'><b style='color:#25D366;'>{m['user']}</b>: {m['text']}<div class='time'>{m['time']}</div></div>", unsafe_allow_html=True)

    msg=st.chat_input(f"{st.session_state['user_name']} message likho... ( /mine = mining )")
    if msg:
        now=datetime.datetime.now().strftime("%I:%M %p")
        st.session_state["chat"].append({"user":st.session_state["user_name"],"text":msg,"time":now})
        if "/mine" in msg.lower():
            prev=st.session_state["chain"][-1]["hash"] if st.session_state["chain"] else "0"*64
            final="000"+h(secrets.token_hex(8))[3:]
            block={"height":len(st.session_state["chain"])+1,"hash":final,"prev":prev,"miner":st.session_state["addr"],"reward":rw,"nonce":1234,"time":now}
            st.session_state["chain"].append(block); st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])+rw; st.session_state["mined"]+=rw
            st.session_state["chat"].append({"user":"⛏️ SYSTEM","text":f"{st.session_state['user_name']} ne CHAT se /mine kiya +{rw} BTC - Balance {get_bal(st.session_state['addr'])}","time":now})
        save_db(); st.rerun()

    if st.button("🔄 Chat Refresh"):
        db=load_db(); st.session_state["chat"]=db.get("chat",[]); st.session_state["chain"]=db.get("chain",[]); st.rerun()
