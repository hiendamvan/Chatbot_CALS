# agents/classifier.py
from langchain_openai import ChatOpenAI
import config
llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0.1)

def classify_question(question: str) -> str:
    """
    Classify user question into one of the following categories:
    - greeting
    - multi-hop
    - simple 

    """
    prompt = f"""
You are a classification assistant.

Classify the following question into one of the categories:
- **greeting**: if the question is a greeting or salutation (e.g., "hi", "hello", "good morning", "who are you?").
- **simple**: if the question can be answered by retrieving a single relevant document or a single fact from the knowledge base. These questions do NOT require combining information from multiple sources or steps of reasoning. Example: "Who is the leader of department X?", "What year was the project approved?".
- **multi-hop**: if the question requires combining multiple pieces of information from different documents or needs reasoning across several facts to answer. These questions usually need multiple steps to reach the answer. Example: "Which department leads the vertical that handles project A?", "What units are involved in implementing the strategy and who oversees them?".

Return only the category name.

Question: {question}
Type:"""

    try:
        response = llm.invoke(prompt)
        category = response.content.strip().lower()

        if category not in ["greeting", "multi-hop", "simple"]:
            return "unknown"
        return category
    except Exception as e:
        print(f"[Classifier Error] {e}")
        return "unknown"
