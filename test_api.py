from fastapi import FastAPI
from langchain_community.document_loaders import PyMuPDFLoader
path = r"C:\Users\shahe\OneDrive\Desktop\NLP Sessions\Project\Diagnosify\04012024HR8220R.pdf"


app = FastAPI()

@app.post('/pdf')
def load_pdf(path):
    loader = PyMuPDFLoader(path)
    pages = loader.load_and_split()
    return {
        'data': pages[0].page_content
    }


@app.post('/x_rays')
def load_xrays(data):
    #loader
    return {
        'data': 'working'
    }