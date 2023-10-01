import os
import re
import json
import random
import warnings

class GenerateQuiz:
    '''
    A class containing functions to generate quizzes using OpenAI
    '''

    def __init__(self, content):
        self.content = content
