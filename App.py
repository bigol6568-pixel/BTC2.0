import streamlit as st
import hashlib, time, secrets, datetime, json, os, io, qrcode
from mnemonic import Mnemonic

st.set_page_config(page_title="BTC 2.0 FULL", page_icon="₿", layout="wide")
DB_FILE = "btc_full_db.json"

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

if "chain" not in st.session_state:
    db=load_db()
    st.session_state["chain"]=db.get("chain",[]); st.session_state["bal"]=db.get("bal",{}); st.session_state["txs"]=db.get("txs",[]); st.session_state["mined"]=db.get("mined",0); st.session_state["wallets"]=db.get("wallets",{}); st.session_state["chat"]=db.get("chat",[])
    if not st.session_state["wallets"]:
        m=Mnemonic("english"); ph=m.generate(strength=128); addr,pk=wallet_from_phrase(ph)
        st.session_state["addr"]=addr; st.session_state["pkey"]=pk; st.session_state["phrase"]=ph; st.session_state["bal"][addr]=1400; st.session_state["mined"]=1400; st.session_state["wallets"][addr]={"pkey":pk,"phrase":ph}; save_db()
    else:
        first=list(st.session_state["wallets"].keys())[0]; st.session_state["addr"]=first; st.session_state["pkey"]=st.session_state["wallets"][first]["pkey"]; st.session_state["phrase"]=st.session_state["wallets"][first].get("phrase","")
if "user_name" not in st.session_state: st.session_state["user_name"]=""

if st.session_state["user_name"]=="":
    st.title("₿ BTC 2.0 - LOGIN")
    name=st.text_input("Aapka naam?")
    if st.button("START", type="primary", use_container_width=True):
        if name.strip()!="": st.session_state["user_name"]=name.strip(); st.rerun()
    st.stop()

ht=len(st.session_state["chain"]); rw=get_reward(); my_bal=get_bal(st.session_state["addr"])

st.markdown("<style>.stApp{background:#0b141a;}.msg-me{background:#005c4b;color:white;padding:8px 12px;border-radius:8px 0 8px 8px;margin:4px 0;max-width:75%;float:right;clear:both;}.msg-other{background:#202c33;color:white;padding:8px 12px;border-radius:0 8px 8px 8px;margin:4px 0;max-width:75%;float:left;clear:both;}.time{font-size:10px;color:#8696a0;text-align:right;}</style>", unsafe_allow_html=True)

st.title(f"₿ BTC 2.0 - {st.session_state['user_name']}")
c1,c2,c3,c4=st.columns(4); c1.metric("Height",ht); c2.metric("Mined",f'{st.session_state["mined"]} / 21M'); c3.metric("Reward",f"{rw} BTC"); c4.metric("YOUR BAL",f"{my_bal} BTC")

# YAHAN FIX HAI - 4 TABS SAHI SE
tab1, tab2, tab3, tab4 = st.tabs(["⛏️ MINING & SEND", "👛 WALLET", "💬 CHAT", "📹 VIDEO CALL"])

with tab1:
    l,r=st.columns([1.2,1])
    with l:
        st.subheader("⛏️ MINING")
        if st.button(f"🚀 MINE BLOCK #{ht+1} - {rw} BTC", type="primary", use_container_width=True):
            prev=st.session_state["chain"][-1]["hash"] if st.session_state["chain"] else "0"*64
            nonce=0; final="000"+h(secrets.token_hex(8))[3:]
            block={"height":ht+1,"hash":final,"prev":prev,"miner":st.session_state["addr"],"reward":rw,"nonce":nonce,"time":datetime.datetime.now().strftime("%H:%M:%S")}
            st.session_state["chain"].append(block); st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])+rw; st.session_state["mined"]+=rw
            st.session_state["chat"].append({"user":"⛏️ SYSTEM","text":f"{st.session_state['user_name']} ne Block #{ht+1} mine kiya +{rw} BTC","time":datetime.datetime.now().strftime("%I:%M %p")})
            save_db(); st.balloons(); st.rerun()
        st.subheader("💸 SEND BTC")
        to_addr=st.text_input("To Address bc1q..."); amount=st.number_input("Amount", min_value=0.0, step=1.0)
        if st.button("SEND NOW", use_container_width=True):
            if get_bal(st.session_state["addr"])<amount: st.error("Balance kam hai")
            elif amount>0:
                st.session_state["bal"][st.session_state["addr"]]-=amount; st.session_state["bal"][to_addr]=get_bal(to_addr)+amount; save_db(); st.success("Sent!"); st.rerun()
        st.subheader("Last Blocks")
        for b in reversed(st.session_state["chain"][-5:]):
            st.code(f"#{b['height']} {b['hash'][:20]} +{b['reward']}")
    with r:
        st.write(f"Miner: {st.session_state['user_name']}")
        st.write(f"Bal: {my_bal} BTC")

with tab2:
    st.code(st.session_state["addr"]); st.image(make_qr(st.session_state["addr"]), width=250)
    st.code(st.session_state["pkey"]); st.image(make_qr(st.session_state["phrase"]), width=250); st.success(st.session_state["phrase"])

with tab3:
    st.subheader("Live Chat")
    box=st.container(height=350)
    with box:
        for m in st.session_state["chat"][-80:]:
            if "SYSTEM" in m["user"]:
                st.markdown(f"<div style='text-align:center;color:#25D366;font-size:13px;'>{m['text']} - {m['time']}</div>", unsafe_allow_html=True)
            elif m["user"]==st.session_state["user_name"]:
                st.markdown(f"<div class='msg-me'>{m['text']}<div class='time'>{m['time']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='msg-other'><b style='color:#25D366;'>{m['user']}</b>: {m['text']}<div class='time'>{m['time']}</div></div>", unsafe_allow_html=True)
    msg=st.chat_input("Message likho...")
    if msg:
        now=datetime.datetime.now().strftime("%I:%M %p")
        st.session_state["chat"].append({"user":st.session_state["user_name"],"text":msg,"time":now})
        if "/mine" in msg.lower():
            final="000"+h(secrets.token_hex(8))[3:]; prev=st.session_state["chain"][-1]["hash"] if st.session_state["chain"] else "0"*64
            block={"height":len(st.session_state["chain"])+1,"hash":final,"prev":prev,"miner":st.session_state["addr"],"reward":rw,"nonce":1,"time":now}
            st.session_state["chain"].append(block); st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])+rw; st.session_state["mined"]+=rw
            st.session_state["chat"].append({"user":"⛏️ SYSTEM","text":f"{st.session_state['user_name']} ne /mine kiya +{rw} BTC","time":now})
        save_db(); st.rerun()

with tab4:
    st.subheader("📹 WhatsApp jaisi Video Call")
    room = st.text_input("Room ID banao", value="vkt-btc-123")
    name = st.session_state["user_name"]
    jitsi_url = f"https://meet.jit.si/{room}#userInfo.displayName='{name}'"
    st.link_button("📹 VIDEO CALL START", jitsi_url, use_container_width=True, type="primary")
    st.link_button("🎤 VOICE CALL", jitsi_url+"#config.startWithVideoMuted=true", use_container_width=True)
    st.success(f"Link: {jitsi_url}")
    wa_link = f"https://wa.me/?text=Video Call join karo: {jitsi_url}"
    st.link_button("📤 WhatsApp pe Share", wa_link, use_container_width=True)
