import os
import re
import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
os.environ["STREAMLIT_SERVER_RUN_ON_SAVE"] = "false"
# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Configuration
DATA_PATH = "data"
CHROMA_PATH = "chroma_db"
NUM_RESULTS = 3

# Initialize embedding model
embedding = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
)

# Initialize LLM
llm = ChatOpenAI(
    model='gpt-4.1-nano'
)

# Connect to Chroma DB
vector_store = Chroma(
    collection_name="vcc_env",
    embedding_function=embedding,
    persist_directory=CHROMA_PATH
)

retriever = vector_store.as_retriever(
    search_type='similarity',
    search_kwargs={'k': NUM_RESULTS}
)

def remove_think_tags(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# Streamlit UI setup
st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("🤖 RAG Chatbot with Ollama + HuggingFace")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(msg["user"])
    with st.chat_message("assistant"):
        st.markdown(msg["assistant"])
        
# Chat input box
user_input = st.chat_input("Hãy hỏi tôi về Viettel Construction...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)

    # Retrieve knowledge
    docs = retriever.invoke(user_input)
    knowledge = "\n".join(doc.page_content for doc in docs)

    # Build RAG prompt
    rag_prompt = f"""
You are an assistant that answers questions based only on the provided knowledge.
Do not use prior knowledge or mention the source information.
Use only the content from the section "The knowledge".

The question: {user_input}

Conversation history: {st.session_state.chat_history}

The knowledge: {knowledge}
"""

    print(rag_prompt)
    
    # Display assistant message with streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        partial_message = ""
        cleaned_message = ""

        try:
            thinking = False
            for chunk in llm.stream(rag_prompt):
                if "<think>" in chunk.content:
                    thinking = True
                elif "</think>" in chunk.content:
                    thinking = False
                    continue
                if thinking == True:
                    continue
                partial_message += chunk.content
                placeholder.markdown(partial_message)
                
        except Exception as e:
            placeholder.markdown(f"❌ Lỗi: {e}")

    # Save conversation to history
    st.session_state.chat_history.append({
        "user": user_input,
        "assistant": cleaned_message
    })