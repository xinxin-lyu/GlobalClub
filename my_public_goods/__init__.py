
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
    PLAYERS_PER_GROUP =  None
    # MULTIPLIER = 2.4
    block_dierolls_template = 'block_random_termination/block_dierolls.html'
    DELTA = 0.75  # discount factor equals to 0.75
    BLOCK_SIZE = int(1 / (1 - DELTA))
    # print(BLOCK_SIZE)
    # first supergame lasts 2 rounds, second supergame lasts 3 rounds, etc...
    # These are the payoff relevants rounds; 
    # Note: for my current experiment design, there are only 3 repeated games/matches (ABA or BAA)
    COUNT_ROUNDS_PER_SG = [5, 7, 6]
    JOIN_CLUB_SG = [1] # super games where a global club is offered 
    # number of supergames to be played
    NUM_SG = len(COUNT_ROUNDS_PER_SG)
    # Get what the round each supergame ends
    # SG_ENDS = cumsum(COUNT_ROUNDS_PER_SG)

    # find how many blocks are needed for each supergame
    # find out how many rounds players have to go through
    PLAYED_ROUNDS_PER_SG = numblock(COUNT_ROUNDS_PER_SG, BLOCK_SIZE)  
    SG_ENDS = cumsum(PLAYED_ROUNDS_PER_SG)
    print('PLAYED_ROUND_END is', SG_ENDS)
    PLAYED_ROUND_STARTS = [0] + SG_ENDS[:-1]
    print('PLAY_STARTS is', PLAYED_ROUND_STARTS)
    PAY_ROUNDS = find_pay_rounds(COUNT_ROUNDS_PER_SG, PLAYED_ROUND_STARTS)
    print('PAY_ROUNDS are', PAY_ROUNDS)
    PAY_ROUNDS_ENDS = [sum(x) for x in zip(COUNT_ROUNDS_PER_SG, PLAYED_ROUND_STARTS)]
    print('PAY_ROUND_ENDS are', PAY_ROUNDS_ENDS)
    NUM_ROUNDS = sum(PLAYED_ROUNDS_PER_SG)

class Subsession(BaseSubsession):
    # current # of supergame
    sg = models.IntegerField()
    # the period in current supergame
    period = models.IntegerField()
    # whether a round is the last period of a supergame
    is_sg_last_period = models.BooleanField()
    is_sg_first_period = models.BooleanField()
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
            # if (ss_round==1) or (ss_round-1 in C.SG_ENDS):
            if ss_round==1 :
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
     # Number inflate to avoid rounding issues
     if homo_endowment==1:
        for p in players:
            p.endowment = 200
            p.local_community = p.id_in_subsession % shuffle_group # again, only true for the random grouping
            p.id_in_local =  (p.id_in_subsession-1) // shuffle_group 
     else :
        for p in players:
            p.local_community = p.id_in_subsession % shuffle_group # again, only true for the random grouping
            p.id_in_local =  (p.id_in_subsession-1)// shuffle_group 
            if p.id_in_group <= int(local_size/2):
                p.endowment=300
            else :
                p.endowment=100
                
def check_club_formed(group: Group):
    players = group.get_players()
    join_club = [p.join_club for p in players]
    join_number = sum(join_club)
    if join_number <2 :
        for p in players:
            p.join_club = 0
    else :
        group.global_formed = 1
        for p in players:
            if p.join_club:
                p.endowment -= p.session.config['FC']
            
