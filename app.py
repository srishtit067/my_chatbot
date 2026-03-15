import streamlit as st
from groq import Groq

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    h1 { color: #e2e8f0 !important; text-align: center; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    .stChatInputContainer textarea {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    .stButton > button {
        background-color: #6366f1;
        color: white;
        border: none;
        border-radius: 8px;
        width: 100%;
    }
    .stButton > button:hover { background-color: #4f46e5; }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    import os
api_key = os.environ.get("GROQ_API_KEY", "")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your FREE key at https://console.groq.com",
    )

    st.divider()
    st.subheader("Model")
    model = st.selectbox(
        "Choose model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        index=0,
    )

    st.subheader("Parameters")
    max_tokens = st.slider("Max tokens", 256, 4096, 1024, step=128)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, step=0.05)

    st.divider()
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "Persona / instructions",
        value="You are a helpful, friendly, and concise AI assistant.",
        height=120,
    )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        msg_count = len(st.session_state.get("messages", []))
        st.metric("Messages", msg_count)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 AI Chatbot")
st.caption("Powered by Groq (Free) · Built with Streamlit")
st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your message…"):

    if not api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar. Get one FREE at https://console.groq.com")
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Stream assistant response
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            client = Groq(api_key=api_key)

            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages],
                ],
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
            err = str(e)
            if "invalid_api_key" in err.lower() or "401" in err:
                st.error("❌ Invalid API key. Check your Groq key and try again.")
            elif "rate_limit" in err.lower() or "429" in err:
                st.error("⏳ Rate limit reached. Wait a moment and retry.")
            else:
                st.error(f"Something went wrong: {e}")
            st.session_state.messages.pop()
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": full_response})
