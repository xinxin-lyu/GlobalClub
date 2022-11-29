from otree.api import Currency as c, currency_range
from . import *
from otree.api import Bot
import random

# def call_live_method(method, **kwargs):
    # method(0, {'type': 'wait_page'})


class PlayerBot(Bot):

    def play_round(self):
        
        
        if self.round_number ==1: 
            yield P01_beginExperiment
        
        
        yield P02_Contribution, dict(contribution_local =  random.choice(range(0,int(int(self.player.endowment)/10)+1)) )
        # yield P03_ResultsWaitPage
        
        if self.subsession.is_bk_last_period == 1:
            yield P04_BlockEnd
