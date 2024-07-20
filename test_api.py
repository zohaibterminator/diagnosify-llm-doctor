from fastapi import FastAPI, UploadFile, Form
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()

llm = ChatOllama(
    model_name=os.getenv('OLLAMA_MODEL_NAME'),
    tempreture=0
)


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


@app.post('/infer')
async def infer_diagnosis(user_input: str = Form(...)):
    # Define the messages for the Ollama model
    messages = [
        (
            "system",
            "You are a helpful AI doctor, who can help diagnose medical conditions and give recommendations for treating diseases. If you don't know the answer to a specific medical inquiry, advise seeking professional help.",
        ),
        (
            "human", user_input
        ),
    ]

    # Perform inference with the Ollama model
    ai_msg = llm.invoke(messages)
    return {
        'diagnosis': ai_msg.content
    }