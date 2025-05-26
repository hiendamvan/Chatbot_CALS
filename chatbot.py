from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings 
from langchain_ollama import ChatOllama
import gradio as gr 
import os 

# import env file 
from dotenv import load_dotenv 
load_dotenv()

# configuration 
DATA_PATH = r'data'
CHROMA_PATH = r'chroma_db'

# initialize the embedding model 
embedding = CohereEmbeddings(
    cohere_api_key=os.getenv('COHERE_API_KEY'), 
    model='embed-multilingual-v3.0'
)

# initialize the chat model 
llm = ChatOllama(
    model='qwen3:0.6b',
    temperature=0.7, 
    num_predict=512,
)

# connect to database 
vector_store = Chroma(
    collection_name='vcc_env',
    embedding_function=embedding,
    persist_directory=CHROMA_PATH
)

# Set up vector store 
num_results = 3
retriever = vector_store.as_retriever(
    search_type='similarity',
    search_kwargs={
        'k': num_results,
    }
)

# call this function for every message added to the chatbot
def stream_response(message, history):
    # retrieve relavant chunks according to the message 
    docs = retriever.invoke(message)
    knowledge = ''
    for doc in docs:
        knowledge += doc.page_content + '\n'

    # call LLM 
    if message is not None: 
        partial_message = ""

        rag_prompt = f"""
        You are an assistent which answers questions based on knowledge which is provided to you.
        While answering, you don't use your internal knowledge, 
        but solely the information in the "The knowledge" section.
        You don't mention anything to the user about the povided knowledge.

        The question: {message}

        Conversation history: {history}

        The knowledge: {knowledge}

        """

        print(rag_prompt)
        
        # stream the response to the Gradio app 
        for response in llm.stream(rag_prompt):
            partial_message += response.content
            yield partial_message
          
# gradio chatbot interface 
chatbot = gr.ChatInterface(
    stream_response,
    textbox=gr.Textbox(placeholder="Send a message...",
    autoscroll=True, 
    scale=7),
    title="VCC Environment Chatbot",
)

chatbot.launch()