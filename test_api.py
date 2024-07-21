from fastapi import FastAPI, UploadFile, Form
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq
import os
load_dotenv()
chat_histories = {} # for keeping track of users and their chat histories


app = FastAPI()

llm = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key=os.getenv('GROQ_API')
)


def get_session_history(user_id: str):
    if user_id not in chat_histories:
        memory = InMemoryChatMessageHistory(memory_key="chat_history")
        chat_histories[user_id] = memory
    return chat_histories[user_id]


@app.post('/lab_report')
async def load_pdf(file: UploadFile):
    extension = file.filename[-3:]

    if extension != 'pdf':
        return {
            'data': 'Invalid file format',
            'extension': extension
        }

    loader = PyMuPDFLoader(file.filename)
    pages = loader.load_and_split()
    return {
        'data': pages[0].page_content
    }


@app.post('/x_rays')
async def load_xrays(file: UploadFile):
    return {
        'data': file
    }


@app.post('/infer/{user_id}')
async def infer_diagnosis( user_id: str, user_input: str = Form(...)):
    # Define the messages for the Ollama model
    

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI doctor who can help diagnose medical conditions and give recommendations for treating diseases. If you don't know the answer to a specific medical inquiry, advise seeking professional help. Keep your diagnoses concise"
            ),  # The persistent system prompt
            MessagesPlaceholder(
                variable_name="chat_history"
            ),  # Where the memory will be stored.
            ("human", "{user_input}")  # Where the human input will injected
        ]
    )

    runnable = prompt | llm

    conversation = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        history_messages_key="chat_history",
        input_messages_key="user_input"
    )

    # Generate response
    response = conversation.invoke(
        {"user_input": user_input},
        config={"configurable": {"session_id": user_id}}
    )

    return {
        'response': response
    }