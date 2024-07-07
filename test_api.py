from fastapi import FastAPI, UploadFile
from langchain_community.document_loaders import PyMuPDFLoader


app = FastAPI()


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