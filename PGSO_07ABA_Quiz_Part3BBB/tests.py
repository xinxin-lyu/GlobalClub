from otree.api import Currency as c, currency_range

from . import *
from otree.api import Bot



class PlayerBot(Bot):

    def play_round(self):
            
            
        yield beginQuiz
        yield Question1, dict(quizHistory1='something')
        yield Question2, dict(quizHistory2='something')
        yield Question3, dict(quizHistory3='something')
        yield Question4, dict(quizHistory4='something')
        yield Question5, dict(quizHistory5='something')