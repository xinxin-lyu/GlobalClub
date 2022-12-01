from otree.api import Currency as c, currency_range
from . import *
from otree.api import Bot



class PlayerBot(Bot):

    def play_round(self):
        yield Questionnaire, dict(ageSelect='Under 20', genderSelect='Male', majorSelect='Economics or Management', hsSelect='In US')
