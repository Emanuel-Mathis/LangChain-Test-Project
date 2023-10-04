import fitz
import requests
import io
import sys
from fastapi import HTTPException

""" def get_raw_file_data_url(url):
    try:
        request = requests.get(url)
    except requests.exceptions.HTTPError as e:
        print(e, file=sys.stderr)
        raise HTTPException(status_code=requests.exceptions.HTTPError, detail="File request failed")
    filestream = io.BytesIO(request.content)
    return filestream
 """

def get_pdf_from_raw_data(file_content):
    pdf = io.BytesIO(file_content.content)
    doc = fitz.open(stream=pdf)
    return doc
"""     with fitz.open(stream=pdf) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    print(text) """