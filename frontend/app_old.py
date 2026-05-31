import streamlit.components.v1 as components
import streamlit as st
import requests
import json
import os
import uuid

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Airtel AI Assistant",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("style.css not found")

load_css()

# ─────────────────────────────────────────────
# RENAME DIALOG
# ─────────────────────────────────────────────
@st.dialog("Rename Chat")
def rename_chat_dialog(cid):
    new_title = st.text_input(
        "Chat name",
        value=chat_sessions.get(cid, {}).get("title", "")
    )
    cols = st.columns(2)
    with cols[0]:
        if st.button("Save", key=f"save_dialog_{cid}"):
            chat_sessions[cid]["title"] = new_title
            save_chats()
            st.rerun()
    with cols[1]:
        if st.button("Cancel", key=f"cancel_dialog_{cid}"):
            st.rerun()

# ─────────────────────────────────────────────
# BACKEND
# ─────────────────────────────────────────────
BACKEND = "http://127.0.0.1:8000/chat/stream"
CHAT_FILE = "chat_history.json"

# ─────────────────────────────────────────────
# LOAD CHAT HISTORY
# ─────────────────────────────────────────────
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        chat_sessions = json.load(f)
else:
    chat_sessions = {}

# ─────────────────────────────────────────────
# SAVE CHATS
# ─────────────────────────────────────────────
def save_chats():
    with open(CHAT_FILE, "w") as f:
        json.dump(chat_sessions, f, indent=4)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

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

    # NEW CHAT
    if st.button("+ New Chat", key="new_chat_btn"):
        chat_id = str(uuid.uuid4())[:8]
        chat_sessions[chat_id] = {"title": "New Chat", "messages": []}
        save_chats()
        st.session_state.current_chat = chat_id
        st.rerun()

    # INIT current_chat
    if "current_chat" not in st.session_state:
        if chat_sessions:
            st.session_state.current_chat = list(chat_sessions.keys())[-1]
        else:
            chat_id = str(uuid.uuid4())[:8]
            chat_sessions[chat_id] = {"title": "New Chat", "messages": []}
            save_chats()
            st.session_state.current_chat = chat_id

    # SAFETY
    if st.session_state.current_chat not in chat_sessions:
        st.session_state.current_chat = list(chat_sessions.keys())[-1]

    st.markdown(
        '<div class="sidebar-section-label">Recent Chats</div>',
        unsafe_allow_html=True,
    )

    # Build active-chat CSS targeting Streamlit's key attribute on the button element
    active_cid = st.session_state.current_chat
    st.markdown(
        f'<style>'
        f'[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]'
        f'[key="chat_{active_cid}"], '
        f'[data-testid="stSidebar"] div[data-testid="stButtonGroup"] '
        f'button[aria-label="{chat_sessions.get(active_cid,{}).get("title","")[:30]}"] {{'
        f'background: rgba(228,0,0,0.11) !important;'
        f'border-left: 2px solid #e40000 !important;'
        f'border-radius: 0 6px 6px 0 !important;'
        f'color: #f0f0f5 !important;'
        f'font-weight: 500 !important;'
        f'padding-left: 6px !important;'
        f'}}</style>',
        unsafe_allow_html=True,
    )

    # ── CHAT LIST ──
    for cid in reversed(list(chat_sessions.keys())):
        title = chat_sessions[cid]["title"]
        is_active = cid == st.session_state.current_chat

        col1, col2 = st.columns([14, 1])

        with col1:
            # Truncate title in button label for display
            display_title = title if len(title) <= 30 else title[:27] + "…"
            if st.button(
                display_title,
                key=f"chat_{cid}",
                use_container_width=True,
            ):
                st.session_state.current_chat = cid
                st.rerun()

        with col2:
            with st.popover("⋯"):
                if st.button(
                    "Rename",
                    key=f"rename_btn_{cid}",
                    use_container_width=True,
                ):
                    rename_chat_dialog(cid)

                if st.button(
                    "Delete",
                    key=f"delete_{cid}",
                    use_container_width=True,
                ):
                    del chat_sessions[cid]
                    if not chat_sessions:
                        new_chat_id = str(uuid.uuid4())[:8]
                        chat_sessions[new_chat_id] = {"title": "New Chat", "messages": []}
                        st.session_state.current_chat = new_chat_id
                    else:
                        st.session_state.current_chat = list(chat_sessions.keys())[-1]
                    save_chats()
                    st.rerun()

