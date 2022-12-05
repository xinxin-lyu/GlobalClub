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
        
        yield P03_JoinClub, dict(join_club = random.choice([0,1]))
        
        # yield  Submission(P04_ClubWaitPage,check_html=False) 
        
        cont_l = random.choice(range(0,int(int(self.player.endowment)/10)+1))
        cont_g = random.choice(range(0,int(int(self.player.endowment)/10)-cont_l+1))
        if self.player.join_club == 1  : 
            yield P05_Contribution, dict(contribution_local = cont_l,  contribution_global = cont_g  )
        else : 
            yield P05_Contribution, dict(contribution_local = cont_l)
            
        # yield P06_ResultsWaitPage
        
        if self.subsession.is_bk_last_period == 1:
            yield P07_BlockEnd
