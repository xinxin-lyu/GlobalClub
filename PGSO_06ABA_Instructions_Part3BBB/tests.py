from otree.api import Currency as c, currency_range
from . import *
from otree.api import Bot



class PlayerBot(Bot):

    def play_round(self):
       yield  P01_BeginPart3
       yield  P02_MatchWork, dict( testingHistory = ',3,5,8,2,7,7,10,-1,2,1,1,9,9,4' )
       yield  P03_RoundOverview
       yield  P04_RoundOverview2