# ─────────────────────────────────────────────
# CURRENT CHAT
# ─────────────────────────────────────────────
current_chat = chat_sessions[st.session_state.current_chat]
messages = current_chat["messages"]

# ─────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-title">
            <span>Airtel</span> FAQ Assistant
        </div>
        <div class="topbar-badge">● LIVE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# CHAT DISPLAY
# ─────────────────────────────────────────────
if len(messages) == 0:
    welcome_html = """
<div class="welcome-wrap">
  <div class="welcome-icon">📡</div>
  <div class="welcome-title">Hello! I'm your <span>Airtel</span> Assistant</div>
  <div class="welcome-sub">
    Ask anything about Airtel plans, broadband, DTH,
    recharge, roaming, payments, support and more.
  </div>
  <div class="suggestion-chips">
    <div class="chip">📶 Best prepaid plans</div>
    <div class="chip">🌍 International roaming</div>
    <div class="chip">📺 DTH packages</div>
    <div class="chip">🏠 Airtel Fiber</div>
    <div class="chip">💳 Recharge offers</div>
  </div>
</div>
"""
    st.markdown(welcome_html, unsafe_allow_html=True)

else:
    for msg in messages:
        role = msg["role"]
        with st.chat_message(role):
            st.markdown(msg["content"])

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
query = st.chat_input("Ask about plans, recharge, broadband, DTH...")

# ─────────────────────────────────────────────
# HANDLE USER QUERY
# ─────────────────────────────────────────────
if query:

    # UPDATE TITLE
    if current_chat["title"] == "New Chat":
        current_chat["title"] = query[:30] + ("..." if len(query) > 30 else "")

    # USER MESSAGE
    with st.chat_message("user"):
        st.markdown(query)

    # PREVIOUS HISTORY ONLY
    recent_history = messages[-6:]

    # SAVE USER MESSAGE
    messages.append({"role": "user", "content": query})

    # ASSISTANT RESPONSE
    with st.chat_message("assistant"):

        token_placeholder = st.empty()
        full_text = ""
        sources = []
        rewritten = None

        try:
            with requests.post(
                BACKEND,
                json={"question": query, "history": recent_history},
                stream=True,
                timeout=120,
            ) as response:

                response.raise_for_status()

                for raw_line in response.iter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.decode("utf-8")
                    if not line.startswith("data: "):
                        continue
                    payload = json.loads(line[6:])

                    if "token" in payload:
                        full_text += payload["token"]
                        token_placeholder.markdown(full_text + "▌")

                    if payload.get("done"):
                        sources = payload.get("sources", [])
                        rewritten = payload.get("rewritten_query")

        except requests.exceptions.ConnectionError:
            full_text = "⚠️ Backend not running.\n\nStart FastAPI server first."
        except requests.exceptions.Timeout:
            full_text = "⚠️ Backend timeout."
        except Exception as e:
            full_text = f"⚠️ Error: {e}"

        token_placeholder.markdown(full_text)

        if sources:
            if rewritten and rewritten != query:
                st.caption(f"Query interpreted as: *{rewritten}*")
            for s in sources:
                st.markdown(
                    f"**[Source {s['index']}]** `{s['source']}` — {s['section']}\n\n> {s['snippet']}"
                )

    # SAVE ASSISTANT RESPONSE
    messages.append({
        "role": "assistant",
        "content": full_text,
        "sources": sources,
        "rewritten_query": rewritten,
    })

    current_chat["messages"] = messages
    save_chats()
    st.rerun()