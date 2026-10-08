import streamlit as st, hashlib, time, secrets, datetime, json, os, io, qrcode
from mnemonic import Mnemonic

st.set_page_config(page_title="BTC 2.0 Live Chat", page_icon="💬", layout="wide")

DB_FILE="vkt_real_chat_db.json"

def h(s): return hashlib.sha256(s.encode()).hexdigest()
def make_qr(t):
    qr=qrcode.QRCode(version=1,box_size=6,border=2); qr.add_data(t); qr.make(fit=True)
    img=qr.make_image(fill='black',back_color='white'); buf=io.BytesIO(); img.save(buf,format="PNG"); return buf.getvalue()
def wallet_from_phrase(p):
    x=h(p); return "bc1q"+x[:38], "5K"+h(x+"pk")[:49]
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"chain":[],"bal":{},"txs":[],"mined":0,"wallets":{},"public_chat":[]}
def save_db():
    d={"chain":st.session_state["chain"],"bal":st.session_state["bal"],"txs":st.session_state["txs"],"mined":st.session_state["mined"],"wallets":st.session_state["wallets"],"public_chat":st.session_state["public_chat"]}
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
def get_reward(): return max(50/(2**(len(st.session_state["chain"])//21)),0.5)
def get_bal(a): return st.session_state["bal"].get(a,0)

if "chain" not in st.session_state:
    db=load_db()
    st.session_state["chain"]=db.get("chain",[]); st.session_state["bal"]=db.get("bal",{}); st.session_state["txs"]=db.get("txs",[]); st.session_state["mined"]=db.get("mined",0); st.session_state["wallets"]=db.get("wallets",{}); st.session_state["public_chat"]=db.get("public_chat",[])
    if not st.session_state["wallets"]:
        m=Mnemonic("english"); ph=m.generate(strength=128); addr,pk=wallet_from_phrase(ph)
        st.session_state["addr"]=addr; st.session_state["pkey"]=pk; st.session_state["phrase"]=ph; st.session_state["bal"][addr]=1400; st.session_state["wallets"][addr]={"pkey":pk,"phrase":ph}; st.session_state["mined"]=1400; save_db()
    else:
        first=list(st.session_state["wallets"].keys())[0]; st.session_state["addr"]=first; st.session_state["pkey"]=st.session_state["wallets"][first]["pkey"]; st.session_state["phrase"]=st.session_state["wallets"][first].get("phrase","")

if "user_name" not in st.session_state:
    st.session_state["user_name"]=""

# Login
if st.session_state["user_name"]=="":
    st.title("💬 BTC 2.0 - Live Community Chat")
    st.markdown("### Apna naam likho taaki log aapas me baat kar saken")
    name=st.text_input("Aapka naam?", placeholder="Jaise: Ali, VKT, Ahmed")
    if st.button("✅ Chat me Jao", type="primary"):
        if name.strip()!="":
            st.session_state["user_name"]=name.strip()
            now=datetime.datetime.now().strftime("%I:%M %p")
            st.session_state["public_chat"].append({"user":"System","text":f"{name} joined the chat 🎉","time":now})
            save_db(); st.rerun()
    st.stop()

ht=len(st.session_state["chain"]); rw=get_reward(); my_bal=get_bal(st.session_state["addr"])

st.markdown("""
<style>
.stApp {background:#111b21;}
.msg {padding:8px 12px; border-radius:8px; margin:5px 0; max-width:80%;}
.me {background:#005c4b; color:white; margin-left:auto;}
.other {background:#202c33; color:white;}
.sys {background:#182533; color:#8696a0; text-align:center; font-size:12px; margin:10px auto; max-width:60%;}
</style>
""", unsafe_allow_html=True)

st.title(f"₿ BTC 2.0 | 💬 Live Chat - {st.session_state['user_name']}")
c1,c2,c3,c4=st.columns(4); c1.metric("Height",ht); c2.metric("Mined",st.session_state["mined"]); c3.metric("Reward",rw); c4.metric("Your BTC",f"{my_bal}")

tab1, tab2 = st.tabs(["⛏️ MINING", "💬 PUBLIC GROUP CHAT (Real)"])

with tab1:
    left,right=st.columns([1,1])
    with left:
        if st.button(f"🚀 MINE BLOCK #{ht+1} +{rw} BTC", type="primary", use_container_width=True):
            prev=st.session_state["chain"][-1]["hash"] if st.session_state["chain"] else "0"*64
            final="000"+h(secrets.token_hex(8))[3:]
            now=datetime.datetime.now().strftime("%I:%M %p")
            block={"height":ht+1,"hash":final,"prev":prev,"miner":st.session_state["addr"],"reward":rw,"nonce":1234,"time":now}
            st.session_state["chain"].append(block); st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])+rw; st.session_state["mined"]+=rw
            # Chat me bhi announce
            st.session_state["public_chat"].append({"user":"⛏️ MINING","text":f"{st.session_state['user_name']} ne Block #{ht+1} mine kiya! +{rw} BTC 🔥","time":now})
            save_db(); st.balloons(); st.rerun()
        st.code(st.session_state["addr"]); st.success(st.session_state["phrase"])
    with right:
        st.subheader("Live Chat Shortcut")
        st.info("Chat tab pe jao, wahan logon se baat karo. Wahan /mine likhoge to mining bhi hogi!")

with tab2:
    st.subheader(f"🌍 Public Group - {len(st.session_state['public_chat'])} messages - Sab log yahan baat karte hain")
    st.caption("Yahan jo likhoge wo sab users ko dikhega - Real time jaisa")

    chat_box=st.container(height=400)
    with chat_box:
        for m in st.session_state["public_chat"][-100:]:
            if m["user"]=="System" or m["user"]=="⛏️ MINING":
                st.markdown(f"<div class='msg sys'>{m['text']} - {m['time']}</div>", unsafe_allow_html=True)
            elif m["user"]==st.session_state["user_name"]:
                st.markdown(f"<div class='msg me'><b>You</b>: {m['text']}<div style='font-size:10px;text-align:right;'>{m['time']} ✅✅</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='msg other'><b style='color:#25D366;'>{m['user']}</b>: {m['text']}<div style='font-size:10px;text-align:right;color:#8696a0;'>{m['time']}</div></div>", unsafe_allow_html=True)

    col1,col2=st.columns([0.85,0.15])
    msg=st.chat_input(f"{st.session_state['user_name']} - Message likho...")
    if msg:
        now=datetime.datetime.now().strftime("%I:%M %p")
        st.session_state["public_chat"].append({"user":st.session_state["user_name"],"text":msg,"time":now})
        # Agar /mine likha to mine bhi karo
        if "/mine" in msg.lower():
            prev=st.session_state["chain"][-1]["hash"] if st.session_state["chain"] else "0"*64
            final="000"+h(secrets.token_hex(8))[3:]
            block={"height":len(st.session_state["chain"])+1,"hash":final,"prev":prev,"miner":st.session_state["addr"],"reward":rw,"nonce":1234,"time":now}
            st.session_state["chain"].append(block); st.session_state["bal"][st.session_state["addr"]]=get_bal(st.session_state["addr"])+rw; st.session_state["mined"]+=rw
            st.session_state["public_chat"].append({"user":"⛏️ MINING","text":f"{st.session_state['user_name']} ne /mine se Block mine kiya +{rw} BTC!","time":now})
        save_db(); st.rerun()

    if st.button("🔄 Refresh Chat (Naye messages dekho)"):
        st.session_state["chain"]=load_db().get("chain",st.session_state["chain"])
        st.session_state["public_chat"]=load_db().get("public_chat",st.session_state["public_chat"])
        st.rerun()
