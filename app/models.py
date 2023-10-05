from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

class Quiz(BaseModel):
    input: str
    inputType: str
    quizType: str
    numberQuestions: int

class QuizOptions(BaseModel):
    type: Optional[str] = "Text"
    difficulty: Optional[str] = "Medium"
    numberQuestions: Optional[int] = 2
    tone: Optional[str] = "Educational"
    systemInstruction: Optional[str] = "Expert Quizmaker"
    topicInstruction: Optional[str] = ""

class QuizRequest(BaseModel):
    input: str
    inputType: str
    quizType: str
    quizOptions: QuizOptions