def set_payoffs(group: Group):
    players = group.get_players()
    multiplier = group.session.config['multiplier']
    local_size = group.session.config['localPG_size']
    community_num = group.session.config['K']
    contribution_local = np.zeros(community_num)
    contribution_global = 0
    for p in players:
        # local needs to be specified because it's supposed to be half of the group size  
        # individual contribution is recorded on the 0-20 base
        contribution_local[p.local_community] += p.contribution_local * 10
        contribution_global += p.contribution_global * 10
    individual_share_local = contribution_local *  multiplier/ local_size
    group.total_contribution_global = contribution_global
    group.individual_share_global = group.total_contribution_global * multiplier / local_size
    # note: for mg=ml, just use the players per local PG group
    # for the congestion case, can use the number of players in each club 
    fixed_cost = group.session.config['FC']
    # print(fixed_cost)
    for p in players:
        p.total_contribution_local = contribution_local[p.local_community]
        p.individual_share_local = individual_share_local[p.local_community]
        # p.payoff = p.endowment - p.contribution_local + p.individual_share_local +  p.join_club* (- p.contribution_global - fixed_cost + group.individual_share_global)
        p.payoff = p.endowment - p.contribution_local*10 + p.individual_share_local +  p.join_club* (- p.contribution_global*10 + group.individual_share_global)
Group.set_payoffs = set_payoffs

class Player(BasePlayer):
    endowment = models.CurrencyField(initial=0)  
    join_club =  models.IntegerField(initial=0)
    local_community = models.IntegerField(initial=0) # indicate the local community number
    id_in_local = models.IntegerField(initial=-1) # indicate the individual id in local community
    contribution_local = models.CurrencyField(initial=0, label='What is your contribution to local PG?', min=0)
    contribution_global = models.CurrencyField(initial=0, label='What is your contribution to global CL?', min=0)
    # For the local PG
    total_contribution_local = models.CurrencyField(initial=0)
    individual_share_local = models.CurrencyField(initial=0)    

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
def js_vars(player):

    
    end_toshow = player.endowment/10
    endowment_list_l = [end_toshow]
    endowment_list_g = [end_toshow]
    
    current_sp = player.subsession.sg -1 
    LocalSize = int(player.session.config['localPG_size'])
    GlobalSize = int(player.session.config['localPG_size'] * player.session.config['K'],)
    
    others = player.get_others_in_group()
    for p in others:
        end_toshow = p.endowment/10
        endowment_list_g.append(end_toshow)
        if p.local_community == player.local_community:
            endowment_list_l.append(end_toshow)
        
    d = dict( matchNumber = player.subsession.sg,
        Round = player.subsession.period,
        
        E_l = endowment_list_l,
        E_g = endowment_list_g,
        LocalSize = LocalSize,
        GlobalSize = GlobalSize,
        )
       
    #Everthing here is about history: 
    if player.subsession.period !=1 :
        joinedLastRound = player.in_round(player.round_number - 1).join_club
        ClubFormedLastRound = player.in_round(player.round_number - 1).group.global_formed
        all_previous = player.in_rounds(C.PLAYED_ROUND_STARTS[current_sp]+1, player.round_number-1)
        contribution_l = [int(x.total_contribution_local/10) for x in all_previous ]
        contribution_g = [int(x.group.total_contribution_global/10) for x in all_previous ]
        contribution_l.reverse()
        contribution_g.reverse()
        
        # Individual contribution is stored as proper points
        my_cont_l = [int(x.contribution_local) for x in all_previous ]
        my_cont_g = [ ]
        for x in all_previous: 
            if x.join_club == 1:
                my_cont_g.append(int(x.contribution_global))
            else :
                my_cont_g.append(np.nan)
        my_cont_l.reverse()
        my_cont_g.reverse()
        others_cont_l_lastOnly = [] 
        others_cont_l = []
        others_cont_g_lastOnly = []
        others_cont_g = []
        others_join_g = []
        others_join_g_lastOnly = []
        
        others = player.get_others_in_group()
        for p in others:
            p_previous = p.in_rounds( C.PLAYED_ROUND_STARTS[current_sp]+1, player.round_number-1,)
            # print(p_previous)
            
            o_all_g = []
            for x in p_previous:
                if x.join_club==1 :
                    o_all_g.append(int(x.contribution_global))
                else :
                    o_all_g.append(np.nan)
                    
            o_join_g = [x.join_club for x in p_previous]
            o_all_g.reverse()
            o_join_g.reverse()
            others_cont_g.append(o_all_g)
            others_cont_g_lastOnly.append(o_all_g[0])
            others_join_g.append(o_join_g)
            others_join_g_lastOnly.append(o_join_g[0])
            
            if p.local_community == player.local_community:
                o_all_l = [int(x.contribution_local) for x in p_previous]
                o_all_l.reverse()
                others_cont_l.append(o_all_l)
                others_cont_l_lastOnly.append(o_all_l[0])
        # To find the max and min value's position 
        # print("contr g")
        # print(others_cont_g_lastOnly)
        # print(others_join_g_lastOnly)
        # print(np.multiply(others_cont_g_lastOnly, others_join_g_lastOnly))
        all_list = range(LocalSize-1)
        max_local = np.argwhere(others_cont_l_lastOnly == np.nanmax(others_cont_l_lastOnly)).flatten().tolist()
        min_local = np.argwhere(others_cont_l_lastOnly == np.nanmin(others_cont_l_lastOnly)).flatten().tolist()
        rest_local = [x for x in all_list if ( x not in max_local and x not in min_local) ]
        
        
        all_list = range(GlobalSize-1)
        max_global = np.argwhere(others_cont_g_lastOnly == np.nanmax(others_cont_g_lastOnly)).flatten().tolist()
        min_global = np.argwhere(others_cont_g_lastOnly == np.nanmin(others_cont_g_lastOnly)).flatten().tolist()
        rest_global = [x for x in all_list if ( x not in max_global and x not in min_global) ]
        
        # round_num = range(1, player.round_number-2)
        d = dict(d, 
                joinedLastRound = joinedLastRound, 
                C_t_l = contribution_l,
                C_t_g = contribution_g,
                my_cont_l = my_cont_l,
                my_cont_g = my_cont_g,
                others_cont_l = others_cont_l,
                others_cont_g = others_cont_g,
                others_join_g = others_join_g,
                max_local = max_local,
                min_local = min_local,
                rest_local = rest_local,
                max_global = max_global,
                min_global = min_global,
                rest_global = rest_global,
                ClubFormedLastRound = ClubFormedLastRound,
                
        )
        
        
        
        
    return dict(
        d,
        )




