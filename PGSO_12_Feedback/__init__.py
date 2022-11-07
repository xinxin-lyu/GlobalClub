import numpy as np
from otree.api import *


author = 'Yaroslav Rosokha'
doc = """
Post-experimental Questionnaire.
"""


class Constants(BaseConstants):
    name_in_url = 'PGSO_12_Feedback'
    players_per_group = None
    num_rounds = 1


class Group(BaseGroup):
    pass


class Subsession(BaseSubsession):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
# PAGES
class ThankYou(Page):
    @staticmethod
    def vars_for_template(player: Player):
        x = player.participant.vars['pay_matters'] * player.session.config['real_world_currency_per_point']
        return {'earningsTotal': round(x, 2)}


page_sequence = [
    ThankYou,
]
