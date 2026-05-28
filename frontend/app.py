import streamlit as st
import requests
import json
import os
import uuid

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Airtel AI Assistant",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# LOAD CSS
# FIX 1 & 2: file now lives next to app.py;
#   __file__ makes the path work regardless of
#   which directory `streamlit run` is called from.
# ─────────────────────────────────────────────
def load_css() -> None:
    """Inject style.css (lives in the same folder as app.py)."""
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(
            f"⚠️ style.css not found at `{css_path}`. "
            "Place style.css in the same folder as app.py."
        )

load_css()

CHAT_FILE = "chat_history.json"

# ─────────────────────────────────────────────
# LOAD CHAT HISTORY
# ─────────────────────────────────────────────
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        chat_sessions = json.load(f)
else:
    chat_sessions = {}


def save_chats() -> None:
    with open(CHAT_FILE, "w") as f:
        json.dump(chat_sessions, f, indent=4)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">📡</div>
            <div>
                <div class="sidebar-brand-text">Airtel AI</div>
                <div class="sidebar-brand-sub">FAQ Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # New Chat button
    if st.button("New Chat", key="new_chat_btn"):
        chat_id = str(uuid.uuid4())[:8]
        chat_sessions[chat_id] = {"title": "New Chat", "messages": []}
        save_chats()
        st.session_state.current_chat = chat_id
        st.rerun()

    # ── Initialize current chat ──
    if "current_chat" not in st.session_state:
        if chat_sessions:
            st.session_state.current_chat = list(chat_sessions.keys())[-1]
        else:
            chat_id = str(uuid.uuid4())[:8]
            chat_sessions[chat_id] = {"title": "New Chat", "messages": []}
            save_chats()
            st.session_state.current_chat = chat_id

    # Guard: selected chat may have been deleted externally
    if st.session_state.current_chat not in chat_sessions:
        st.session_state.current_chat = list(chat_sessions.keys())[-1]

    # ── Section label ──
    st.markdown(
        '<div class="sidebar-section-label">Recent Chats</div>',
        unsafe_allow_html=True,
    )

    # ── Chat list (newest first) ──
    for cid in reversed(list(chat_sessions.keys())):
        title = chat_sessions[cid]["title"]
        is_active = cid == st.session_state.current_chat
        label = f"{'▸  ' if is_active else '💬  '}{title}"
        if st.button(label, key=f"chat_{cid}"):
            st.session_state.current_chat = cid
            st.rerun()

    # Footer
    st.markdown(
        """
        <div style="position:absolute;bottom:20px;left:14px;right:14px;
                    font-size:11px;color:#333345;text-align:center;
                    border-top:1px solid rgba(255,255,255,0.04);padding-top:12px;">
            Powered by Gemma · Ollama · FAISS
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# CURRENT CHAT DATA
# ─────────────────────────────────────────────
current_chat = chat_sessions[st.session_state.current_chat]
messages = current_chat["messages"]

# ─────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-title"><span>Airtel</span> FAQ Assistant</div>
        <div class="topbar-badge">● Live</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# CHAT MESSAGES  or  WELCOME SCREEN
# ─────────────────────────────────────────────
if not messages:
    st.markdown(
        """
        <div class="welcome-wrap">
            <div class="welcome-icon">📡</div>
            <div class="welcome-title">Hello! I'm your <span>Airtel</span> Assistant</div>
            <div class="welcome-sub">
                Ask me anything about Airtel plans, recharges, broadband,
                DTH, international roaming, or account support.
            </div>
            <div class="suggestion-chips">
                <div class="chip">📶 Best prepaid plans</div>
                <div class="chip">🌍 International roaming</div>
                <div class="chip">📺 DTH packages</div>
                <div class="chip">🔁 Port my number</div>
                <div class="chip">🏠 Airtel Xstream Fiber</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for msg in messages:
        avatar = "" if msg["role"] == "user" else "📡"
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
query = st.chat_input("Ask about plans, recharge, broadband, DTH…")

if query:
    # Update title on first message
    if current_chat["title"] == "New Chat":
        current_chat["title"] = query[:30] + ("…" if len(query) > 30 else "")

    # ── Render user message ──
    with st.chat_message("user", avatar="🧑"):
        st.markdown(query)

    # FIX 3: snapshot history BEFORE appending the new user message
    #   so the current question is NOT duplicated inside `history`.
    #   We send the last 6 *previous* turns as context.
    recent_history = messages[-6:]

    # Now append the user message to the in-memory list
    messages.append({"role": "user", "content": query})

    # ── Get + render assistant response ──
    with st.chat_message("assistant", avatar="📡"):
        with st.spinner("Searching knowledge base…"):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={
                        "question": query,
                        "history": recent_history,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]

            except requests.exceptions.ConnectionError:
                answer = (
                    " **Connection error** – the backend server isn't reachable. "
                    "Please make sure FastAPI is running on `localhost:8000`."
                )
            except requests.exceptions.Timeout:
                answer = " **Timeout** – the backend took too long to respond. Please try again."
            except requests.exceptions.HTTPError as exc:

                status_code = (
                exc.response.status_code
                if exc.response else "Unknown"
                )

                error_text = (
                exc.response.text
                if exc.response else "No response body"
            )

                answer = (
                f" **HTTP {status_code}** — {error_text}"
                )
            except Exception as exc:
                answer = f" **Unexpected error:** {exc}"

        st.markdown(answer)

    # ── Persist ──
    messages.append({"role": "assistant", "content": answer})
    current_chat["messages"] = messages
    save_chats()
    st.rerun()