def vars_for_template(player: Player):
    if player.subsession.period == 1 :
        earning = 0
        joined = 0
        formed_g = 0 
    else :
        pre_player = player.in_round(player.round_number - 1)
        earning = pre_player.payoff / 10
        joined = pre_player.join_club
        formed_g = pre_player.group.global_formed
    return dict(local_size = player.session.config['localPG_size'],
                local_multiplier = player.session.config['multiplier'] / player.session.config['localPG_size'],
                global_multiplier =player.session.config['multiplier'] / player.session.config['localPG_size'],
                FC = int(player.session.config['FC'] / 10),
                endow = int(player.endowment/10),
                
                earning = earning, 
                joined = joined,
                formed_g = formed_g,
               multiplier = player.session.config['multiplier'],
               join_club = player.join_club==1
                )


class SuperGameWaitPage(WaitPage):
    after_all_players_arrive = get_role
    body_text = 'Waiting for other players to join the group'

class NewSupergame(Page):
    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.period == 1
    
class JoinClub(Page):
    form_model = 'player'
    form_fields = ['join_club']
    
    js_vars = js_vars
    vars_for_template = vars_for_template

class ClubWaitPage(WaitPage):
    after_all_players_arrive = check_club_formed
    body_text = 'Waiting for other players to choose to join the club or not'


                   
class Contribution(Page):
    form_model = 'player'
    form_fields = []

    def get_form_fields(player: Player):
        if player.join_club == 1  : 
            return ['contribution_local', 'contribution_global']
        else:
            return ['contribution_local']
    
    def js_vars(player: Player):
        d = js_vars(player)
        others = player.get_others_in_group()
        OtherJoin = [x.join_club for x in others]
        return dict(d, 
                MeJoin = player.join_club,
                OtherJoin = OtherJoin,
                Formed = player.group.global_formed,
                
                )
    vars_for_template = vars_for_template

    
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
page_sequence = [SuperGameWaitPage, NewSupergame, JoinClub, ClubWaitPage, Contribution, ResultsWaitPage, Results, BlockEnd  ]