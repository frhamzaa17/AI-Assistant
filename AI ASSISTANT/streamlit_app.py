import streamlit as st
from main import answer_question

# Page setup
st.set_page_config(page_title="AI Study Coach", layout="centered")
st.markdown("""
    <style>
        .chat-container {
            background-color: #f9f9f9;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .user-msg {
            background-color: #dbeafe;
            color: #1e3a8a;
            padding: 0.7rem 1rem;
            border-radius: 10px;
            margin: 0.3rem 0;
            max-width: 75%;
            align-self: flex-end;
        }
        .bot-msg {
            background-color: #e5e7eb;
            color: #111827;
            padding: 0.7rem 1rem;
            border-radius: 10px;
            margin: 0.3rem 0;
            max-width: 75%;
            align-self: flex-start;
            word-wrap: break-word
        }
        .chat-box {
            display: flex;
            flex-direction: column;
        }
        .input-area {
            position: fixed;
            bottom: 1.5rem;
            left: 0;
            right: 0;
            width: 100%;
            max-width: 720px;
            margin: auto;
            background-color: #ffffff;
            padding: 0.75rem 1rem;
            box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
            border-top: 1px solid #e5e7eb;
        }
        .stTextInput>div>div>input {
            padding: 0.6rem 0.75rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>🎓 AI Study Coach</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>A personalized academic assistant for learners and achievers.</p>", unsafe_allow_html=True)

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history container
with st.container():
    for msg in st.session_state.messages:
        css_class = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(
            f"<div class='chat-container chat-box'><div class='{css_class}'>{msg['content']}</div></div>",
            unsafe_allow_html=True
        )

# Input container
with st.container():
    with st.form("chat_input", clear_on_submit=True):
        user_input = st.text_input("Type your message", label_visibility="collapsed", placeholder="Ask me anything...")
        submitted = st.form_submit_button("Send")

# Handle response
if submitted and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate AI answer
    with st.spinner("Coach is composing a response..."):
        answer = answer_question(user_input)
    st.session_state.messages.append({"role": "bot", "content": answer})

    # Refresh to show new messages
    st.rerun()