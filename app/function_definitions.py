functions = [
    {
        "name": "generate_question_answer_pairs",
        "description": "Generate a question-answer pairs only based on the provided inputText",
        "parameters": {
            "type": "object",
            "properties": {
                "inputText": {
                    "type": "string",
                    "description": "The text from which question-answer pairs will be generated",
                },
            },
            "required": ["inputText"],
        },
    },
        {
        "name": "generate_multiple_choice_answers",
        "description": "Given question & answers, generate ",
        "parameters": {
            "type": "object",
            "properties": {
                "inputText": {
                    "type": "string",
                    "description": "The text from which question-answer pairs will be generated",
                },
            },
            "required": ["inputText"],
        },
    },
    {
        "name": "get_pizza_info",
        "description": "Get name and price of a pizza of the restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "pizza_name": {
                    "type": "string",
                    "description": "The name of the pizza, e.g. Salami",
                },
            },
            "required": ["pizza_name"],
        },
    },
    {
        "name": "create_order",
        "description": "Create an order for a specific pizza",
        "parameters": {
            "type": "object",
            "properties": {
                "pizza_name": {
                    "type": "string",
                    "description": "The name of the pizza to order, e.g. Margherita",
                },
            },
            "required": ["pizza_name"],
        },
    },
    {
        "name": "create_review",
        "description": "Create a review for the restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "review_text": {
                    "type": "string",
                    "description": "The text of the review, e.g. Great pizza!",
                },
            },
            "required": ["review_text"],
        },
    },
    {
        "name": "ask_vector_db",
        "description": "Ask any question related to our restaurant. This can include queries about our opening hours, menu items, ingredients used, special dietary accommodations, ongoing promotions, or health and safety measures in place.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to ask, e.g. 'What is the most popular pizza topping?'",
                },
            },
            "required": ["question"],
        },
    },
]
