import os
import re
import json
import random
import fitz
import warnings
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
#from langchain_contrib.prompts import ChainedPromptTemplate
from app.schemas import Quiz

class QuizTypeValidation:
    '''
    A class containing functions to validate input from post request and return success/error message
    '''

    def __init__(self, quiz):
        self.quiz = quiz
    
    def validate_request(self):
        response = (200, 'Success')
        if (not self.quiz.input):
            response = (422, 'Invalid input!')
            return response
        
        if (len(self.quiz.input) < 50):
            response = (422, 'Input must be more than 50 characters')
            return response
        
        if (self.quiz.inputType.upper() != 'TEXT'):
            response = (422, 'Only Text as input type supported!')
            return response

        if (self.quiz.quizType.upper() != 'MCQ'):
            response = (422, 'Only MCQ supported!')
            return response
        
        return response

class PDFTextExtraction:
    '''
    A class containing functions to extract text from pdf and remove header/footer
    '''

    def __init__(self, doc):
        self.doc = doc

    def __extract_text(self, page):
        '''Extract text from a page and returns a list of strings'''

        text = page.get_text(sort=True)
        text = text.split('\n')
        text = [t.strip() for t in text if t.strip()]

        return text

    def __compare(self, a, b):
        '''Fuzzy matching of strings to compare headers/footers in neighboring pages'''

        count = 0
        a = re.sub('\d', '@', a)
        b = re.sub('\d', '@', b)
        for x, y in zip(a, b):
            if x == y:
                count += 1
        return count / max(len(a), len(b))

    def __remove_header(self, elements, header_candidates, WIN):
        '''Extract headers from content dictionary. Helper function for extract_header_footer() function.'''

        header_weights = [1.0, 0.75, 0.5, 0.5, 0.5]
        detected = []

        for i, candidate in enumerate(header_candidates):
            temp = header_candidates[max(i-WIN, 1) : min(i+WIN, len(header_candidates))]
            maxlen = len(max(temp, key=len))
            for sublist in temp:
                sublist[:] =  sublist + [''] * (maxlen - len(sublist))

            for j, cn in enumerate(candidate):
                score = 0
                try:
                    cmp = list(list(zip(*temp))[j])
                    for cm in cmp:
                        score += self.__compare(cn,cm) * header_weights[j]
                    score = score/len(cmp)
                except:
                    score = header_weights[j]
                if score > 0.5:
                    detected.append(cn)
            del temp
            
            for d in detected:
                while d in elements[i]['text'][:6]:
                    elements[i]['text'].remove(d)

        return elements

    def __remove_footer(self, elements, footer_candidates, WIN):
        '''Extract footers from content dictionary. Helper function for extract_header_footer() function.'''

        footer_weights = [0.5, 0.5, 0.5, 0.75, 1.0]
        detected = []

        for i, candidate in enumerate(footer_candidates):
            temp = footer_candidates[max(i-WIN, 1) : min(i+WIN, len(footer_candidates))]
            maxlen = len(max(temp, key=len))
            for sublist in temp:
                sublist[:] =  [''] * (maxlen - len(sublist)) + sublist

            for j, cn in enumerate(candidate):
                score = 0
                try:
                    cmp = list(list(zip(*temp))[j])
                    for cm in cmp:
                        score += self.__compare(cn,cm)
                    score = score/len(cmp)
                except:
                    score = footer_weights[j]
                if score > 0.5:
                    detected.append(cn)
            del temp
            
            for d in detected:
                while d in elements[i]['text'][-6:]:
                    elements[i]['text'] = elements[i]['text'][::-1]
                    elements[i]['text'].remove(d)
                    elements[i]['text'] = elements[i]['text'][::-1]
                
        return elements

    def __remove_header_footer(self, elements):
        '''Extract headers and footers from all pages dynamically using page-association method'''
    
        header_candidates = []
        footer_candidates = []

        for element in elements:
            if element['text']: 
                header_candidates.append(element['text'][:5])
                footer_candidates.append(element['text'][-5:])

        WIN = 6
        if header_candidates and footer_candidates:
            elements = self.__remove_header(elements, header_candidates, WIN)
            elements = self.__remove_footer(elements, footer_candidates, WIN)

        return elements
    
    def get_pdf_data(self):
        '''Driver function to run end-to-end pdf parsing pipeline'''
    
        pages = self.doc.pages()
        content = dict()
        elements = []

        for idx, page in enumerate(pages):
            page_data = dict()
            text = self.__extract_text(self.doc[idx])

            page_data['page'] = idx
            page_data['text'] = text
            elements.append(page_data)

        content['elements'] = self.__remove_header_footer(elements)

        return content

