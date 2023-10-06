from dotenv import find_dotenv, load_dotenv
import os
import requests
import json
import sys
from fastapi import HTTPException
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType, load_tools

class TopicExtraction:
    def __init__(
        self,
        model="gpt-3.5-turbo-0613",
    ):
        load_dotenv(find_dotenv())
        open_ai_api_key = os.environ.get("OPENAI_API_KEY")
        if open_ai_api_key is None:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.model = model
        self.llm = OpenAI(openai_api_key=open_ai_api_key)
        self.tools = load_tools(["wikipedia"], llm=self.llm)
        self.zero_shot_agent = initialize_agent(
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            max_interations=3,
        )

    def run_topic_agent(self, topic):
        try:
            response = self.zero_shot_agent.run(topic)
        except requests.exceptions.HTTPError as e:
            print(e, file=sys.stderr)
            raise HTTPException(status_code=requests.exceptions.HTTPError, detail="File request failed")
        return response
    