import streamlit.components.v1 as components
import streamlit as st
import requests
import json
import os
import uuid
import string as _string

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
# BACKEND
# ─────────────────────────────────────────────
BACKEND = "http://127.0.0.1:8000/chat/stream"
CHAT_FILE = "chat_history.json"

# ─────────────────────────────────────────────
# SERVICE DEFINITIONS (reserved for future use)
# ─────────────────────────────────────────────
SERVICES = {
    "prepaid": {
        "icon": "📱",
        "label": "Prepaid",
        "color": "#e40000",
        "faqs": [
            "What are the best recharge plans?",
            "How do I check my data balance?",
            "How do I check my plan validity?",
            "How do I activate international roaming?",
            "How do I get a SIM replacement?",
            "How do I port my number to Airtel?",
        ],
    },
    "postpaid": {
        "icon": "📞",
        "label": "Postpaid",
        "color": "#c0392b",
        "faqs": [
            "How do I pay my postpaid bill?",
            "What is my current postpaid plan?",
            "How do I upgrade my postpaid plan?",
            "How do I enable roaming on postpaid?",
            "How do I activate eSIM?",
            "How do I check my usage details?",
        ],
    },
    "wifi": {
        "icon": "📶",
        "label": "WiFi Broadband",
        "color": "#9b1c1c",
        "faqs": [
            "How do I pay my broadband bill?",
            "How do I change my broadband plan?",
            "How do I fix slow internet speed?",
            "How do I request a relocation?",
            "How do I get a new Airtel Fiber connection?",
            "How do I register a complaint?",
        ],
    },
    "dth": {
        "icon": "📺",
        "label": "DTH",
        "color": "#7b241c",
        "faqs": [
            "How do I recharge my DTH?",
            "What channel packs are available?",
            "How do I fix signal issues?",
            "How do I add new channels?",
            "How do I upgrade to HD?",
            "How do I manage my DTH account?",
        ],
    },
    "payments": {
        "icon": "🏦",
        "label": "Payments Bank",
        "color": "#641e16",
        "faqs": [
            "How do I open an Airtel savings account?",
            "How do I set up UPI?",
            "How do I transfer money?",
            "What wallet services are available?",
            "How do I update my KYC?",
            "How do I get an Airtel debit card?",
        ],
    },
    "black": {
        "icon": "⭐",
        "label": "Airtel Black",
        "color": "#1a1a1a",
        "faqs": [
            "What Airtel Black plans are available?",
            "How do I check my Airtel Black bill?",
            "How do I upgrade my Airtel Black package?",
            "How do I add more services to Airtel Black?",
            "How do I contact Airtel Black support?",
        ],
    },
}

# ─────────────────────────────────────────────
# FOLLOW-UP SUGGESTIONS BY KEYWORD
# ─────────────────────────────────────────────
FOLLOWUP_SUGGESTIONS = {
    "prepaid":  ["Check data balance", "Recharge now", "Check validity", "Port to Airtel", "International roaming"],
    "postpaid": ["Pay bill", "Upgrade plan", "Enable roaming", "Activate eSIM", "Usage summary"],
    "wifi":     ["Pay broadband bill", "Check speed tips", "Change plan", "New connection", "Raise complaint"],
    "dth":      ["Recharge DTH", "Add channels", "Fix signal issue", "HD upgrade", "Channel packs"],
    "payments": ["UPI setup", "Transfer money", "Update KYC", "Open account", "Debit card"],
    "black":    ["View plans", "Check bill", "Add services", "Upgrade package", "Support"],
    "default":  ["Check balance", "Current plan", "Bill payment", "Recharge options", "Talk to support"],
}

def get_followups(query: str) -> list[str]:
    q = query.lower()
    for key in FOLLOWUP_SUGGESTIONS:
        if key in q or any(word in q for word in key.split()):
            return FOLLOWUP_SUGGESTIONS[key]
    return FOLLOWUP_SUGGESTIONS["default"]

# ─────────────────────────────────────────────
# CHAT TITLE GENERATOR
# ─────────────────────────────────────────────
def generate_chat_title(query: str) -> str:
    title = query.strip().strip(_string.punctuation).strip()
    if len(title) > 40:
        title = title[:40].rstrip()
    return title.capitalize() if title else "New Chat"

# ─────────────────────────────────────────────
# GREETING MESSAGE
# ─────────────────────────────────────────────
GREETING_MESSAGE = {
    "role": "assistant",
    "content": (
        "👋 **Hi! I'm Airtel Assistant.**\n\n"
        "I can help with:\n"
        "- 📱 Mobile Recharge & Plans\n"
        "- 📶 WiFi Broadband\n"
        "- 📺 DTH Services\n"
        "- 🏦 Airtel Payments Bank\n"
        "- ⭐ Airtel Black\n\n"
        "Ask me anything or choose one of the quick options below."
    ),
    "sources": [],
    "rewritten_query": None,
}

