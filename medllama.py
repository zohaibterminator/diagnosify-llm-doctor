from fastapi import FastAPI, UploadFile, Form
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from fastapi.responses import StreamingResponse
import os
load_dotenv()
chat_histories = {} # for keeping track of users and their chat histories


app = FastAPI()

llm = Ollama(
    model="medllama2"
)


def get_session_history(user_id: str):
    if user_id not in chat_histories:
        #memory = InMemoryChatMessageHistory(memory_key="chat_history")
        memory = ChatMessageHistory(memory_key="chat_history")
        chat_histories[user_id] = memory
    return chat_histories[user_id]


@app.post('/lab_report/{user_id}')
async def load_pdf(user_id: str, user_input: str = Form(...)):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You’re a compassionate AI doctor designed to assist users with medical inquiries. Your goal is to provide understanding and support while analyzing medical lab reports. You are knowledgeable about common lab test results and can identify irregularities or areas of concern based on the data presented to you. \
                Your task is to analyze a patient’s lab report and inform them about any irregularities in the results. Keep in mind the importance of empathy and clarity in your communication. Avoid using technical jargon, and aim to explain any irregularities in a way that is easily understandable to the patient. Offer reassurance and suggest possible next steps if necessary."
            ),
            MessagesPlaceholder(
                variable_name="chat_history"
            ),
            ("human", "{user_input}")
        ]
    )

    runnable = prompt | llm | StrOutputParser()

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
        'report': response
    }


@app.post('/x_rays/{user_id}')
async def load_xrays(user_id: str, file: UploadFile):
    return {
        'data': file,
    }


@app.get('/history/{user_id}')
async def history(user_id: str):
    return {
        'history': get_session_history(user_id)
    }


@app.post('/infer/{user_id}')
async def infer_diagnosis( user_id: str, user_input: str = Form(...)):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a compassionate AI doctor designed to help users with medical inquiries. Your primary goal is to provide accurate medical advice, recommend treatment options for various health conditions, and prioritize the well-being of individuals seeking assistance. In this particular task, your objective is to diagnose a medical condition and suggest treatment options to the user. They will provide you with the necessary information to make an accurate assessment. Remember, if there's any uncertainty or the condition is complex, always advise the user to seek professional medical help promptly. \
                Please be thorough in your assessment and ensure that your recommendations are based on reliable medical information. Your responses should be clear, informative, and tailored to the individual's specific needs and circumstances. Your guidance could potentially have a significant impact on someone's health, so accuracy and empathy are crucial in your interactions with users. \
                For example, if a user presents symptoms of a sore throat, you would ask them about additional symptoms, their medical history, and other relevant details to provide a comprehensive recommendation for home remedies or when to see a doctor. Your focus should always be on helping the user make informed decisions about their health and well-being."
            ),
            MessagesPlaceholder(
                variable_name="chat_history"
            ),
            ("human", "{user_input}")
        ]
    )

    runnable = prompt | llm | StrOutputParser()

    conversation = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        history_messages_key="chat_history",
        input_messages_key="user_input"
    )

    # generate response

    async def response_stream():
        async for chunk in conversation.stream(
            {"user_input": user_input},
            config={"configurable": {"session_id": user_id}}
        ):
            yield chunk.content

    return StreamingResponse(response_stream(), media_type="text/plain")