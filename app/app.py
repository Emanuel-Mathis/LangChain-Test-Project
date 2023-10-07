from fastapi import FastAPI, HTTPException, Response
from app.handler.openai_handler import OpenAIHandler
from app.models import QuizRequest
from app.utils.pdf_text_extraction import PDFTextExtraction
from app.utils.quiz_validation import QuizTypeValidation
from app.utils.url_reader import get_pdf_from_raw_data
from app.prompts import quiz_text_template
from app.utils.topic_extraction import TopicExtraction
import os
import random
import asyncio
import json
from app.handler.firebase_handler import FirebaseHandler
from functools import cache
import mimetypes

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.handler.langchain_chain_handler import LangchainChainHandler

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
    elif (quizRequest.inputType.upper() == "TOPIC"):
        get_topics = TopicExtraction()
        retrieved_data = get_topics.run_topic_agent(quizRequest.input)
        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1024,
                chunk_overlap=32,  # number of tokens overlap between chunks
                length_function=len,
                separators=['\n\n', '\n', ' ', '']
            )
        chunks = text_splitter.split_text(retrieved_data)

    #determine number of questions to generate from text
    number_questions = quizRequest.quizOptions.numberQuestions or 10
    chunk_length = len(chunks)
    selected_chunks = []
    number_questions_per_chunk = 1.0
    if (chunk_length < number_questions):
        #less chunks than number of questions means we need to increase the number of questions per chunk
        number_questions_per_chunk = number_questions // chunk_length
        selected_chunks = chunks
    else:
        #too many chunks means we need to select 
        selected_chunks = random.sample(chunks, k=number_questions)

    print(selected_chunks)
    #prepare prompts
    prompt_list = []
### new implementation
    langchain_handler = LangchainChainHandler()
    handler_response = await langchain_handler.generate_concurrently(selected_chunks)
    print(handler_response)
    response_list = {'body':[]}
    for response in handler_response:
        single_response = json.loads(response)
        response_list['body'].append(single_response)

    final_response = json.dumps(response_list)
    return Response(content=final_response, media_type="application/json")  
"""     langchain_handler = LangchainChainHandler()
    for chunk in selected_chunks:
        print(langchain_handler.get_mcqs_from_chunk(chunk, 1.0, difficulty="medium"))

    return Response(content="success", media_type="application/json") """

### past implementation
"""     for chunk in selected_chunks:
        variables = {"text": chunk, \
                    "systemInstruction": quizRequest.quizOptions.systemInstruction, \
                    "customInstruction": quizRequest.quizOptions.systemInstruction, \
                    "tone": quizRequest.quizOptions.tone, \
                    "number": int(number_questions_per_chunk), \
                    "type": quizRequest.quizOptions.type, \
                    "difficulty": quizRequest.quizOptions.difficulty, \
                    }
        full_prompt = quiz_text_template.format(**variables)
        prompt_list.append([{"role": "user", "content": full_prompt}])
    #call openai
    temperature=0.1
    handler_response = await handler.send_prompt_openai_async(temperature, prompt_list)
    if (handler_response is None):
        raise HTTPException(status_code=400, detail="No response from OpenAI")
    generated_value = ""
    for i, x in enumerate(handler_response):
        #json_response.extend(x['choices'][0]['message']['content'])
        generated_value += x["choices"][0]['message']['content']
        if i != len(handler_response) - 1:
            generated_value += ", "

    return Response(content=generated_value, media_type="application/json") """

@cache
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

    #determine number of questions to generate from text
    number_questions = quizRequest.quizOptions.numberQuestions or 10
    chunk_length = len(chunks)
    selected_chunks = []
    number_questions_per_chunk = 1.0
    if (chunk_length < number_questions):
        #less chunks than number of questions means we need to increase the number of questions per chunk
        number_questions_per_chunk = number_questions // chunk_length
        selected_chunks = chunks
    else:
        #too many chunks means we need to select 
        selected_chunks = random.sample(chunks, k=number_questions)

    #prepare prompts
    prompt_list = []
    for chunk in selected_chunks:
        variables = {"text": chunk, \
                    "systemInstruction": quizRequest.quizOptions.systemInstruction, \
                    "customInstruction": quizRequest.quizOptions.systemInstruction, \
                    "tone": quizRequest.quizOptions.tone, \
                    "number": int(number_questions_per_chunk), \
                    "type": quizRequest.quizOptions.type, \
                    "difficulty": quizRequest.quizOptions.difficulty, \
                    }
        full_prompt = quiz_text_template.format(**variables)
        prompt_list.append([{"role": "user", "content": full_prompt}])
    #call openai
    temperature=0.1
    handler_response = await handler.send_prompt_openai_async(temperature, prompt_list)
    if (handler_response is None):
        raise HTTPException(status_code=400, detail="No response from OpenAI")
    merged_response = []
    #test_response = {}
    generated_value = ""
    for i, x in enumerate(handler_response):
        #json_response.extend(x['choices'][0]['message']['content'])
        generated_value += x["choices"][0]['message']['content']
        if i != len(handler_response) - 1:
            generated_value += ", "

    return Response(content=generated_value, media_type="application/json")

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