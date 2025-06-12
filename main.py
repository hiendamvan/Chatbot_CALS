from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import re

# Load environment variables
load_dotenv()

# Constants
CHROMA_PATH = "chroma_db"
NUM_RESULTS = 3

# Initialize components
embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")
llm = ChatOpenAI(model="gpt-4.1-nano")

# Create retriever 
vector_store = Chroma(collection_name="vcc_env",embedding_function=embedding,persist_directory=CHROMA_PATH)
retriever = vector_store.as_retriever(search_type="similarity",search_kwargs={"k": NUM_RESULTS})

# FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Chat input model
class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []

# Helper: remove <think> tags
def remove_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

@app.post("/chat")
async def chat(request: ChatRequest):
    question = request.question
    history = request.history or []

    # Retrieve documents
    docs = retriever.invoke(question)
    knowledge = "\n".join(doc.page_content for doc in docs)

    # Format RAG prompt
    rag_prompt = f"""
You are an assistant that answers questions based only on the provided knowledge.
Do not use prior knowledge or mention the source information.
Use only the content from the section "The knowledge".

The question: {question}

Conversation history: {history}

The knowledge: {knowledge}
"""

    try:
        # Streaming not supported in standard FastAPI response, so aggregate response
        partial_message = ""
        thinking = False

        for chunk in llm.stream(rag_prompt):
            if "<think>" in chunk.content:
                thinking = True
            elif "</think>" in chunk.content:
                thinking = False
                continue
            if thinking:
                continue
            partial_message += chunk.content

        cleaned_message = remove_think_tags(partial_message)

        # Append to history
        history.append({"user": question, "assistant": cleaned_message})

        return {
            "answer": cleaned_message,
            "history": history
        }

    except Exception as e:
        return {"error": str(e)}
