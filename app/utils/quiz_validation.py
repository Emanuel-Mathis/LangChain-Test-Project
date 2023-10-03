class QuizTypeValidation:
    '''
    A class containing functions to validate input from post request and return success/error status message
    '''

    def __init__(self, quiz):
        self.quiz = quiz

    def validate_request(self):
        response = (200, 'Success')
        if (not self.quiz.input):
            response = (400, 'No input submitted!')
            return response

        if (len(self.quiz.input) < 10):
            response = (400, 'Input must be more than 10 characters')
            return response

        if (self.quiz.inputType.upper() != 'TEXT' and self.quiz.inputType.upper() != 'FIREBASEURL'):
            response = (400, 'Only Text or FirebaseURL as input type supported!')
            return response

        if (self.quiz.quizType.upper() != 'MCQ'):
            response = (422, 'Only MCQ supported!')
            return response

        return response