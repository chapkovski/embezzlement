from os import environ

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

SESSION_CONFIGS = [
    dict(
        name='baseline',
        display_name="Embezzlement game - baseline",
        num_demo_participants=2,
        app_sequence=['embez'],
        treatment='baseline'
    ),
    dict(
        name='negative',
        display_name="Embezzlement game - negative incentive",
        num_demo_participants=2,
        app_sequence=['embez'],
        treatment='negative'
    ),
    dict(
        name='positive',
        display_name="Embezzlement game - positive incentive",
        num_demo_participants=2,
        app_sequence=['embez'],
        treatment='positive'
    ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'k4y6sr0h22wfig5f0ish2w$pqy7ze)&sbqvff#zd)5i$wu-_i$'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
