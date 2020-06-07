from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from otree.common import random_chars_8
import random
import numpy as np
from decimal import *

author = 'Anna'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'embez'
    players_per_group = None
    num_rounds = 1
    k_min = 1
    k_max = 3
    k_step = 0.25
    endowment = 10
    tax_rate = .5
    left_endowment = int((1 - tax_rate) * endowment)
    presumed_players_per_group = 2
    total_taxes = presumed_players_per_group * endowment * tax_rate
    coef = .2
    checking_prob = .3
    investment_coef = 0.05  # that is the probability increase due to investment
    checking_prob_formatted = f"{checking_prob:0.0%}"
    rest_prob_formatted = f"{1 - checking_prob:0.0%}"
    K_CHOICES = list(np.arange(k_min, k_max + 0.01, k_step))
    fine_coef = 1.5
    guess_bonus = c(5)
    correct_answers = dict(
        cq1_1=10,
        cq1_2=30,
        cq2_1=15,
        cq2_2=10,
        cq3_1=20,
        cq3_2=20,
    )
    IS_OCCUPIED_CHOICES = [[False, ('Нет')], [True, ('Да')]]


from django.forms.models import model_to_dict
from otree.models import Participant


class Subsession(BaseSubsession):
    treatment = models.StringField()
    sign = models.BooleanField(initial=True)

    @property
    def cents_per_10_tokens(self):
        return self.session.config.get('real_world_currency_per_point', 1) * 1000

    def creating_session(self):
        ########### BLOCK: PSEUDO ##############################################################
        kwargs = model_to_dict(self.session.get_participants()[0], exclude=['id',
                                                                            'code',
                                                                            'session',
                                                                            'pk', 'vars', 'id_in_session'])
        kwargs['code'] = random_chars_8()
        kwargs['id_in_session'] = 100000
        kwargs['session'] = self.session
        pa = Participant.objects.create(**kwargs)
        p = Player.objects.create(participant=pa, session=self.session, subsession=self)
        p.pseudo = True
        ############ END OF: PSEUDO #############################################################

        self.treatment = self.session.config.get('treatment')
        if self.treatment == 'negative':
            self.sign = False
        #  we give to each player some money at the beginning
        for p in self.get_players():
            p.endowment = Constants.endowment


class Group(BaseGroup):
    real_k = models.FloatField()
    check_investment = models.IntegerField(min=0, max=Constants.left_endowment)
    final_check_prob = models.FloatField(initial=Constants.checking_prob)
    k_declare = models.FloatField(
        widget=widgets.RadioSelectHorizontal,
        label='Выберите значение коэффициента, которое Вы объявите Гражданину:')

    def k_declare_choices(self):
        return [f'{i:.2f}' for i in Constants.K_CHOICES if i <= self.real_k]

    def k_belief_choices(self):
        return [f'{i:.2f}' for i in Constants.K_CHOICES if i >= self.k_declare]

    incentive = models.IntegerField()
    k_belief = models.FloatField(label='Как Вы думаете, чему был равен истинный коэффициент?',
                                 choices=Constants.K_CHOICES,
                                 widget=widgets.RadioSelectHorizontal, )
    taxes_paid = models.CurrencyField()
    taxes_multiplied = models.CurrencyField()
    taxes_paid_back = models.CurrencyField()
    individual_share = models.CurrencyField()
    embezzled_amount = models.CurrencyField(initial=0)
    officer_checked = models.BooleanField()
    true_k = models.BooleanField()
    officer_fine = models.CurrencyField()

    @property
    def officer(self):
        return self.get_player_by_role('officer')

    def after_group_is_formed(self):
        # in each period in each group an official is checked with certain probability.
        # we also generate a certain K based on which official can declare his own K
        for i, p in enumerate(self.get_players(), start=1):
            p.id_in_group = i

        self.real_k = random.choice(Constants.K_CHOICES)
        current_inp = self.get_players()[0].participant._index_in_pages
        numlasts = self.session.participant_set.filter(_index_in_pages__lt=current_inp)
        if numlasts.count() == 1:
            lastone = numlasts[0]
            if lastone.id_in_session == 100000:
                print('GONNA DELETE')
                lastone.delete()

    def generate_checking(self):
        """Define whether officer is checked"""
        r = random.random()

        self.officer_checked = r < self.final_check_prob

    def apply_sanctions(self):
        """Applying sanctions on officer if he is checked.
        The officer payoff is diminished by the embezzled amount IF he is checked.
        """
        self.officer_fine = self.embezzled_amount * Constants.fine_coef
        self.officer.payoff -= self.officer_checked * (not self.true_k) * self.officer_fine

    def set_payoffs(self):
        self.generate_checking()
        # we get two user (officer and citizen)
        officer = self.officer
        citizen = self.get_player_by_role('citizen')
        # we check if officer lied
        self.true_k = self.real_k == self.k_declare
        # collect all paid taxes
        self.taxes_paid = sum([p.tax_paid for p in self.get_players()])
        self.taxes_multiplied = self.taxes_paid * self.real_k;
        self.taxes_paid_back = self.taxes_paid * self.k_declare;
        # calculate how much everone one get based on amount declared by officer
        self.individual_share = self.taxes_paid_back / Constants.presumed_players_per_group
        # calculated an embezzled amount
        self.embezzled_amount = self.taxes_multiplied - self.taxes_paid_back
        for p in self.get_players():
            p.payoff = p.endowment - p.tax_paid + self.individual_share
        # this is for the treatment

        officer.payoff += self.embezzled_amount
        # apply punishment on the officer (if any):
        self.apply_sanctions()


