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

# Display chat history
if st.session_state.history:
    st.subheader("🧠 Chat History")
    for msg in st.session_state.history:
        st.markdown(f"**🧑 You:** {msg['user']}")
        st.markdown(f"**🤖 Assistant:** {msg['assistant']}")

if submit_button and user_query:
    try:
        with requests.post(
            API_URL,
            json={"question": user_query, "history": st.session_state.history},
            stream=True,
            timeout=60
        ) as response:
            if response.status_code != 200:
                st.error(f"❌ Error: {response.text}")
            else:
                # Display user query
                st.markdown(f"**🧑 You:** {user_query}")

                # Display assistant response in real-time
                assistant_placeholder = st.empty()
                full_response = ""

                for chunk in response.iter_lines(decode_unicode=True):
                    if chunk:
                        full_response += chunk + "\n"
                        assistant_placeholder.markdown(f"**🤖 Assistant:** {full_response}", unsafe_allow_html=True)

                # Update chat history
                st.session_state.history.append({
                    "user": user_query,
                    "assistant": full_response
                })

    except Exception as e:
        st.error(f"❌ Exception occurred: {str(e)}")

elif not submit_button:
    st.markdown("🚀 Enter a question and press **Send** to start chatting.")