class GenerateQuiz:
    '''
    A class containing functions to generate quizzes using OpenAI
    '''

    def __init__(self, content):
        self.content = content

    def __get_chunks(self):
        '''Divide the whole text in chunks of less than 5000 characters'''

        chunks = []
        text = ''
        for page in self.content['elements']:
            text = ' '.join(page['text'])
            if len(text) > 200:
                chunks.append((text, page['page']))
            
        return chunks

    def __get_prompt(self, chunk):
        '''Format prompt for each chunk of text'''
        
        #prompt = ChainedPromptTemplate([
        #    PromptTemplate.from_template("Generate 3 question-answer pairs based on the following text: {text}."),
        #    """Convert the above mentioned questions into mcqs, mention the correct answers for each question and include source paragraph of the correct answer.
        #    Example question:

        #    Question: question here
        #    CHOICE_A: choice here
        #    CHOICE_B: choice here
        #    CHOICE_C: choice here
        #    CHOICE_D: choice here
        #    Answer: A or B or C or D
        #    Source: here""",
        #    "Return only MCQs and source."
        #    ], joiner="\n\n")
        
        #formatted_prompt = prompt.format(text=chunk)
        formatted_prompt = ""
        return formatted_prompt

    def __convert_to_question_dicts(self, question_list, page):
        question_dicts = []
        current_question = {}
        page += 1

        for line in question_list:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Question: "):
                if current_question:
                    question_dicts.append(current_question)
                current_question = {'question': line[len(line.split(': ')[0]) + 2:]}
            elif line.startswith("CHOICE_A: "):
                current_question['a'] = line[len("CHOICE_A: "):]
            elif line.startswith("CHOICE_B: "):
                current_question['b'] = line[len("CHOICE_B: "):]
            elif line.startswith("CHOICE_C: "):
                current_question['c'] = line[len("CHOICE_C: "):]
            elif line.startswith("CHOICE_D: "):
                current_question['d'] = line[len("CHOICE_D: "):]
            elif line.startswith("Answer: "):
                current_question['answer'] = line[len("Answer: "):]
            elif line.startswith("Source: "):
                current_question['source'] = line[len("Source: "):]

        if current_question:
            question_dicts.append(current_question)

        for q in question_dicts:
            q['page'] = page
        
        return question_dicts

    def mcqs_generation(self, count):
        '''Generate MCQs against each chunk of text'''
        
        chunks = self.__get_chunks()
        random.shuffle(chunks)
        
        if count > len(chunks) * 2:
            raise Exception('File size is too small to generate {num} meaningful MCQs.'.format(num=count))
        else:
            mcqs = []
            for chunk in chunks:
                if len(mcqs) < count:
                    prompt = self.__get_prompt(chunk[0])
                    llm = OpenAI(temperature=.1, model_name = "gpt-3.5-turbo-0613", openai_api_key=openai_api_key)
                    result = llm(prompt)
                    mcqs += self.__convert_to_question_dicts(result.split('\n'), chunk[1])
            
            mcqs = mcqs[:count]
            random.shuffle(mcqs)
            
            with open('mcqs.json', 'w') as f:
                json.dump(mcqs, f, indent=4)