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