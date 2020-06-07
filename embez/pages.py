from otree.api import Currency as c, currency_range
from ._builtin import WaitPage
from .generic_pages import Page, OfficialPage, CitizenPage, InstructionPage
from .models import Constants


class FirstWP(WaitPage):
    group_by_arrival_time = True


class Instructions(InstructionPage):
    pass


class Examples(InstructionPage):
    pass


class CQs(InstructionPage):
    form_model = 'player'
    form_fields = [
        "cq1_1",
        "cq1_2",
        "cq2_1",
        "cq2_2",
        "cq3_1",
        "cq3_2",
    ]

    def before_next_page(self):
        qs = Constants.correct_answers
        results = [getattr(self.player, k) == v for k, v in qs.items()]

        self.player.tot_correct = sum(results)


class BeforeTheGame(InstructionPage):
    def vars_for_template(self):
        qs = Constants.correct_answers
        results = [getattr(self.player, k) == v for k, v in qs.items()]

        return dict(results=results)
        self.player.tot_correct = sum(results)
def is_displayed(self):
        return self.round_number == 1

from .models import Group


class PayTax(InstructionPage):
    def before_next_page(self):
        pseudo = self.subsession.player_set.get(pseudo=True)
        if not pseudo.group:

            g = Group.objects.create(session=self.session, subsession=self.subsession,
                                     id_in_subsession=Group.objects.all().count() + 1)
            g.save()
            self.player.group = g
            pseudo = self.subsession.player_set.get(pseudo=True)
            pseudo.group = g
        else:
            g = pseudo.group
            pseudo.group = None
            self.player.group = g
        self.player.tax_paid = self.player.endowment * Constants.tax_rate

    # def before_next_page(self):
    #     self.player.tax_paid = self.player.endowment * Constants.tax_rate


from django.utils.safestring import mark_safe


class IntermittentWP(WaitPage):
    body_text = mark_safe("""
      <div class="alert alert-danger font-weight-bold text-center">
        Сейчас вам необходимо  подождать второго участника Толоки. Пожалуйста, проявите терпение, так
        как это может занять некоторое время.
        Если вы ждете больше нескольких минут, дайте нам знать через систему сообщений толоки или по e-mail  
        <a href="mailto:fchapkovskiy@hse.ru">fchapkovskiy@hse.ru</a>.
    </div>
    """)
    after_all_players_arrive = 'after_group_is_formed'


class RoleAnnouncement(InstructionPage):
    pass


class CheckIncrease(CitizenPage):
    form_model = 'group'
    form_fields = ['check_investment']

    def extra_is_displayed(self):
        return self.session.config.get('treatment') == 'negative'

    def before_next_page(self):
        self.group.final_check_prob = Constants.checking_prob + self.group.check_investment * Constants.investment_coef


class KDeclare(OfficialPage):
    form_model = 'group'
    form_fields = ['k_declare']


class KBelief(CitizenPage):
    form_model = 'group'
    form_fields = ['k_belief']

    def before_next_page(self):
        self.player.set_guess_payoff()


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

    def vars_for_template(self):
        if self.player.role() == 'officer':
            return dict(body_text='Пожалуйста, подождите второго участника')
        else:
            return dict(body_text='Пожалуйста, ожидайте решения Чиновника о коэффициенте')


class Results(Page):
    pass


class Incentives(Page):
    form_model = 'player'

    def get_form_fields(self):
        if self.player.role() == 'officer':
            q = [
                'off_pos',
                'off_neg'
            ]
        else:
            q = [
                'cit_pos',
                'cit_neg'
            ]
        return q + ['quest']


page_sequence = [
    Instructions,
    Examples,
    BeforeTheGame,
    PayTax,
    IntermittentWP,
    RoleAnnouncement,
    CheckIncrease,
    KDeclare,
    ResultsWaitPage,
    Results,
    KBelief,
    Incentives,
]
