from agents.classify import classify_question
from agents.simple_rag import simple_rag
from agents.multihop import multihop 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_cohere import CohereRerank
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import config
import pickle
import os

# Load environment variables
load_dotenv()
# Constants
CHROMA_PATH = config.CHROMA_PATH
NUM_RESULTS = config.NUM_RESULTS

# Initialize embedding and llm 
embedding = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
llm = ChatOpenAI(model=config.LLM_MODEL)

# Create hybrid retriever 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> Chatbot_CALS/
CHUNKS_PATH = os.path.join(BASE_DIR, "data", "chunks.pkl")
with open(CHUNKS_PATH, 'rb') as f:
    chunks = pickle.load(f)

bm25_retriever = BM25Retriever.from_documents(
    chunks, embedding_function=embedding)
bm25_retriever.k = NUM_RESULTS 

vector_store = Chroma(
    collection_name="vcc_env",
    embedding_function=embedding,
    persist_directory=CHROMA_PATH
)
dense_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": NUM_RESULTS}
)

retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, dense_retriever],
    weights=[0.5, 0.5],
    return_source_documents=True
)

# Add reranking
reranker = CohereRerank(model='rerank-v3.5')

# FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Chat input model
class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []
    category: Optional[str] = None


@app.post("/classify")
async def classify(request: ChatRequest):
    category = classify_question(request.question)
    return {"category": category}

@app.post("/chat")
async def chat(request: ChatRequest):
    question = request.question
    history = request.history or []
    category = request.category or classify_question(question)
    
    if category == "simple":
        return await simple_rag(question, history, retriever, reranker, llm)
    elif category == "multi-hop":
        return await multihop(question, history, retriever, reranker, llm)
    elif category == "greeting":
        return {"response": "Hello! How can I assist you today?"}
    
