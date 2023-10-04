mcq_template_old = """
Generate {number} distinct questions with 1 correct answer and 3 wrong answers from the text below and indicate the source paragraph of the question & answer it was generated from.
Strictly respond in the following JSON format like in the following examples:
[{{
    "question": "What did the Home Rule Bill propose for Ireland?",
    "answer-a": "Complete independence from the UK",
    "answer-b": "Becoming a part of France",
    "answer-c": "A self-governing Ireland with its own parliament but still part of the UK",
    "answer-d": "Absorption into the British government",
    "correct-answer": "answer-c",
    "question-source": "The proposal was to have a self-governing Ireland with its own parliament but still part of the UK.",
    "answer-source": "A self-governing Ireland with its own parliament but still part of the UK"
}}]
Text: '{text}'
"""

mcq_template = """
Text: {text} \
You are an expert quiz maker helping students to learn the most important information quickly. \
Given the above text, it is your job to create a quiz of {number} multiple choice questions with {difficulty} difficulty. \
Make sure that questions are not repeated and check all the questions to be conforming to the text as well. \
Make sure to format your response like the example JSON format below and use it as a guide. \
Ensure to make the {number} MCQ(s). \
Strictly respond in the following JSON format: \
{{ \
"mcq": "multiple choice question", \
"question-source": "Add the source text the question was generated from here", \
"options": {{ \
    "a": "choice here", \
    "b": "choice here", \
    "c": "choice here", \
    "d": "choice here", \
}}, \
"correct-answer": "correct answer reference", \
"correct-answer-explanation": "Explanation why the answer is correct by referencing the source it was generated from.", \
"correct-answer-hint": "Give a short but helpful indirect hint to the identify the correct answer without providing it directly.", \
}} \
"""
