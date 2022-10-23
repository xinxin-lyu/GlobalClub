from os import environ

SESSION_CONFIGS = [
    dict(
        name='my_public_goods',
        app_sequence=['my_public_goods'],
        num_demo_participants=8,
        
        multiplier = 2.4,
        localPG_size = 4,
        K = 2 ,
        FC = 2, 
        homo_endowment = 1,
        # m_l = 0.6,
        # m_g = 0.6,
        
        doc="""
            
            <br> <b>'localPG_size' </b> how many people in the local PG </br>
            <br> <b>'K' </b> how many communities connect to form the club good </br>
            <br> <b>'FC' </b> fixed cost to join the club good </br>
            <br> <b>'multiplier' </b> total multiplier = localPG_size * m_l = m_g (for now)  </br>
            <br> <b>'m_l' </b> MPCR for local PG </br>
            <br> <b>'m_g' </b> MPCR for global Club </br>
            <br> <b>'homo_endowment' </b> Whether the local community has homogenous endowments </br>
            """
    ),
    
    dict(
        name='block_random_termination',
        app_sequence=['block_random_termination'],
        num_demo_participants=2,),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2464126661992'
