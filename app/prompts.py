quiz_text_template = """\
Text: {text}

You are a {systemInstruction} helping {customInstruction} in {tone} style. \
Given the above text, it is your job to create a quiz of {number} {type} that are {difficulty} difficult to guess. \
Make sure that questions are not repeated and check all the questions to be conforming to the text as well. \
Make sure to format your response like the example JSON format below and use it as a guide. \
Ensure to make the {number} MCQ(s). \
Strictly respond in the following JSON format: \
{{ \
"mcq": "multiple choice question", \
"options": {{ \
    "a": "choice here", \
    "b": "choice here", \
    "c": "choice here", \
    "d": "choice here", \
}}, \
"correct-answer": "correct answer reference", \
"correct-answer-explanation": "Give a explanation why the answer is correct by referencing the source it was generated from.", \
"correct-answer-hint": "Give a short, not easily guessable hint to help identify the correct answer without providing the answer directly.", \
}} \
"""

old_mcq_template = """ \
Text: {text} \
You are an expert quiz maker helping students to learn the most important information quickly. \
Given the above text, it is your job to create a quiz of {number} multiple choice questions with {difficulty} difficulty. \
Make sure that questions are not repeated and check all the questions to be conforming to the text as well. \
Make sure to format your response like the example JSON format below and use it as a guide. \
Ensure to make the {number} MCQ(s). \
Strictly respond in the following JSON format: \
{{ \
"mcq": "multiple choice question", \
"question-source": "For the correct answer, write source text the question was generated from", \
"options": {{ \
    "a": "choice here", \
    "b": "choice here", \
    "c": "choice here", \
    "d": "choice here", \
}}, \
"correct-answer": "correct answer reference", \
"correct-answer-explanation": "Give a explanation why the answer is correct by referencing the source it was generated from.", \
"correct-answer-hint": "Give a short but helpful indirect hint to the identify the correct answer without providing it directly.", \
}} \
"""

qa_template ="""
Step1:

Generate one distinct question-answer pairs from on the following text: {chunk}.
Q: Write Question Here
A: Write Answer Here
Question Source: Extract the source text of the question and write it here
Answer Source: Extract the source text of the answer and write it here
"""

mcq_template ="""
Step2:

Question Answer Pairs: {question_answers}

For each of the generated pairs, create multiple choice answers that are difficult to guess. \
Make sure that answers are not repeated and check all the questions to be conforming to the question-answer pairs as well. \
Make sure to format your response like the example JSON format below and use it as a guide. \
Ensure to make 3 incorrect answers and keep the correct one. \
Strictly respond in the following JSON format: \
{{ \
"mcq": "multiple choice question", \
"question-source": "For the correct answer, write source text the question was generated from", \
"options": {{ \
    "a": "choice here", \
    "b": "choice here", \
    "c": "choice here", \
    "d": "choice here", \
}}, \
"correct-answer": "correct answer reference", \
"correct-answer-explanation": "Give a explanation why the answer is correct by referencing the source it was generated from.", \
"correct-answer-hint": "Give a short but helpful indirect hint to the identify the correct answer without providing it directly.", \
}} \
"""