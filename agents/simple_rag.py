# agents/simple_rag.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_cohere import CohereRerank
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from fastapi.responses import StreamingResponse
from typing import List, Optional
from dotenv import load_dotenv
import pickle
import asyncio
import config


# Hàm xử lý câu hỏi factual
def build_prompt(question: str, history: List[dict], knowledge: str) -> str:
    return f"""
You are an assistant that answers questions based only on the provided knowledge.
Do not use prior knowledge or mention the source information.
Use only the content from the section "The knowledge".

The question: {question}

Conversation history: {history}

The knowledge: {knowledge}
"""

async def simple_rag(question: str, history: List[dict], retriever, reranker, llm) -> StreamingResponse:
    # Step 1: Retrieve related documents
    docs = retriever.invoke(question)

    # Step 2: We keep 4 results from 8 retrieved documents
    reranked_results = reranker.rerank(query=question, documents=docs, top_n=4)
    reranked_docs = [docs[item["index"]] for item in reranked_results]

    # Step 3: Build the prompt
    knowledge = "\n".join(doc.page_content for doc in reranked_docs)
    prompt = build_prompt(question, history, knowledge)

    # Bước 4: Trả kết quả dạng stream
    async def stream_generator():
        full_response = ""
        try:
            async for chunk in llm.astream(prompt):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    full_response += content
                    yield content
                    await asyncio.sleep(0.06)
            history.append({"user": question, "assistant": full_response})
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(stream_generator(), media_type="text/plain")
