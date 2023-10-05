from fastapi import FastAPI, HTTPException
from app.handler.openai_handler import OpenAIHandler
from app.models import Quiz, QuizRequest
from app.utils.pdf_text_extraction import PDFTextExtraction
from app.utils.quiz_validation import QuizTypeValidation
from app.utils.url_reader import get_pdf_from_raw_data
from app.prompts import mcq_template, quizbot_text_template
import os
import random
import asyncio
import json
from app.handler.firebase_handler import FirebaseHandler
from functools import cache
import mimetypes

from langchain.text_splitter import RecursiveCharacterTextSplitter

import sys

app = FastAPI()
handler = OpenAIHandler()

@app.get("/")
async def root():
    return {"message": "We are live!"}

@cache
@app.post("/v1/testudy")
async def query_endpoint(quizRequest: QuizRequest):
    #validate QuizInput against business rules
    quiz_validation = QuizTypeValidation(quizRequest)
    validation_response = quiz_validation.testudy_validate_request()
    if (validation_response[0] != 200):
        raise HTTPException(status_code=validation_response[0], detail=validation_response[1])

    #determine data source
    chunks = []
    if (quizRequest.inputType.upper() == "TEXT"):
        #preprocess text (clean it & split it)
        input_text = quizRequest.input.strip()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=32,  # number of tokens overlap between chunks
            length_function=len,
            separators=['\n\n', '\n', ' ', '']
        )
        chunks = text_splitter.split_text(input_text)
    elif (quizRequest.inputType.upper() == "FIREBASEURL"):
        firebase_handler = FirebaseHandler()
        firebase_file_url = firebase_handler.retrieve_url_from_firebase_file_name(quizRequest.input)
        file_content = firebase_handler.retrieve_from_url(firebase_file_url)
        file_extension_guess = file_content.headers['content-type']
        file_extension = mimetypes.guess_extension(file_extension_guess)
        print("-- repsonse code")
        print(file_content.status_code)
        print("-- url")
        print(firebase_file_url)
        print(file_extension)
        if (file_extension == ".pdf"):
            pdf_doc = get_pdf_from_raw_data(file_content)
            pte = PDFTextExtraction(pdf_doc)
            content = pte.get_pdf_data()
            text = ''
            for page in content['elements']:
                text = ' '.join(page['text'])
                if len(text) > 200:
                    chunks.append((text, page['page']))
        elif (file_extension == ".txt"):
            input_text = file_content.text.strip()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1024,
                chunk_overlap=32,  # number of tokens overlap between chunks
                length_function=len,
                separators=['\n\n', '\n', ' ', '']
            )
            chunks = text_splitter.split_text(input_text)
        else:
            raise HTTPException(status_code=400, detail="File type not supported!")

    print("--")
    print(len(chunks))
    print(chunks)
    print("--")
    #determine number of questions to generate from text
    number_questions = quizRequest.quizOptions.numberQuestions or 10
    chunk_length = len(chunks)
    selected_chunks = []
    number_questions_per_chunk = 1.0
    if (chunk_length < number_questions):
        #less chunks than number of questions means we need to increase the number of questions per chunk
        number_questions_per_chunk = number_questions // chunk_length
        selected_chunks = chunks
        print("-- number questions")
        print(number_questions_per_chunk)
        print("--")
    else:
        #too many chunks means we need to select 
        selected_chunks = random.sample(chunks, k=number_questions)
        print("-- chunks")
        print(selected_chunks)
        print("--")

    #prepare prompts
    print("-- expected prompts")
    print(chunk_length)
    prompt_list = []

    for chunk in selected_chunks:
        variables = {"text": chunk, "number": int(number_questions_per_chunk), "difficulty": "medium"}
        full_prompt = mcq_template.format(**variables)
        prompt_list.append([{"role": "user", "content": full_prompt}])
    print("-- actual prompts")
    print(prompt_list)
    #call openai
    temperature=0.1
    handler_response = await handler.send_prompt_openai_async(temperature, prompt_list)
    #handler_response = asyncio.run(handler.send_prompt_openai_async(temperature, prompt_list))
    #handler_response = await handler.run_openai_async(temperature, prompt_list)
    if (handler_response is None):
        raise HTTPException(status_code=400, detail="No response from OpenAI")
    merged_response = []
    for i, x in enumerate(handler_response):
        print(f"Response {i}: {x['choices'][0]['message']['content']}\n\n")
        merged_response.append(x['choices'][0]['message']['content'])
    print("-- merged output")
    print(merged_response)
    json_response = json.loads(merged_response[0])

    return {"response": json_response}

#@cache
@app.post("/v1/quizbot")
async def query_endpoint(quizRequest: QuizRequest):

    #validate QuizInput against business rules
    quiz_validation = QuizTypeValidation(quizRequest)
    validation_response = quiz_validation.quizbot_validate_request()
    if (validation_response[0] != 200):
        raise HTTPException(status_code=validation_response[0], detail=validation_response[1])
    
    #determine data source
    chunks = []
    if (quizRequest.inputType.upper() == "TEXT"):
        #preprocess text (clean it & split it)
        input_text = quizRequest.input.strip()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=32,  # number of tokens overlap between chunks
            length_function=len,
            separators=['\n\n', '\n', ' ', '']
        )
        chunks = text_splitter.split_text(input_text)

    print("--")
    print(len(chunks))
    print(chunks)
    print("--")
    #determine number of questions to generate from text
    number_questions = quizRequest.quizOptions.numberQuestions or 10
    chunk_length = len(chunks)
    selected_chunks = []
    number_questions_per_chunk = 1.0
    if (chunk_length < number_questions):
        #less chunks than number of questions means we need to increase the number of questions per chunk
        number_questions_per_chunk = number_questions // chunk_length
        selected_chunks = chunks
        print("-- number questions")
        print(number_questions_per_chunk)
        print("--")
    else:
        #too many chunks means we need to select 
        selected_chunks = random.sample(chunks, k=number_questions)
        print("-- chunks")
        print(selected_chunks)
        print("--")

    #prepare prompts
    print("-- expected prompts")
    print(chunk_length)
    prompt_list = []

    for chunk in selected_chunks:
        variables = {"text": chunk, "tone": quizRequest.quizOptions.tone, "number": int(number_questions_per_chunk), "difficulty": "medium"}
        full_prompt = quizbot_text_template.format(**variables)
        prompt_list.append([{"role": "user", "content": full_prompt}])
    print("-- actual prompts")
    print(prompt_list)
    #call openai
    temperature=0.1
    handler_response = await handler.send_prompt_openai_async(temperature, prompt_list)
    if (handler_response is None):
        raise HTTPException(status_code=400, detail="No response from OpenAI")
    merged_response = []
    for i, x in enumerate(handler_response):
        print(f"Response {i}: {x['choices'][0]['message']['content']}\n\n")
        merged_response.append(x['choices'][0]['message']['content'])
    print("-- merged output")
    print(merged_response)
    json_response = json.loads(merged_response[0])
    return {"response": json_response}

""" @app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    create_pizzas()
    if not os.path.exists("vectorstore.pkl"):
        create_store()


@app.on_event("shutdown")
async def shutdown_event():
    os.remove("pizzadb.db")


@app.post("/conversation")
async def query_endpoint(interaction: Interaction):
    response = handler.send_response(interaction.query)
    return {"response": response}


@app.get("/reviews")
async def get_all_reviews():
    session = Session()
    reviews = session.query(Review).all()
    session.close()
    return reviews


@app.get("/orders")
async def get_all_orders():
    session = Session()
    orders = session.query(Order).all()
    session.close()
    return orders
 """