# ─────────────────────────────────────────────
# STARTER CHIPS
# ─────────────────────────────────────────────
STARTER_CHIPS = [
    "What are the best recharge plans?",
    "My WiFi is slow",
    "How do I recharge DTH?",
    "How do I open a savings account?",
    "What is Airtel Black?",
]

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
# LOAD CHAT HISTORY
# ─────────────────────────────────────────────
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        chat_sessions = json.load(f)
else:
    chat_sessions = {}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

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

    if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True):
        chat_id = str(uuid.uuid4())[:8]
        chat_sessions[chat_id] = {"title": "New Chat", "messages": [GREETING_MESSAGE]}
        save_chats()
        st.session_state.current_chat = chat_id
        st.rerun()

    # ── CHAT INITIALIZATION ──
    if "current_chat" not in st.session_state:
        if chat_sessions:
            st.session_state.current_chat = list(chat_sessions.keys())[-1]
        else:
            chat_id = str(uuid.uuid4())[:8]
            chat_sessions[chat_id] = {"title": "New Chat", "messages": [GREETING_MESSAGE]}
            save_chats()
            st.session_state.current_chat = chat_id

    if st.session_state.current_chat not in chat_sessions:
        st.session_state.current_chat = list(chat_sessions.keys())[-1]

    # SEARCH
    st.markdown('<div class="sidebar-section-label">Recent Chats</div>', unsafe_allow_html=True)
    search_val = st.text_input(
        "Search chats",
        placeholder="🔍  Search history…",
        label_visibility="collapsed",
        key="sidebar_search_input",
    )

    filtered_chats = [
        cid for cid in reversed(list(chat_sessions.keys()))
        if search_val.lower() in chat_sessions[cid].get("title", "").lower()
    ] if search_val else list(reversed(list(chat_sessions.keys())))

    if not filtered_chats:
        st.markdown('<div class="sidebar-empty">No chats found</div>', unsafe_allow_html=True)

    for cid in filtered_chats:
        title = chat_sessions[cid].get("title", "New Chat")
        is_active = cid == st.session_state.current_chat
        display_title = title if len(title) <= 28 else title[:25] + "…"

        col1, col2 = st.columns([13, 1])
        with col1:
            if is_active:
                st.markdown(f'<div class="chat-row-active">{display_title}</div>', unsafe_allow_html=True)
                if st.button(display_title, key=f"chat_{cid}", use_container_width=True):
                    pass  # already active
            else:
                if st.button(display_title, key=f"chat_{cid}", use_container_width=True):
                    st.session_state.current_chat = cid
                    st.rerun()

        with col2:
            with st.popover("⋯"):
                if st.button(" Rename", key=f"rename_btn_{cid}", use_container_width=True):
                    rename_chat_dialog(cid)
                if st.button("Delete", key=f"delete_{cid}", use_container_width=True):
                    del chat_sessions[cid]
                    if not chat_sessions:
                        new_chat_id = str(uuid.uuid4())[:8]
                        chat_sessions[new_chat_id] = {"title": "New Chat", "messages": [GREETING_MESSAGE]}
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
        <div class="topbar-left">
            <div class="topbar-logo">📡</div>
            <div>
                <div class="topbar-title"><span>Airtel</span> Assistant</div>
                <div class="topbar-sub">Powered by AI · Always available</div>
            </div>
        </div>
        <div class="topbar-right">
            <div class="topbar-badge">● LIVE</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# SEND QUERY HELPER
# ─────────────────────────────────────────────
def send_query(query: str):
    """Handles the full send-and-stream flow for a query string."""

    if current_chat["title"] == "New Chat":
        current_chat["title"] = generate_chat_title(query)
        save_chats()

    with st.chat_message("user", avatar="👤"):
        st.markdown(query)

    recent_history = messages[-6:]
    messages.append({"role": "user", "content": query})

    with st.chat_message("assistant", avatar="🤖"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<div class="typing-indicator">'
            '<span class="typing-text">Airtel Assistant is typing</span>'
            '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>'
            '</div>',
            unsafe_allow_html=True,
        )

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
                typing_placeholder.empty()

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
            typing_placeholder.empty()
            full_text = "⚠️ **Backend not running.**\n\nPlease start the FastAPI server first."
        except requests.exceptions.Timeout:
            typing_placeholder.empty()
            full_text = "⚠️ **Request timed out.** Please try again."
        except Exception as e:
            typing_placeholder.empty()
            full_text = f"⚠️ **Error:** {e}"

        token_placeholder.markdown(full_text)

        # Sources and query rewrite intentionally not displayed

        # FOLLOW-UP SUGGESTIONS
        suggestions = get_followups(query)
        st.markdown('<div class="followup-label">You might also ask:</div>', unsafe_allow_html=True)
        cols = st.columns(len(suggestions))
        for i, sug in enumerate(suggestions):
            with cols[i]:
                if st.button(sug, key=f"followup_{uuid.uuid4().hex[:6]}", use_container_width=True):
                    st.session_state.pending_query = sug

    messages.append({
        "role": "assistant",
        "content": full_text,
        "sources": sources,
        "rewritten_query": rewritten,
    })
    current_chat["messages"] = messages
    save_chats()

# ─────────────────────────────────────────────
# CHAT RENDERING
# ─────────────────────────────────────────────
for i, msg in enumerate(messages):
    role = msg["role"]
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

        # ── STARTER CHIPS — only below the greeting, only when no user messages yet ──
        if role == "assistant" and i == 0 and len(messages) == 1:
            st.markdown('<div class="followup-label">Quick questions:</div>', unsafe_allow_html=True)
            chip_cols = st.columns(len(STARTER_CHIPS))
            for j, chip in enumerate(STARTER_CHIPS):
                with chip_cols[j]:
                    if st.button(chip, key=f"starter_{j}", use_container_width=True):
                        st.session_state.pending_query = chip
                        st.rerun()

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
query = st.chat_input("Ask me anything about Airtel services…")

# ─────────────────────────────────────────────
# HANDLE PENDING (chip-triggered) QUERY
# ─────────────────────────────────────────────
if st.session_state.pending_query:
    pq = st.session_state.pending_query
    st.session_state.pending_query = None
    send_query(pq)
    st.rerun()

# ─────────────────────────────────────────────
# HANDLE TYPED QUERY
# ─────────────────────────────────────────────
if query:
    send_query(query)
    st.rerun()