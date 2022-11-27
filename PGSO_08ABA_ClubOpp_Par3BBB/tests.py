from otree.api import Currency as c, currency_range
from . import *
from otree.api import Bot
import random



class PlayerBot(Bot):

    def play_round(self):
        
        
        if self.round_number ==1: 
            yield P01_beginExperiment
        
        joinClub = random.choice([0,1])
        yield P03_JoinClub, dict(join_club = joinClub)
        
        # yield P04_ClubWaitPage
        
        cont_l = random.choice([0,self.player.endowment])
        cont_g = 0
        # yield P05_Contribution, dict(contribution_local = ), 
                                          # contribution_global = random.choice([0,self.player.endowment-contribution_local])   )
        if self.player.join_club == 1  : 
            yield P05_Contribution, dict(contribution_local = cont_l,  contribution_global = cont_g  )
        else : 
            yield P05_Contribution, dict(contribution_local = cont_l)
            
        # yield P06_ResultsWaitPage
        
        if self.subsession.is_bk_last_period == 1:
            yield P07_BlockEnd
