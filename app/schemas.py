#from typing import List
from pydantic import BaseModel

class Quiz(BaseModel):
    input: str
    inputType: str
    quizType: str
    numberQuestions: int