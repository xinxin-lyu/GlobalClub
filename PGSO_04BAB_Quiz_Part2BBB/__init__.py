import copy as cp

import numpy as np
from otree.api import *


author = 'Xinxin Lyu'
doc = """
A quiz app for public good with a second option experiment.
"""


class Constants(BaseConstants):
    name_in_url = 'PGSO_04BAB_Quiz_Part2BBB'
    players_per_group = None
    num_rounds = 1



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    quizHistory1 = models.StringField()
    quizHistory2 = models.StringField()
    quizHistory3 = models.StringField()
    quizHistory4 = models.StringField()
    quizHistory5 = models.StringField()
    quizHistory6 = models.StringField()
    quizHistory7 = models.StringField()


# FUNCTIONS
# PAGES


            
class beginQuiz(Page):
    pass



class Question1(Page):
    form_model = 'player'
    form_fields = ['quizHistory1']


class Question2(Page):
    form_model = 'player'
    form_fields = ['quizHistory2']

class Question3(Page):
    form_model = 'player'
    form_fields = ['quizHistory3']

class Question4(Page):
    form_model = 'player'
    form_fields = ['quizHistory4']

class Question5(Page):
    form_model = 'player'
    form_fields = ['quizHistory5']
    
class Question6(Page):
    form_model = 'player'
    form_fields = ['quizHistory6']

class Question7(Page):
    form_model = 'player'
    form_fields = ['quizHistory7']


page_sequence = [
    beginQuiz,
    Question1,
    Question2,
    Question3,
    Question4,
    Question5,
    Question6,
    Question7,
]
