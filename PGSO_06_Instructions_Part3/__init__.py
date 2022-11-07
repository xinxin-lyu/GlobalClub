from otree.api import *
import numpy as np

author = 'Xinxin Lyu'
doc = """
"""


class Constants(BaseConstants):
    name_in_url = 'PGSO_06_Instructions_Part3'
    players_per_group = None
    num_rounds = 1

class Group(BaseGroup):
    pass


class Subsession(BaseSubsession):
    pass


class Player(BasePlayer):
    testingHistory = models.StringField()
    
    option1= models.IntegerField(widget=widgets.RadioSelect, choices=[1,2,3,4], blank=True)
    option2= models.IntegerField(widget=widgets.RadioSelect, choices=[1,2,3,4], blank=True)
    option3= models.IntegerField(widget=widgets.RadioSelect, choices=[1,2,3,4], blank=True)
    option4= models.IntegerField(widget=widgets.RadioSelect, choices=[1,2,3,4], blank=True)
    



# FUNCTIONS
# PAGES

class WaitForOthers(WaitPage):

    @staticmethod
    def vars_for_template(player: Player):
        title_text = ""
        body_text = "Please wait for other participants to finish Part 2."
        return {'title_text': title_text, "body_text": body_text}

        
class P01_BeginPart3(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if 'endowment' in player.participant.vars.keys():
            endow = player.participant.vars['endowment']
        else : 
            endow = -1
        return {
            'Matches': 1,
            'PointsPerDollar': int(1.0 / player.session.config['real_world_currency_per_point']/10),
            'ShowUpFee': int(player.session.config['participation_fee']),
            'CutoffRoll': int(player.session.config['CutoffRoll']),
            'myEndow': endow, 

        }
    @staticmethod
    def js_vars(player):
        return dict( 
        CutoffRoll = int(player.session.config['CutoffRoll']),
        )

    
class P02_MatchWork(Page):
    form_model = 'player'
    form_fields = ['testingHistory']

    @staticmethod
    def vars_for_template(player: Player):
        if 'endowment' in player.participant.vars.keys():
            endow = player.participant.vars['endowment']
        else : 
            endow = -1
        return {
            'Matches': 1,
            'PointsPerDollar': int(1.0 / player.session.config['real_world_currency_per_point']/10),
            'ShowUpFee': int(player.session.config['participation_fee']),
            'CutoffRoll': int(player.session.config['CutoffRoll']),
            'myEndow': endow,
        }
    @staticmethod
    def js_vars(player):
        return dict( 
        CutoffRoll = int(player.session.config['CutoffRoll']),
        )

    
        
class P03_RoundOverview(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'HOMO': player.session.config['homo_endowment'],
            'PointsPerDollar': int(1.0 / player.session.config['real_world_currency_per_point']/10),
            'ShowUpFee': int(player.session.config['participation_fee']),
            'CutoffRoll': int(player.session.config['CutoffRoll']),
        }
   
class P04_RoundOverview2(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'HOMO': player.session.config['homo_endowment'],
            'ShowUpFee': int(player.session.config['participation_fee']),
            'CutoffRoll': int(player.session.config['CutoffRoll']),
            'PointsPerDollar': int(1.0 / player.session.config['real_world_currency_per_point']/10),

        }
   


page_sequence = [
    WaitForOthers,
    P01_BeginPart3,
    P02_MatchWork,
    P03_RoundOverview,
    P04_RoundOverview2


]
