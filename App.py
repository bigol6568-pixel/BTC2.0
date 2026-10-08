# Tab 4 me ye add karo

tab1, tab2, tab3, tab4 = st.tabs(["⛏️ MINING", "👛 WALLET", "💬 CHAT", "📹 VIDEO CALL"])

with tab4:
    st.subheader("📹 WhatsApp jaisi Video Call - Live")
    st.info("2 log same room name likh ke Join karen - Video call start ho jayegi jaise WhatsApp!")
    
    try:
        from streamlit_webrtc import webrtc_streamer
        room = st.text_input("Room Name likho (jaise: vkt-room-123)", value="vkt-btc-room")
        st.caption(f"Apne dost ko bolo yehi naam likhe: {room} - Dono ka video connect ho jayega")
        
        if st.button("📹 Video Call JOIN Karo", type="primary", use_container_width=True):
            webrtc_streamer(key=room, video_processor_factory=None, 
                            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            st.success("Camera On! Dusre bande ka wait karo...")
            
        st.divider()
        st.markdown("""
        **Kaise use kare:**
        1. Room naam likho: `vkt-family`
        2. JOIN dabao - Camera on
        3. Dost ko same link bhejo + same room naam bolo
        4. Dost JOIN karega to dono ka video connect - WhatsApp jaisa!
        """)
        
    except:
        st.error("Video ke liye `streamlit-webrtc` install karna hai - requirements.txt me add karo")
        st.code("streamlit-webrtc\nav", language="text")
        # Fallback - Jitsi link
        room = st.text_input("Room Name", value="vktbtc123")
        jitsi_link = f"https://meet.jit.si/{room}"
        st.link_button(f"📹 {room} me Video Call Start Karo (Jitsi)", jitsi_link, use_container_width=True, type="primary")
        st.caption("Ye button dabao - Nayi window me WhatsApp jaisi HD video call khulegi, dost ko same link bhejo!")
