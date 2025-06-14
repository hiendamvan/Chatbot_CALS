from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import pickle
import asyncio

# Load environment variables
load_dotenv()

# Constants
CHROMA_PATH = "chroma_db"
NUM_RESULTS = 6

# Initialize embedding and llm 
embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")
llm = ChatOpenAI(model="gpt-4.1-nano")

# Create hybrid retriever 
with open("data/chunks.pkl", 'rb') as f:
    chunks = pickle.load(f)

bm25_retriever = BM25Retriever.from_documents(
    chunks, embedding_function=embedding)
bm25_retriever.k = 3

vector_store = Chroma(
    collection_name="vcc_env",
    embedding_function=embedding,
    persist_directory=CHROMA_PATH
)
dense_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, dense_retriever],
    weights=[0.5, 0.5],
    return_source_documents=True
)

# FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Chat input model
class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    question = request.question
    history = request.history or []

    # Retrieve documents
    docs = retriever.invoke(question)
    # You can optionally remove duplicate docs here if needed

    # Combine knowledge base content
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

    async def stream_generator():
        try:
            full_response = ""
            async for chunk in llm.astream(rag_prompt):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    print(repr(content))  # DEBUG
                    full_response += content
                    yield content
                    await asyncio.sleep(0.02)
            history.append({"user": question, "assistant": full_response})
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(stream_generator(), media_type="text/plain")
