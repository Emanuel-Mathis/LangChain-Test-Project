import json
import os
import asyncio
import openai
from dotenv import find_dotenv, load_dotenv
from typing import Any

class OpenAIHandler:
    def __init__(
        self,
        model="gpt-3.5-turbo",
    ):
        load_dotenv(find_dotenv())
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.model = model
    
    async def send_prompt_openai_async(self, temperature: float, messages_list: list[list[dict[str,Any]]]):
        print("--messages list")
        print(messages_list)
        try:
            async_responses = [
                openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=message,
                    temperature=temperature,
                    top_p=1.0,
                )
                for message in messages_list
            ]
            
            return await asyncio.gather(*async_responses)
        except Exception as exc:
            print(exc)            

    def run_openai_async(self, temperature: float, messages_list: list[list[dict[str,Any]]]):
        return asyncio.gather(self.send_prompt_openai_async(temperature, messages_list))