class Player(BasePlayer):
    pseudo = models.BooleanField(initial=False)
    endowment = models.CurrencyField()
    tax_paid = models.CurrencyField()
    guess_bonus = models.CurrencyField(initial=0)
    cq1_1 = models.IntegerField(label='Какое вознаграждение получает Гражданин?')
    cq1_2 = models.IntegerField(label='Какое вознаграждение получает Чиновник?')
    cq2_1 = models.IntegerField(label='Какое вознаграждение получает Гражданин?')
    cq2_2 = models.IntegerField(label='Какое вознаграждение получает Чиновник?')
    cq3_1 = models.IntegerField(label='Какое вознаграждение получает Гражданин?')
    cq3_2 = models.IntegerField(label='Какое вознаграждение получает Чиновник?')
    tot_correct = models.IntegerField(initial=0, doc='to count number of correct answers')
    off_pos = models.BooleanField(label=(
        "Если бы вы знали, что Гражданин может повысить вероятность проверки, стали бы вы объявлять коэффициент меньше истинного?"),
        choices=Constants.IS_OCCUPIED_CHOICES,
        widget=widgets.RadioSelectHorizontal)

    off_neg = models.BooleanField(label=(
        "Если бы у Гражданина была возможность заплатить вам деньги напрямую, вы бы стали объявлять истинное значение коэффициента?"),
        choices=Constants.IS_OCCUPIED_CHOICES,
        widget=widgets.RadioSelectHorizontal)

    cit_pos = models.BooleanField(label=(
        "Если бы у вас была возможность заплатить деньги, чтобы повысить вероятность проверки действий Чиновника, стали бы вы это делать?"),
        choices=Constants.IS_OCCUPIED_CHOICES,
        widget=widgets.RadioSelectHorizontal)

    cit_neg = models.BooleanField(label=(
        "Если бы вы могли напрямую заплатить Чиновнику, чтоб он объявил истинный коэффициент, стали бы вы это делать?"),
        choices=Constants.IS_OCCUPIED_CHOICES,
        widget=widgets.RadioSelectHorizontal)

    quest = models.LongStringField(
        label=('Если у вас возникли проблемы с пониманием инструкции, то напишите, что именно было непонятно:'),
        initial='Проблем не возникло')

    def set_guess_payoff(self):
        g = self.group
        self.guess_bonus = Constants.guess_bonus * (g.k_declare == g.k_belief)
        self.payoff += self.guess_bonus

    def role_desc(self):
        """return Russian description of role - for showing at the pages"""
        descs = dict(officer='Чиновник',
                     citizen='Гражданин')
        return descs.get(self.role())

    def role(self):
        """defines that the first player in group will be a bureaucrat"""
        if self.id_in_group == 1:
            return 'officer'
        return 'citizen'
