import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.document_loaders import PyMuPDFLoader
import requests
import os
import json
import fitz
import asyncio
load_dotenv()

user_id = "1"


def extract_pdf_text(file):
    # Use PyMuPDF to extract text from the PDF file
    if file is not None:
        document = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        with open('test_file_fitz.txt', 'w') as f:
            f.write(text)
        return text, True
    return "", False


async def get_streamed_response(user_input, report):
    if not report:
        url = f"http://127.0.0.1:8000/infer/{user_id}"
    else:
        url = f"http://127.0.0.1:8000/lab_report/{user_id}"

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"user_input": user_input}

    response = requests.post(url, headers=headers, data=data, stream=True)

    response_text = ""
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            response_text += chunk.decode()
            yield response_text
    

st.set_page_config(page_title="Diagnosify", page_icon="🤖")
st.title("Diagnosify")

res = requests.get(url=f"http://127.0.0.1:8000/history/{user_id}")
data = res.json()
st.session_state.chat_history = data['history']['messages']

user_query = ""
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Files")
    lab_report = st.file_uploader(
        label="Upload File",
        type=["pdf"],
        accept_multiple_files=False,
        label_visibility="collapsed"
    )

    report_result, report = extract_pdf_text(lab_report)

    if report:
        user_query = report_result

    # Add some vertical space to push the file uploader down
    st.markdown("<br>" * 10, unsafe_allow_html=True)

with col2:
    st.subheader("Hello, User") # Replace with name of user, depending on whether the user is new or not
    for message in st.session_state.chat_history:
        if message != []:
            if message['type'] == "human":
                with st.chat_message("Human"):
                    st.markdown(message['content'])
            else:
                with st.chat_message("AI"):
                    st.markdown(message['content'])

    if not report:
        user_query = st.chat_input("Your message")
    if user_query:
        with st.chat_message("Human"):
            st.markdown(user_query)

        response_placeholder = st.empty()
        response_text = ""

        for chunk in asyncio.run(get_streamed_response(user_query, lab_report is not None)):
            response_text = chunk
            with st.chat_message("AI"):
                response_placeholder.markdown(response_text)

# custom CSS to style the file uploader
css = '''
<style>
    [data-testid='stFileUploader'] {
        width: max-content;
    }
    [data-testid='stFileUploader'] section {
        padding: 0;
        float: left;
    }
    [data-testid='stFileUploader'] section > input + div {
        display: none;
    }
    [data-testid='stFileUploader'] section + div {
        float: right;
        padding-top: 0;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)