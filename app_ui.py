import streamlit as st
import requests
import config

API_URL = config.API_URL

st.set_page_config(page_title="AI-Powered Knowledge Assistant", page_icon="🤖", layout="wide")
st.title("📚 CALS Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

# Form nhập câu hỏi
with st.form(key="chat_form", clear_on_submit=True):
    user_query = st.text_input("💬 Ask a question:")
    submit_button = st.form_submit_button("Send")

# Hiển thị lịch sử trò chuyện
if st.session_state.history:
    st.subheader("🧠 Chat History")
    for msg in st.session_state.history:
        st.markdown(f"**🧑 You:** {msg['user']}")
        st.markdown(f"**🤖 Assistant:** {msg['assistant']}")

# Xử lý khi người dùng gửi câu hỏi
if submit_button and user_query:
    try:
        with st.spinner("🧠 Classifying question..."):
            classify_response = requests.post(
                f"{API_URL}/classify",
                json={"question": user_query}
            )

        if classify_response.status_code != 200:
            st.error(f"❌ Classification failed: {classify_response.text}")
        else:
            category = classify_response.json().get("category", "")
            st.markdown(f"🔍 **Category:** `{category}`")

            if category == "greeting":
                assistant_response = "Hello! How can I assist you today?"
                st.markdown(f"**🧑 You:** {user_query}")
                st.markdown(f"**🤖 Assistant:** {assistant_response}")
                st.session_state.history.append({
                    "user": user_query,
                    "assistant": assistant_response
                })

            else:
                with st.spinner("🤖 Generating response..."):
                    with requests.post(
                        f"{API_URL}/chat",
                        json={"question": user_query, "history": st.session_state.history, "category": category},
                        stream=True,
                        timeout=60
                    ) as response:
                        if response.status_code != 200:
                            st.error(f"❌ Error: {response.text}")
                        else:
                            st.markdown(f"**🧑 You:** {user_query}")
                            assistant_placeholder = st.empty()
                            full_response = ""

                            for chunk in response.iter_lines(decode_unicode=True):
                                if chunk:
                                    full_response += chunk
                                    assistant_placeholder.markdown(
                                        f"**🤖 Assistant:** {full_response.strip()}",
                                        unsafe_allow_html=True
                                    )

                            st.session_state.history.append({
                                "user": user_query,
                                "assistant": full_response.strip()
                            })

    except Exception as e:
        st.error(f"❌ Exception occurred: {str(e)}")

elif not submit_button:
    st.markdown("🚀 Enter a question and press **Send** to start chatting.")
