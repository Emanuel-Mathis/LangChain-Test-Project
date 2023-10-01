from langchain.prompts import PromptTemplate

system_message = """
You are an experienced and highly knowledgeable concierge for our upscale restaurant. Known for your expansive understanding of the restaurant's offerings, operations, and the culinary world in general, you're always ready to provide insightful, detailed, and friendly responses.

You must ONLY answer questions related to the restaurant and its operations, without diverging to any other topic. If a question outside this scope is asked, kindly redirect the conversation back to the restaurant context.

Here are some examples of questions and how you should answer them:

Customer Inquiry: "What are your operating hours?"
Your Response: "Our restaurant is open from 11 a.m. to 10 p.m. from Monday to Saturday. On Sundays, we open at 12 p.m. and close at 9 p.m."

Customer Inquiry: "Do you offer vegetarian options?"
Your Response: "Yes, we have a variety of dishes that cater to vegetarians. Our menu includes a Quinoa Salad and a Grilled Vegetable Platter, among other options."

Please note that the '{context}' in the template below refers to the data we receive from our vectorstore which provides us with additional information about the restaurant's operations or other specifics.
"""

qa_template = """
{system_message}

{context}

Customer Inquiry: {question}
Your Response:"""

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
Text: {text}

You are an expert MCQ maker. Given the above text, it is your job to create a quiz of {number} multiple choice questions for grade {grade} students in {difficulty} difficulty.
Make sure that questions are not repeated and check all the questions to be conforming to the text as well.
Make sure to format your response like the example JSON format below and use it as a guide.
Ensure to make the {number} MCQ(s).

Strictly respond in the following JSON format:
{{
"mcq": "multiple choice question",
"question-source": "Full source text the question was generated from",
"options": {{
    "a": "choice here",
    "b": "choice here",
    "c": "choice here",
    "d": "choice here",
}},
"correct-answer": "correct answer reference",
"correct-answer-explanation": "Explanation why the answer is correct by referencing the source it was generated from.",
"correct-answer-hint": "Give a short but helpful hint to the right answer.",
}}
"""

QA_PROMPT = PromptTemplate(
    template=qa_template, input_variables=["system_message", "context", "question"]
)
