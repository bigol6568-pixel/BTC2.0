import streamlit as st, hashlib, time, secrets, datetime
st.set_page_config(page_title="BTC 2.0", page_icon="₿", layout="wide")
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def wallet():
    r=secrets.token_hex(16); x=h(r)
    return "bc1q"+x[:38], "5K"+h(x+"p")[:49]
if "chain" not in st.session_state:
    st.session_state.chain=[]; st.session_state.bal={}; st.session_state.txs=[]; st.session_state.mined=0
    a,p=wallet(); st.session_state.addr=a; st.session_state.priv=p; st.session_state.bal[a]=0; st.session_state.wallets={a:p}
def rew(): return max(50/(2**(len(st.session_state.chain)//21)),0.5)
def bal(a): return st.session_state.bal.get(a,0)
ht=len(st.session_state.chain); rw=rew(); left=21000000-st.session_state.mined
st.title("₿ BITCOIN 2.0 FULL")
c1,c2,c3,c4=st.columns(4)
c1.metric("Height",ht); c2.metric("Mined",f"{st.session_state.mined}/21M"); c3.metric("Reward",f"{rw}"); c4.metric("Left",f"{left:,.0f}")
st.progress(min(st.session_state.mined/21000000,1.0))
L,R=st.columns([1.2,1])
with L:
    st.subheader("⛏️ MINING")
    if st.button(f"🚀 MINE BLOCK #{ht+1} +{rw} BTC",type="primary",use_container_width=True):
        ph=st.session_state.chain[-1]["hash"] if st.session_state.chain else "0"*64
        n=0; fh=None
        with st.status("Mining..."):
            for i in range(300000):
                d=f"{ht}{ph}{st.session_state.addr}{n}{time.time()}"; hh=h(d)
                if hh.startswith("000"): fh=hh; break
                n+=1
            if not fh: fh="000"+h(secrets.token_hex(8))[3:]
            b={"height":ht+1,"hash":fh,"prev":ph,"miner":st.session_state.addr,"reward":rw,"nonce":n,"time":datetime.datetime.now().strftime("%H:%M:%S")}
            st.session_state.chain.append(b); st.session_state.bal[st.session_state.addr]=bal(st.session_state.addr)+rw; st.session_state.mined+=rw
            st.balloons(); st.rerun()
    st.subheader("💸 SEND")
    with st.container(border=True):
        fa=st.selectbox("From",list(st.session_state.wallets.keys())); st.write(f"Bal: {bal(fa)} BTC")
        ta=st.text_input("To bc1q..."); am=st.number_input("Amount",0.0,step=1.0)
        if st.button("📤 SEND",use_container_width=True):
            if not ta.startswith("bc1q"): st.error("bc1q address dalo")
            elif bal(fa)<am: st.error(f"Balance kam {bal(fa)}")
            elif am<=0: st.error("Amount >0")
            else:
                st.session_state.bal[fa]=bal(fa)-am; st.session_state.bal[ta]=bal(ta)+am
                tx={"from":fa,"to":ta,"amount":am,"time":datetime.datetime.now().strftime("%H:%M:%S"),"txid":h(f"{fa}{ta}{am}{time.time()}")[:64]}
                st.session_state.txs.append(tx); st.success(f"Sent {am} BTC"); st.rerun()
with R:
    st.subheader("👛 WALLET")
    with st.container(border=True):
        st.text_input("Address",value=st.session_state.addr); st.text_area("Private Key",value=st.session_state.priv,height=68)
        st.metric("Balance",f"{bal(st.session_state.addr)} BTC")
        if st.button("➕ New Wallet",use_container_width=True):
            a,p=wallet(); st.session_state.wallets[a]=p; st.session_state.addr=a; st.session_state.priv=p; st.session_state.bal[a]=0; st.rerun()
    st.subheader("📜 TXS")
    for t in reversed(st.session_state.txs[-10:]): st.code(f"{t['from'][:15]}->{t['to'][:15]} {t['amount']} BTC\n{t['txid'][:30]}")
st.divider()
st.subheader("🔗 BLOCKS")
if not st.session_state.chain: st.info("Mine karo!")
else:
    for b in reversed(st.session_state.chain[-10:]): st.success(f"#{b['height']} {b['hash'][:30]}... +{b['reward']} BTC Miner {b['miner'][:10]}... Nonce {b['nonce']}")
