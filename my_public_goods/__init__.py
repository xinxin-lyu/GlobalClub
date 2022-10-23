
from otree.api import *
import random
import numpy as np

doc = '''Based on Otree Studio public good. 
        This program is designed to implement a local public good vs a global club good
        Blcok random termination attributes to Jieqiong Jin, procedure follows Frechette&Yuksel(2017)'''
        
def cumsum(lst):
    total = 0
    new = []
    for ele in lst:
        total += ele
        new.append(total)
    return new


def numblock(lst, a):
    block = []
    for ele in lst:
        if ele % a == 0:
            block.append(int(ele / a)*a)
        else:
            block.append(int(ele // a + 1)*a)
    return block


def find_pay_rounds(sg_lst, sg_start):
    rounds = []
    for m in range(len(sg_lst)):
        pay_periods = [a + 1 for a in list(range(sg_lst[m]))]
        pay_rounds = [b + sg_start[m] for b in pay_periods]
        rounds.extend(pay_rounds)
    return rounds

def group_size():
    return 
    
class C(BaseConstants):
    NAME_IN_URL = 'my_public_goods'
    PLAYERS_PER_GROUP =  8
    # MULTIPLIER = 2.4
    # block_dierolls_template = 'block_random_termination/block_dierolls.html'
    DELTA = 0.75  # discount factor equals to 0.75
    BLOCK_SIZE = int(1 / (1 - DELTA))
    # print(BLOCK_SIZE)
    # first supergame lasts 2 rounds, second supergame lasts 3 rounds, etc...
    # These are the payoff relevants rounds
    COUNT_ROUNDS_PER_SG = [2, 3, 4, 5]
    # number of supergames to be played
    NUM_SG = len(COUNT_ROUNDS_PER_SG)
    # Get what the round each supergame ends
    # SG_ENDS = cumsum(COUNT_ROUNDS_PER_SG)

    # find how many blocks are needed for each supergame
    # find out how many rounds players have to go through
    PLAYED_ROUNDS_PER_SG = numblock(COUNT_ROUNDS_PER_SG, BLOCK_SIZE)  
    SG_ENDS = cumsum(PLAYED_ROUNDS_PER_SG)
    # print('PLAYED_ROUND_END is', SG_ENDS)
    PLAYED_ROUND_STARTS = [0] + SG_ENDS[:-1]
    # print('PLAY_STARTS is', PLAYED_ROUND_STARTS)
    PAY_ROUNDS = find_pay_rounds(COUNT_ROUNDS_PER_SG, PLAYED_ROUND_STARTS)
    # print('PAY_ROUNDS are', PAY_ROUNDS)
    PAY_ROUNDS_ENDS = [sum(x) for x in zip(COUNT_ROUNDS_PER_SG, PLAYED_ROUND_STARTS)]
    # print('PAY_ROUND_ENDS are', PAY_ROUNDS_ENDS)
    NUM_ROUNDS = sum(PLAYED_ROUNDS_PER_SG)

class Subsession(BaseSubsession):
    # current # of supergame
    sg = models.IntegerField()
    # the period in current supergame
    period = models.IntegerField()
    # whether a round is the last period of a supergame
    is_sg_last_period = models.BooleanField()
    # block = models.IntegerField()
    bk = models.IntegerField()
    # whether a round is the last period of a block
    is_bk_last_period = models.BooleanField()
    is_pay_relevant = models.BooleanField()
    dieroll = models.IntegerField(min=1, max=100)
    
def creating_session(subsession: Subsession):
    local_size = subsession.session.config['localPG_size']
    community_num = subsession.session.config['K']
    total_sub = subsession.session.num_participants
    shuffle_group = int(total_sub/local_size) # total number of local communities
    group_n = int(shuffle_group/ community_num)
    
    if subsession.round_number == 1:
        sg = 1
        period = 1
        bk = 1
        for ss in subsession.in_rounds(1, C.NUM_ROUNDS):# loop over all sss
            ss_round = ss.round_number
            ss.sg = sg
            ss.period = period
            ss.bk = period
            if (ss_round==1) or (ss_round-1 in C.SG_ENDS):
                shuffle_list = np.arange(1,int(shuffle_group)+1) # This is when the endowment is assigned randomly 
                #When a round is the first round or right after a supergame's end, reshuffle
                np.random.shuffle(shuffle_list)
                shuffle_list = shuffle_list.reshape(group_n, community_num).tolist()
                print(shuffle_list)
                matrix = []
                for row in shuffle_list:
                    rr = [] 
                    for sub in row: # this is the first member
                        for j in range(local_size):
                            rr.append(sub + shuffle_group*j) # This is when the endowment is assigned randomly 
                    matrix.append(rr)
                ss.set_group_matrix(matrix)
                print(matrix)
            else:
                ss.group_like_round(ss_round - 1)
            
            
            # Whether a round is the last round of a supergame
            # 'in' gives you a bool. for example: 5 in [1, 5, 6] # => True
            is_sg_last_period = ss_round in C.SG_ENDS
            ss.is_sg_last_period = is_sg_last_period
            if is_sg_last_period:
                sg += 1
                period = 1
            else:
                period += 1
            # whether a round is the last round of a block
            if ss_round % C.BLOCK_SIZE == 0:
                is_bk_last_period = 1
            else:
                is_bk_last_period = 0
                
            ss.is_bk_last_period = is_bk_last_period
            if is_bk_last_period:
                bk += 1
                # if is_sg_last_period:
                #     bk = 1
            # whether a round is pay relevant
            is_pay_relevant = ss_round in C.PAY_ROUNDS
            ss.is_pay_relevant = is_pay_relevant

            continuation_chance = int(round(C.DELTA * 100))
            # dieroll_continue = random.randint(1, continuation_chance)
            # dieroll_end = random.randint(continuation_chance + 1, 100)
            is_pay_round_end = ss_round in C.PAY_ROUNDS_ENDS
            if ss.is_pay_relevant and not is_pay_round_end:
                ss.dieroll = random.randint(1, continuation_chance)
            else:

                ss.dieroll = random.randint(continuation_chance + 1, 100)

class Group(BaseGroup):
    matchNumber = models.IntegerField(initial=0)
    roundNumber = models.IntegerField(initial = 0)
    
    # For the local PG
    total_contribution_local = models.CurrencyField(initial=0)
    individual_share_local = models.CurrencyField(initial=0)    

    
    # For the global PG
    global_formed = models.IntegerField(initial=0, min=0, max=1)
    total_contribution_global = models.CurrencyField(initial=0)
    individual_share_global = models.CurrencyField(initial=0) 
   
def get_role(group: Group):
     players = group.get_players()
     homo_endowment = group.session.config['homo_endowment']
     local_size = group.session.config['localPG_size']
     community_num = group.session.config['K']
     total_sub = group.session.num_participants

     shuffle_group = int(total_sub/local_size) # total number of local communities
     # When the endowment is randomly assigned, let the first two be the rich
     if homo_endowment==1:
        for p in players:
            p.endowment = 20
            p.local_community = p.id_in_subsession % shuffle_group # again, only true for the random grouping
     else :
        for p in players:
            p.local_community = p.id_in_subsession % shuffle_group # again, only true for the random grouping
            if p.id_in_group <= int(local_size/2):
                p.endowment=30
            else :
                p.endowment=10
    
def set_payoffs(group: Group):
    players = group.get_players()
    multiplier = group.session.config['multiplier']
    local_size = group.session.config['localPG_size']
    community_num = group.session.config['K']
    contribution_local = np.zeros(community_num)
    contribution_global = 0
    for p in players:
        # local 
        contribution_local[p.local_community] += p.contribution_local
        contribution_global += p.contribution_global
        
        
    # local needs to be specified because it's supposed to be half of the group size 
    contributions = [p.contribution_local for p in players]
    group.total_contribution_local = sum(contributions)
    group.individual_share_local = group.total_contribution_local *  multiplier/ local_size
    # note: for mg=ml, just use the players per local PG group
    # for the congestion case, can use the number of players in each club 
    contributions = [p.contribution_global for p in players]
    group.total_contribution_global = sum(contributions)
    group.individual_share_global = group.total_contribution_global * multiplier / local_size
    fixed_cost = group.session.config['FC']
    for p in players:
        p.payoff = p.endowment - p.contribution_local + group.individual_share_local +  p.join_club* (- p.contribution_global - fixed_cost + group.individual_share_global)

Group.set_payoffs = set_payoffs

class Player(BasePlayer):
    endowment = models.CurrencyField(initial=0)  
    join_club =  models.IntegerField(initial=0)
    local_community = models.IntegerField(initial=0) # indicate the local community number
    contribution_local = models.CurrencyField(initial=0, label='What is your contribution to local PG?', min=0)
    contribution_global = models.CurrencyField(initial=0, label='What is your contribution to global CL?', min=0)

# def my_method(player: Player):
    # group = player.group
    # group = group
    # players = group.get_players()
    # contributions = [ p.contribution for p in players]
    # group.total_contribution = sum(contributions)
    # group.individual_share = group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    # for p in players:
        # p.payoff = p.endowment - p.contribution + group.individual_share
# Player.my_method = my_method
    
def get_block_dierolls(player: Player):
    block_first_round = player.round_number - C.BLOCK_SIZE + 1
    block = player.in_rounds(block_first_round, player.round_number)
    block_history = []
    for b in block:
        block_round = dict(round_number=b.subsession.period, dieroll=b.subsession.dieroll)
        block_history.append(block_round)
    return block_history

# Page section
class SuperGameWaitPage(WaitPage):
    after_all_players_arrive = get_role
    body_text = 'Waiting for other players to start the supergame'

class NewSupergame(Page):
    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.period == 1
    
class JoinClub(Page):
    form_model = 'player'
    form_fields = ['join_club']
    

    
    def vars_for_template(player: Player):
        return dict(local_size = player.session.config['localPG_size'],
                       multiplier = player.session.config['multiplier'])


                   
class Contribution(Page):
    form_model = 'player'
    form_fields = []

    def get_form_fields(player: Player):
        if player.join_club == 1  : 
            return ['contribution_local', 'contribution_global']
        else:
            return ['contribution_local']

    
    def vars_for_template(player: Player):
        return dict(local_size = player.session.config['localPG_size'],
                       multiplier = player.session.config['multiplier'])
    
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    body_text = 'Waiting for other players to make their contributions'
class Results(Page):
    form_model = 'player'
    

class BlockEnd(Page):
    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.is_bk_last_period == 1
        
    def vars_for_template(player: Player):
        continuation_chance = int(round(C.DELTA * 100))
        # TODO: pull out a history of dierolls in this block gettattr()?
        # write a founction get block die rolls
        # player.subsession.dieroll
        # previous_rounds_in_block=
        sg = player.subsession.sg
        player_in_end_round=player.in_round(C.PAY_ROUNDS_ENDS[sg-1])
        end_period=player_in_end_round.subsession.period

        return dict(continuation_chance=continuation_chance,
                    die_threshold_plus_one=continuation_chance + 1,
                    block_history=get_block_dierolls(player),
                    end_period=end_period
                    )
page_sequence = [SuperGameWaitPage, NewSupergame, JoinClub, Contribution, ResultsWaitPage, Results, BlockEnd  ]