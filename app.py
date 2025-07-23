import streamlit as st
from chat_core import generate_reply, process_uploaded_files, USER_DATA

# --------------------------------
# 🔧 Page Config
# --------------------------------
st.set_page_config(
    page_title="MedMentor AI",
    page_icon="⚕️",
    layout="wide"
)

# --------------------------------
# 🎨 CSS STYLING (Fonts, Colors, Backgrounds)
# --------------------------------
st.markdown("""
    <style>
    /* Base font and color */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        color: #f4f6f9;
        background-color: #1e1e2f;
    }

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #161622;
        padding: 2rem 1.5rem;
    }

    /* Upload box */
    .css-1djdyxw, .stFileUploader {
        background-color: #2c2f4a !important;
        border: 1px solid #555 !important;
        border-radius: 10px;
        padding: 12px;
    }

    /* Headings and subheadings */
    h1, h2, h3, h4 {
        color: #4db8ff;
    }

    /* Sidebar custom classes */
    .sidebar-title {
        font-size: 22px;
        font-weight: bold;
        color: #4db8ff;
        margin-bottom: 5px;
    }

    .sidebar-sub {
        font-size: 15px;
        color: #bdc3c7;
        margin-bottom: 20px;
    }

    /* Labels and captions */
    .stSelectbox label {
        color: #ffffff !important;
    }

    .stCaption {
        color: #a0a0a0 !important;
        font-size: 14px !important;
    }

    hr {
        border-top: 1px solid #444 !important;
    }

    /* Chat bubble override */
    .chat-message {
        background-color: #2a2d45;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------
# 🏥 Title
# --------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #4db8ff; font-size: 40px; font-weight: 800;'>⚕️ MedMentor AI</h1>
    <p style='text-align: center; font-size: 18px; color: #bdc3c7;'>Your Surgical Assistant for Smarter Healthcare Decisions</p>
    <hr />
    """,
    unsafe_allow_html=True
)

# --------------------------------
# 🧠 Session State
# --------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "ishaan"
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# --------------------------------
# 📁 Sidebar
# --------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>📚 Medical Knowledge Base</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Any doubts? Upload your medical files here 👇</div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, CSV, TXT files",
        type=["pdf", "docx", "csv", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        process_uploaded_files(uploaded_files)
        st.session_state.uploaded_files = uploaded_files
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")

    st.markdown("<hr />", unsafe_allow_html=True)
    st.markdown("### 🧑‍⚕️ Active Profile")
    user = st.selectbox(
        "Choose a user",
        ("Ishaan", "Jyotika"),
        index=0 if st.session_state.user_id == "ishaan" else 1
    )
    st.session_state.user_id = user.lower()
    specialty = "Cardiothoracic Surgery" if user.lower() == "ishaan" else "Neurosurgery"
    st.markdown(f"<span style='color:#9cc9f3;'>🔹 <b>{user}</b> — <i>{specialty}</i></span>", unsafe_allow_html=True)

# --------------------------------
# 💬 Chat History
# --------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(
            f"<div class='chat-message'>{message['content']}</div>",
            unsafe_allow_html=True
        )

# --------------------------------
# 📝 Chat Input
# --------------------------------
if prompt := st.chat_input("💬 Ask any surgical or medical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='chat-message'>{prompt}</div>", unsafe_allow_html=True)

    with st.spinner("🔍 Consulting surgical knowledge..."):
        reply = generate_reply(
            st.session_state.user_id,
            prompt,
            st.session_state.uploaded_files
        )

    with st.chat_message("assistant"):
        st.markdown(f"<div class='chat-message'>{reply}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
