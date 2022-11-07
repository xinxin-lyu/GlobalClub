
from otree.api import *
import random
import numpy as np
from json import dumps as json_dumps, loads as json_loads

doc = '''This is for pilot, with club opporutnity
    Block random termination still;
    3 matches H/L/M or L/H/M;
    Use a group variable to store the fixed cost for each sp;
    Group rematching is: 
    S1: G1 + G2 (H) ; G3 + G4 (L) 
    S2: G1+G3 (L) ; G2+G4 (H)
    S3: G1 + G2 (L); G3 + G4(H); 
    
    '''
        
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
    NAME_IN_URL = 'PGSO_08_WithClubOppVariedCost_Part3'
    PLAYERS_PER_GROUP =  None
    # MULTIPLIER = 2.4
    block_dierolls_template = 'block_random_termination/block_dierolls.html'
    DELTA = 0.9  # discount factor equals to 0.75
    BLOCK_SIZE = int(1 / (1 - DELTA))
    # print(BLOCK_SIZE)
    # first supergame lasts 2 rounds, second supergame lasts 3 rounds, etc...
    # These are the payoff relevants rounds; 
    # Note: for my current experiment design, there are only 3 repeated games/matches (ABA or BAA)
    # Note: for pilot, only 3 matches, but with different fixed cost
    COUNT_ROUNDS_PER_SG = [8, 12, 7]
    JOIN_CLUB_SG = [1] # super games where a global club is offered; not in use for now
    GroupMatch = [[[1,2],[3,4]], [[1,3],[2,4]], [[1,2],[3,4]]]
    FixedCost = [ [80,20], [20,80],  [20,80]]
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
    dieroll = models.IntegerField(min=1, max=10)
    
def creating_session(subsession: Subsession):
    local_size = subsession.session.config['localPG_size']
    community_num = subsession.session.config['K']
    total_sub = subsession.session.num_participants
    shuffle_group = int(total_sub/local_size) # total number of local communities
    group_n = int(shuffle_group/ community_num)
    # for p in subsession.get_players():
        # p.participant.vars['payoffs'] = 0
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
            # if ss_round==1 :
                # shuffle_list = np.arange(1,int(shuffle_group)+1) # This is when the endowment is assigned randomly 
                # # When a round is the first round or right after a supergame's end, reshuffle
                # np.random.shuffle(shuffle_list)
                # shuffle_list = shuffle_list.reshape(group_n, community_num).tolist()
                print('super game is'+str(sg))
                shuffle_list = C.GroupMatch[sg-1]
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

            continuation_chance = int(round(C.DELTA * 10))
            # dieroll_continue = random.randint(1, continuation_chance)
            # dieroll_end = random.randint(continuation_chance + 1, 100)
            is_pay_round_end = ss_round in C.PAY_ROUNDS_ENDS
            if ss.is_pay_relevant and not is_pay_round_end:
                ss.dieroll = random.randint(1, continuation_chance)
            else:

                ss.dieroll = random.randint(continuation_chance + 1, 10)
    
    
class Group(BaseGroup):
    matchNumber = models.IntegerField(initial=0)
    roundNumber = models.IntegerField(initial = 0)
    # For the global PG
    global_formed = models.IntegerField(initial=0, min=0, max=1)
    total_contribution_global = models.CurrencyField(initial=0)
    individual_share_global = models.CurrencyField(initial=0) 
    # json fields (for wait_page_from_scratch)
    wait_for_ids1 = models.LongStringField(initial='[]')
    arrived_ids1 = models.LongStringField(initial='[]')
    wait_for_ids2 = models.LongStringField(initial='[]')
    arrived_ids2 = models.LongStringField(initial='[]')
    
    did_aapa1 = models.BooleanField(initial=False)
    did_aapa2 = models.BooleanField(initial=False)
    
    FC = models.IntegerField(initial=0)
    
def get_role(group: Group):
    # Pilot only: Changing fixed cost
     group.FC = C.FixedCost[group.subsession.sg-1][group.id_in_subsession-1]
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
            if p.id_in_local < int(local_size/2):
                p.endowment=300
            else :
                p.endowment=100
    

                
def check_club_formed(group: Group):
    players = group.get_players()
    join_club = [p.join_club for p in players]
    join_number = sum(join_club)
    if join_number <1 :
        for p in players:
            p.join_club = 0
    else :
        group.global_formed = 1
        for p in players:
            if p.join_club:
                p.endowment -= p.group.FC
            
