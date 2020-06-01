from otree.api import Currency as c, currency_range
from ._builtin import WaitPage
from questionnaire.generic_pages import Page
from .models import Constants


class Intro(Page):
    def vars_for_template(self):
        return dict(cents_per_10=self.session.config.get('real_world_currency_per_point', 1) * 1000)


page_sequence = [
    Intro
]
