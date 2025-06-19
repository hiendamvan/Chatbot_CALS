# agents/multihop.py
from langchain.prompts import PromptTemplate
from fastapi.responses import StreamingResponse
from typing import List
import asyncio
import config

# Idea: IRCOT - Interleaving Retrieval with Reasoning for Multi-hop Question Answering
# Create sub-question prompt template and reasoning prompt template 
subq_prompt = PromptTemplate.from_template(
    "Given the question: '{question}', what would be a good sub-question to answer first?"
)

reasoning_prompt = PromptTemplate.from_template(
    "Original question: '{orig_question}'\n"
    "Current sub-question: '{sub_question}'\n"
    "Retrieved context (from documents):\n{context}\n\n"
    "Based only on the retrieved context, what is the next sub-question we should ask?\n"
    "If the context is enough to answer the original question, just say: 'Let's answer now'."
)

final_prompt = PromptTemplate.from_template(
    "We are answering the question: '{question}'.\n"
    "We have gone through the following reasoning and retrieved steps:\n"
    "{history}\n"
    "Based on the above reasoning and retrieved context, answer the original question.\n"
    "**Do not explain your reasoning or repeat the question.**"
)

async def multihop(question: str, history: List[dict], retriever, reranker, llm) -> StreamingResponse:
    subq_chain = subq_prompt | llm 
    reasoning_chain = reasoning_prompt | llm
    final_chain = final_prompt | llm

    history_steps = []
    current_query = question
    max_hops = config.MAX_HOPS

    for hop in range(max_hops):
        # Step 1: Retrieve and rerank documents using current query 
        docs = retriever.invoke(current_query)
        reranked_results = reranker.rerank(query=current_query, documents=docs, top_n=config.NUM_RESULTS-1)
        reranked_docs = [docs[item["index"]] for item in reranked_results]
        
        # for i, doc in enumerate(reranked_docs):
        #     print(f"Doc {i+1} for hop {hop+1}: {doc.page_content[:200]}...")

        knowledge = "\n".join(doc.page_content for doc in reranked_docs)

        # Step 2: Decide whether we need a sub-question
        subq = subq_chain.invoke({
            "question": current_query,
            "context": knowledge
        }).content.strip()
        #print(f"Sub-question for hop {hop+1}: {subq}")

        # Step 3: Reason whether to stop or continue
        next_query = reasoning_chain.invoke({
            "orig_question": question,
            "sub_question": subq,
            "context": knowledge
        }).content.strip()
        #print(f"Next query after reasoning (hop {hop+1}): {next_query}")

        history_steps.append((subq, knowledge))

        if next_query.lower() in ["let's answer now", "let’s answer now", "let us answer now"]:
            break
        if next_query.strip().lower() == current_query.strip().lower():
            break  # tránh lặp vô hạn

        current_query = next_query

    # Build history for final answer
    hist_text = ""
    for i, (subq, ctx) in enumerate(history_steps):
        hist_text += f"Step {i+1}:\nSub-question: {subq}\nContext:\n{ctx[:500]}...\n\n"

    final_inputs = {"question": question, "history": hist_text}

    # Step 4: Stream final answer
    async def stream_generator():
        full_response = ""
        try:
            async for chunk in final_chain.astream(final_inputs):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    full_response += content
                    yield content
                    await asyncio.sleep(0.03)
            history.append({"user": question, "assistant": full_response})
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(stream_generator(), media_type="text/plain")