def set_payoffs(group: Group):
    players = group.get_players()
    multiplier = group.session.config['multiplier']
    local_size = group.session.config['localPG_size']
    community_num = group.session.config['K']
    contribution_local = {}
    contribution_global = 0
    for p in players:
        # local needs to be specified because it's supposed to be half of the group size  
        # individual contribution is recorded on the 0-20 base
        if p.local_community not in contribution_local.keys() :
            contribution_local[p.local_community] = 0
            
        contribution_local[p.local_community] += p.contribution_local * 10
        contribution_global += p.contribution_global * 10
    group.total_contribution_global = contribution_global
    group.individual_share_global = group.total_contribution_global * multiplier / local_size
    # note: for mg=ml, just use the players per local PG group
    # for the congestion case, can use the number of players in each club 
    fixed_cost = group.FC
    payRelevant = group.subsession.is_pay_relevant
    for p in players:
        p.total_contribution_local = contribution_local[p.local_community]
        p.individual_share_local = p.total_contribution_local *  multiplier/ local_size
        # p.payoff = p.endowment - p.contribution_local + p.individual_share_local +  p.join_club* (- p.contribution_global - fixed_cost + group.individual_share_global)
        p.payoff = p.endowment - p.contribution_local*10 + p.individual_share_local +  p.join_club* (- p.contribution_global*10 + group.individual_share_global)
        if 'pay_matters' not in p.participant.vars.keys() :
            p.participant.vars['pay_matters'] =0
        
        if payRelevant :
            p.participant.vars['pay_matters'] += p.payoff
Group.set_payoffs = set_payoffs

def unarrived_players(group: Group):
    return set(json_loads(group.wait_for_ids)) - set(json_loads(group.arrived_ids))
    
def ClearWaitPageHistory(group: Group):
    group.wait_for_ids = '[]'
    group.arrived_ids = '[]'
    
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
    
    # Button record
    button_j = models.LongStringField(initial='[]',blank=True)
    button_j_w = models.LongStringField(initial='[]',blank=True)
    button_c = models.LongStringField(initial='[]',blank=True)
    button_c_w = models.LongStringField(initial='[]',blank=True)
    button_b = models.LongStringField(initial='[]',blank=True)
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
    current_sp = player.subsession.sg -1 
    
    # block_first_round = player.round_number - C.BLOCK_SIZE + 1
    block_first_round = C.PLAYED_ROUND_STARTS[current_sp] +1    # I want the full history
    print(block_first_round)
    block = player.in_rounds(block_first_round, player.round_number)
    block_history = []
    for b in block:
        if b.subsession.is_pay_relevant == 1 :
            block_round = dict(round_number=b.subsession.period, earning=int(b.payoff)/10, dieroll=b.subsession.dieroll)
            block_history.append(block_round)
        else :
            block_round = dict(round_number=b.subsession.period, earning=int(b.payoff)/10, dieroll='' )
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
        if p.local_community == player.local_community:
            endowment_list_l.append(end_toshow)
            endowment_list_g.append(end_toshow)
    for p in others:
        end_toshow = p.endowment/10
        if p.local_community != player.local_community:
            endowment_list_g.append(end_toshow)
            
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
            # First, loop over all others in the same local 
            if p.local_community == player.local_community:
                p_previous = p.in_rounds( C.PLAYED_ROUND_STARTS[current_sp]+1, player.round_number-1,)
                o_all_l = [int(x.contribution_local) for x in p_previous]
                o_all_l.reverse()
                others_cont_l.append(o_all_l)
                others_cont_l_lastOnly.append(o_all_l[0])

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
            
        for p in others:
            # Second, loop over all others not in the same local 
            if p.local_community != player.local_community:
                p_previous = p.in_rounds( C.PLAYED_ROUND_STARTS[current_sp]+1, player.round_number-1,)

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
        earning = int(pre_player.payoff) / 10
        joined = pre_player.join_club
        formed_g = pre_player.group.global_formed
    return dict(local_size = player.session.config['localPG_size'],
                local_multiplier = player.session.config['multiplier'] / player.session.config['localPG_size'],
                global_multiplier =player.session.config['multiplier'] / player.session.config['localPG_size'],
                FC = int(player.group.FC / 10),
                endow = int(player.endowment/10),
                
                earning = earning, 
                joined = joined,
                formed_g = formed_g,
               multiplier = player.session.config['multiplier'],
               join_club = player.join_club==1
                )

