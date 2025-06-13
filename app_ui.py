import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

# Streamlit UI setup
st.set_page_config(page_title="AI-Powered Knowledge Assistant", page_icon="🤖", layout="wide")
st.title("📚 CALS Assistant")

# Session state to maintain chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Chat input
with st.form(key="chat_form", clear_on_submit=True):
    user_query = st.text_input("💬 Ask a question:")
    submit_button = st.form_submit_button("Send")

# Send query to FastAPI
if submit_button and user_query:
    try:
        response = requests.post(
            API_URL,
            json={"question": user_query, "history": st.session_state.history}
        )
        data = response.json()

        if "answer" in data:
            # Update history
            st.session_state.history = data["history"]

            # Display full chat
            st.subheader("🧠 Chat History")
            for msg in reversed(st.session_state.history):
                st.markdown(f"**🧑 You:** {msg['user']}")
                st.markdown(f"**🤖 Assistant:** {msg['assistant']}")
        else:
            st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Exception occurred: {str(e)}")

elif not submit_button:
    st.markdown("🚀 Enter a question and press **Send** to start chatting.")
