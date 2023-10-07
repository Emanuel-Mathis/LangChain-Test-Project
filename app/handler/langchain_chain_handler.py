from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

import asyncio

from app.prompts import qa_template, mcq_template

from dotenv import find_dotenv, load_dotenv
import openai
import os

class LangchainChainHandler:
    def __init__(
        self,
        model="gpt-3.5-turbo",
    ):
        load_dotenv(find_dotenv())
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.model = model
        self.llm = OpenAI(temperature= 0, model=self.model)
    
    def __get_mcqs_from_chunk(self):
        qa_prompt = PromptTemplate(
            input_variables=["chunk"],
            template = qa_template                      
        )

        qa_chain = LLMChain(
            llm=ChatOpenAI(temperature=0, model=self.model),
            prompt=qa_prompt
        )

        mcq_prompt = PromptTemplate(
            input_variables=["question_answers"],
            template = mcq_template                      
        )

        mcq_chain = LLMChain(
            llm=ChatOpenAI(temperature=0, model=self.model),
            prompt=mcq_prompt
        )

        overall_chain = SimpleSequentialChain(
            chains=[qa_chain, mcq_chain],
            verbose=True
        )

        return overall_chain

    async def async_generate(self, chain, inputs):   
        with get_openai_callback() as cb:
            resp = await chain.arun(inputs)
        return resp
    
    async def generate_concurrently(self, chunks):
        chain = self.__get_mcqs_from_chunk()

        tasks = []
        for chunk in chunks:
            inputs={
                        "chunk": chunk,
                        "question_answers": ""
                    }
            tasks.append(self.async_generate(chain, chunk))

        results = await asyncio.gather(*tasks)
        return results