def unarrived_players1(group: Group):
    return set(json_loads(group.wait_for_ids1)) - set(json_loads(group.arrived_ids1))
    
def unarrived_players2(group: Group):
    return set(json_loads(group.wait_for_ids2)) - set(json_loads(group.arrived_ids2))
    

def wait_page_live_method1(player: Player, data):
    group = player.group

    arrived_ids_set = set(json_loads(group.arrived_ids1))
    arrived_ids_set.add(player.id_in_subsession)
    group.arrived_ids1 = json_dumps(list(arrived_ids_set))

    if not unarrived_players1(group):
        return {0: dict(finished=True)}
        
def wait_page_live_method2(player: Player, data):
    group = player.group

    arrived_ids_set = set(json_loads(group.arrived_ids2))
    arrived_ids_set.add(player.id_in_subsession)
    group.arrived_ids2 = json_dumps(list(arrived_ids_set))

    if not unarrived_players2(group):
        return {0: dict(finished=True)}

class ScratchWaitPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        # first time
        if not json_loads(group.wait_for_ids):
            wait_for_ids = [p.id_in_subsession for p in group.get_players()]
            group.wait_for_ids = json_dumps(wait_for_ids)
        return unarrived_players(group)

    @staticmethod
    def live_method(player: Player, data):
        if data.get('type') == 'wait_page':
            return wait_page_live_method(player, data)

    @staticmethod
    def error_message(player: Player, values):
        group = player.group
        if unarrived_players(group):
            return "Wait page not finished"


class P01_beginExperiment(Page):

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.round_number == 1
        
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'HOMO': player.session.config['homo_endowment'],
            'PointsPerDollar': int(1.0 / player.session.config['real_world_currency_per_point']),
            'ShowUpFee': int(player.session.config['participation_fee']),
            'CutoffRoll': int(player.session.config['CutoffRoll']),
            'PointsPerDollar': int(1.0 / player.session.config['real_world_currency_per_point']/10),

        }

class SuperGameWaitPage(WaitPage):
    after_all_players_arrive = get_role
    body_text = 'Waiting for other players to join the group'

    
class JoinClub(Page):
    form_model = 'player'
    form_fields = ['join_club', 'button_j']
    
    js_vars = js_vars
    vars_for_template = vars_for_template

class ClubWaitPage(Page):
    form_model = 'player'
    form_fields = ['button_j_w'] 
    
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        # first time
        if not json_loads(group.wait_for_ids1):
            wait_for_ids1 = [p.id_in_subsession for p in group.get_players()]
            group.wait_for_ids1 = json_dumps(wait_for_ids1)
        return unarrived_players1(group)

    @staticmethod
    def live_method(player: Player, data):
        if data.get('type') == 'wait_page':
            return wait_page_live_method1(player, data)

    @staticmethod
    def error_message(player: Player, values):
        group = player.group
        if unarrived_players1(group):
            return "Wait page not finished"
    
    js_vars = js_vars
    vars_for_template = vars_for_template

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if not group.did_aapa1: 
            
            check_club_formed(group)
                                       
            group.did_aapa1 = True


                   
class Contribution(Page):
    form_model = 'player'
    form_fields = []

    def get_form_fields(player: Player):
        if player.join_club == 1  : 
            return ['contribution_local', 'contribution_global', 'button_c']
        else:
            return ['contribution_local', 'button_c']
    
    def js_vars(player: Player):
        d = js_vars(player)
        others = player.get_others_in_group()
        OtherJoin= []
        for x in others:
            if x.local_community == player.local_community:
                OtherJoin.append(x.join_club)
        for x in others:
            if x.local_community != player.local_community:
                OtherJoin.append(x.join_club)    
        
        return dict(d, 
                MeJoin = player.join_club,
                OtherJoin = OtherJoin,
                Formed = player.group.global_formed,
                
                )
    vars_for_template = vars_for_template
    @staticmethod
    def error_message(player, values):
        # print(values)
        if player.join_club == 1  : 
            if int(values['contribution_local']) + int(values['contribution_global']) > int(player.endowment)/10:
                return 'Total allocation must be below your endowment.'
        else :
            if int(values['contribution_local']) > int(player.endowment)/10:
                return 'Total allocation must be below your endowment.'
                
                
