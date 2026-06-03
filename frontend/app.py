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
# BACKEND
# ─────────────────────────────────────────────
BACKEND = "http://127.0.0.1:8000/chat/stream"
CHAT_FILE = "chat_history.json"

# ─────────────────────────────────────────────
# SERVICE DEFINITIONS
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
        "actions": [
            {"label": "Recharge Plans",      "query": "What are the best Airtel prepaid recharge plans available?"},
            {"label": "Balance Check",        "query": "How do I check my Airtel prepaid data and balance?"},
            {"label": "Port to Airtel",       "query": "How do I port my number to Airtel prepaid?"},
            {"label": "SIM Replacement",      "query": "How do I get an Airtel SIM replacement?"},
            {"label": "Other Question",       "query": None},
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
        "actions": [
            {"label": "Pay Bill",             "query": "How do I pay my Airtel postpaid bill?"},
            {"label": "Upgrade Plan",         "query": "How do I upgrade my Airtel postpaid plan?"},
            {"label": "Enable Roaming",       "query": "How do I enable international roaming on my Airtel postpaid?"},
            {"label": "Activate eSIM",        "query": "How do I activate eSIM on Airtel postpaid?"},
            {"label": "Other Question",       "query": None},
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
        "actions": [
            {"label": "New Connection",       "query": "How do I get a new Airtel Fiber broadband connection?"},
            {"label": "Download Bill",        "query": "How do I download my Airtel broadband bill?"},
            {"label": "Slow Internet",        "query": "How do I fix slow Airtel broadband internet speed?"},
            {"label": "Shift Connection",     "query": "How do I request relocation of my Airtel broadband connection?"},
            {"label": "Other Question",       "query": None},
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
        "actions": [
            {"label": "Recharge DTH",         "query": "How do I recharge my Airtel DTH?"},
            {"label": "Channel Packs",        "query": "What channel packs are available on Airtel DTH?"},
            {"label": "Fix Signal Issue",     "query": "How do I fix signal issues on my Airtel DTH?"},
            {"label": "Upgrade to HD",        "query": "How do I upgrade my Airtel DTH to HD?"},
            {"label": "Other Question",       "query": None},
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
        "actions": [
            {"label": "Open Account",         "query": "How do I open an Airtel Payments Bank savings account?"},
            {"label": "Setup UPI",            "query": "How do I set up UPI on Airtel Payments Bank?"},
            {"label": "Transfer Money",       "query": "How do I transfer money using Airtel Payments Bank?"},
            {"label": "Update KYC",           "query": "How do I update my KYC for Airtel Payments Bank?"},
            {"label": "Other Question",       "query": None},
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
        "actions": [
            {"label": "What is Airtel Black?", "query": "What is Airtel Black and what are its benefits?"},
            {"label": "Subscribe",             "query": "How do I subscribe to Airtel Black?"},
            {"label": "Billing",               "query": "How do I check my Airtel Black bill?"},
            {"label": "Support",               "query": "How do I contact Airtel Black customer support?"},
            {"label": "Other Question",        "query": None},
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
# LOAD CHAT  
# ─────────────────────────────────────────────
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        chat_sessions = json.load(f)
else:
    chat_sessions = {}

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "selected_service" not in st.session_state:
    st.session_state.selected_service = None
if "selected_action" not in st.session_state:
    st.session_state.selected_action = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "free_input_mode" not in st.session_state:
    st.session_state.free_input_mode = False
if "sidebar_search" not in st.session_state:
    st.session_state.sidebar_search = ""

# ─────────────────────────────────────────────
# SAVE CHATS
# ─────────────────────────────────────────────
def save_chats():
    with open(CHAT_FILE, "w") as f:
        json.dump(chat_sessions, f, indent=4)

# ─────────────────────────────────────────────
# MODULAR RENDERERS
# ─────────────────────────────────────────────

def render_service_cards():
    """Renders the welcome hero and 6 service cards (3 per row)."""
    st.markdown(
        """
<div class="welcome-wrap">
    <div class="welcome-hero">
        <div class="welcome-icon-wrap">
            <div class="welcome-icon">📡</div>
            <div class="welcome-pulse"></div>
        </div>
        <div class="welcome-title">Hello! I'm your <span>Airtel</span> Assistant 👋</div>
        <div class="welcome-sub">Choose a service to get started, or type your question below.</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    row1 = list(SERVICES.items())[:3]
    row2 = list(SERVICES.items())[3:]

    for row in [row1, row2]:
        cols = st.columns(len(row))
        for col, (key, svc) in zip(cols, row):
            with col:
                clicked = st.button(
                    f"{svc['icon']}\n\n**{svc['label']}**",
                    key=f"svc_btn_{key}",
                    use_container_width=True,
                )
                if clicked:
                    st.session_state.selected_service = key
                    st.session_state.selected_action = None
                    st.session_state.free_input_mode = False
                    st.rerun()


def render_service_actions(svc_key: str):
    """Renders quick-action buttons for the selected service."""
    svc = SERVICES[svc_key]

    st.markdown(
        f"""
<div class="faq-header">
    <div class="faq-header-icon">{svc['icon']}</div>
    <div>
        <div class="faq-header-title">{svc['label']}</div>
        <div class="faq-header-sub">Pick a quick action or type your own question below.</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("← Services", key="back_btn"):
        st.session_state.selected_service = None
        st.session_state.selected_action = None
        st.session_state.free_input_mode = False
        st.rerun()

    st.markdown('<div class="action-grid-vertical">', unsafe_allow_html=True)
    actions = svc["actions"]

    for i in range(0, len(actions), 2):
      col1, col2 = st.columns(2)

      with col1:
        if st.button(
            actions[i]["label"],
            key=f"action_{svc_key}_{i}",
            use_container_width=True,
        ):
         handle_quick_action(actions[i])

      if i + 1 < len(actions):
         with col2:
            if st.button(
                actions[i + 1]["label"],
                key=f"action_{svc_key}_{i+1}",
                use_container_width=True,
            ):
                handle_quick_action(actions[i + 1])
    

    st.markdown("</div>", unsafe_allow_html=True)


def handle_quick_action(action: dict):
    """Handles a quick-action button click."""
    if action["query"] is None:
        # "Other Question" — drop into free chat
        st.session_state.free_input_mode = True
        st.session_state.selected_action = "free"
        st.rerun()
    else:
        st.session_state.selected_action = action["label"]
        st.session_state.pending_query = action["query"]
        st.rerun()


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
        chat_sessions[chat_id] = {"title": "New Chat", "messages": []}
        save_chats()
        st.session_state.current_chat = chat_id
        st.session_state.selected_service = None
        st.session_state.selected_action = None
        st.session_state.free_input_mode = False
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

    if st.session_state.current_chat not in chat_sessions:
        st.session_state.current_chat = list(chat_sessions.keys())[-1]

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
                
            else:
                if st.button(display_title, key=f"chat_{cid}", use_container_width=True):
                    st.session_state.current_chat = cid
                    st.session_state.selected_service = None
                    st.session_state.selected_action = None
                    st.session_state.free_input_mode = False
                    st.rerun()

        with col2:
            with st.popover("⋯"):
                if st.button(" Rename", key=f"rename_btn_{cid}", use_container_width=True):
                    rename_chat_dialog(cid)
                if st.button("Delete", key=f"delete_{cid}", use_container_width=True):
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
        current_chat["title"] = query[:30] + ("…" if len(query) > 30 else "")
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

        if sources:
            if rewritten and rewritten != query:
                st.markdown(
                    f'<div class="query-rewrite">Query interpreted as: <em>{rewritten}</em></div>',
                    unsafe_allow_html=True,
                )
            with st.expander("📎 Sources Used", expanded=False):
                for s in sources:
                    st.markdown(
                        f"""
<div class="source-card">
    <div class="source-header">
        <span class="source-index">#{s['index']}</span>
        <span class="source-file">{s['source']}</span>
    </div>
    <div class="source-section">📂 {s['section']}</div>
    <div class="source-snippet">{s['snippet']}</div>
</div>
""",
                        unsafe_allow_html=True,
                    )

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
        "rewritten_query": rewritten,
    })
    current_chat["messages"] = messages
    save_chats()

# ─────────────────────────────────────────────
# CHAT DISPLAY
# ─────────────────────────────────────────────
if len(messages) == 0:
    # No messages yet — show welcome or service actions
    if st.session_state.selected_service is None:
        render_service_cards()
    else:
        render_service_actions(st.session_state.selected_service)
else:
    # Existing chat — render history
    for msg in messages:
        role = msg["role"]
        avatar = "👤" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
query = st.chat_input("Ask about plans, recharge, broadband, DTH…")

# ─────────────────────────────────────────────
# HANDLE PENDING QUERY (chip / quick-action triggered)
# ─────────────────────────────────────────────
if st.session_state.pending_query:
    pq = st.session_state.pending_query
    st.session_state.pending_query = None
    # Once a query fires, we leave the action screen and go into chat
    st.session_state.selected_service = None
    st.session_state.selected_action = None
    st.session_state.free_input_mode = False
    send_query(pq)
    st.rerun()

# ─────────────────────────────────────────────
# HANDLE TYPED QUERY
# ─────────────────────────────────────────────
if query:
    st.session_state.selected_service = None
    st.session_state.selected_action = None
    st.session_state.free_input_mode = False
    send_query(query)
    st.rerun()