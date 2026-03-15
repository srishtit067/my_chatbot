import streamlit as st
from groq import Groq
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .main { background-color: #0f172a; }
    h1 { color: #e2e8f0 !important; text-align: center; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    .stButton > button { background-color: #6366f1; color: white; border: none; border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    else:
        st.success("API key loaded ✅")
    st.divider()
    model = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"], index=0)
    max_tokens = st.slider("Max tokens", 256, 4096, 1024, step=128)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, step=0.05)
    st.divider()
    system_prompt = st.text_area("System Prompt", value="You are a helpful, friendly, and concise AI assistant.", height=120)
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 AI Chatbot")
st.caption("Powered by Groq (Free) · Built with Streamlit")
st.divider()

for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message…"):
    if not api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_prompt},
                          *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.messages.pop()
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": full_response})