class ResultsWaitPage(Page):
    form_model = 'player'
    form_fields = ['button_c_w'] 
    
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        # first time
        if not json_loads(group.wait_for_ids2):
            wait_for_ids2 = [p.id_in_subsession for p in group.get_players()]
            group.wait_for_ids2 = json_dumps(wait_for_ids2)
        return unarrived_players2(group)


    @staticmethod
    def live_method(player: Player, data):
        if data.get('type') == 'wait_page':
            return wait_page_live_method2(player, data)

    @staticmethod
    def error_message(player: Player, values):
        group = player.group
        if unarrived_players2(group):
            return "Wait page not finished"
    
    js_vars = js_vars
    vars_for_template = vars_for_template

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if not group.did_aapa2: 
            
            set_payoffs(group)
                                       
            group.did_aapa2 = True



    
class BlockEnd(Page):
    form_model = 'player'
    form_fields = ['button_b'] 

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.is_bk_last_period == 1
    
        # Note the only difference here is to return all rounds information !
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
            if p.local_community == player.local_community:
                endowment_list_l.append(end_toshow)
                endowment_list_g.append(end_toshow)
        for p in others:
            end_toshow = p.endowment/10
            if p.local_community != player.local_community:
                endowment_list_g.append(end_toshow)
                

       # All history
        joinedLastRound = player.in_round(player.round_number).join_club
        ClubFormedLastRound = player.in_round(player.round_number).group.global_formed
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
            # First, loop over all others in the same local 
            if p.local_community == player.local_community:
                p_previous = p.in_rounds( C.PLAYED_ROUND_STARTS[current_sp]+1, player.round_number)
                o_all_l = [int(x.contribution_local) for x in p_previous]
                o_all_l.reverse()
                others_cont_l.append(o_all_l)
                others_cont_l_lastOnly.append(o_all_l[0])

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
            
        for p in others:
            # Second, loop over all others not in the same local 
            if p.local_community != player.local_community:
                p_previous = p.in_rounds( C.PLAYED_ROUND_STARTS[current_sp]+1, player.round_number)

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
                

        all_list = range(LocalSize-1)
        max_local = np.argwhere(others_cont_l_lastOnly == np.nanmax(others_cont_l_lastOnly)).flatten().tolist()
        min_local = np.argwhere(others_cont_l_lastOnly == np.nanmin(others_cont_l_lastOnly)).flatten().tolist()
        rest_local = [x for x in all_list if ( x not in max_local and x not in min_local) ]
        
        
        all_list = range(GlobalSize-1)
        max_global = np.argwhere(others_cont_g_lastOnly == np.nanmax(others_cont_g_lastOnly)).flatten().tolist()
        min_global = np.argwhere(others_cont_g_lastOnly == np.nanmin(others_cont_g_lastOnly)).flatten().tolist()
        rest_global = [x for x in all_list if ( x not in max_global and x not in min_global) ]
            
         # After contribution page: 
        others = player.get_others_in_group()
        OtherJoin = [x.join_club for x in others]     
            
            
        return dict(matchNumber = player.subsession.sg,
                    Round = player.subsession.period,
            
                    E_l = endowment_list_l,
                    E_g = endowment_list_g,
                    LocalSize = LocalSize,
                    GlobalSize = GlobalSize,
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
                    MeJoin = player.join_club,
                    OtherJoin = OtherJoin,
                    Formed = player.group.global_formed,
                    
                    )
      
    def vars_for_template(player: Player):
        continuation_chance = int(round(C.DELTA * 100))
        # TODO: pull out a history of dierolls in this block gettattr()?
        # write a founction get block die rolls
        # player.subsession.dieroll
        # previous_rounds_in_block=
        d = vars_for_template(player) 
        sg = player.subsession.sg
        player_in_end_round=player.in_round(C.PAY_ROUNDS_ENDS[sg-1])
        end_period=player_in_end_round.subsession.period

        return dict(d,
            continuation_chance=continuation_chance,
                    die_threshold_plus_one=continuation_chance + 1,
                    block_history=get_block_dierolls(player),
                    end_period=end_period
                    )
page_sequence = [ P01_beginExperiment, SuperGameWaitPage, JoinClub, ClubWaitPage, Contribution, ResultsWaitPage, BlockEnd  ]