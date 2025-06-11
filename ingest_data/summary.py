'''
Use LLM to summarize chunk ans table, use this summary for embedding 
'''
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_ollama import ChatOllama
import os

def summarize(text):
    # Prompt
    prompt_text = """You are an assistant tasked with summarizing tables and text. \ 
    Give a concise summary of the table or text. Table or text chunk: {element} """
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # model 
    #model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # Initialize LLM
    llm = ChatOpenAI(model= 'gpt-4.1-nano', 
                    openai_api_key=os.getenv('') )
    
    summarize_chain = {"element": lambda x: x} | prompt | llm | StrOutputParser()
    summary = summarize_chain.invoke(text)
    return summary
