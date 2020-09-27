from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
from scipy.optimize import root

class FixedIncome(object):
    def __init__(self):
        pass
    
    @staticmethod
    def perc_to_regular(percentage_values):
        return percentage_values*0.01

    @staticmethod
    def regular_to_perc(regular_values):
        return regular_values*100

## TO DO: 
# 1. change yield_regular -> yield
# 2. make regular number as a dict, perc as another dict
# 3. add convexity adjustment (approximate bond price change using DV01 and convexity)

class Bond(FixedIncome):
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis=1):
        ## TO DO: split clean price into 32nd
        self._settlement = settlement
        self._maturity = maturity
        self._coupon_perc = coupon_perc
        self._clean_price_perc = price_perc
        self._frequency = frequency
        self._basis = basis
        self._coupon_interval = 12 / frequency
        self._nperiod = math.ceil((self.diff_month(self._settlement, self._maturity))/self._coupon_interval)
        self._coupon_dates = [self._maturity - relativedelta(months=self._coupon_interval)*i for i in range(self._nperiod)]
        self._couppcd = self._maturity - relativedelta(months=self._coupon_interval)*(self._nperiod)
        self._coupncd = self._coupon_dates[-1]
        if self._maturity==self.last_day_in_month(self._maturity):
            self._coupon_dates = [self.last_day_in_month(item) for item in self._coupon_dates]
            self._couppcd = self.last_day_in_month(self._couppcd)
            self._coupncd = self.last_day_in_month(self._coupncd)
        self._accrint = self.accrint(self._couppcd, self._coupncd, self._settlement, self._coupon_perc, 100, self._frequency, self._basis)
        self._dirty_price_perc = self._clean_price_perc + self._accrint

    def price(self, yield_perc): ## to do change function name to dirty price
        first_period = (self._coupncd - self._settlement).days / (self._coupncd - self._couppcd).days
        self._periods = np.array([first_period + i for i in range(self._nperiod)])
        CF_perc = np.array([self._coupon_perc / self._frequency] * self._nperiod)
        CF_perc[-1] += 100  ## change this to par
        self.CF_regular = FixedIncome.perc_to_regular(CF_perc)
        yield_regular = FixedIncome.perc_to_regular(yield_perc)
        self.DF = 1 / (1 + yield_regular / self._frequency) ** self._periods
        self.CF_PV = self.CF_regular * self.DF
        CF_PV_total = sum(self.CF_PV)
        return FixedIncome.regular_to_perc(CF_PV_total)
    
    def get_yield(self):
        dirty_price_regular = FixedIncome.perc_to_regular(self._dirty_price_perc)
        sol = root(lambda x: FixedIncome.perc_to_regular(self.price(x)) - dirty_price_regular, [0.01] )
        yield_perc = sol.x[0]
        self._yield_regular = FixedIncome.perc_to_regular(yield_perc)
        return yield_perc
    
    def get_mac_duration(self):
        self.CF_PV_times_p = self.CF_PV * self._periods
        return self.CF_PV_times_p.sum() / FixedIncome.perc_to_regular(self._dirty_price_perc) / self._frequency

    def get_mod_duration(self):
        original_yield_perc = self.get_yield()
        ## TO DO: make 0.01 as an argument
        yield_up_perc = original_yield_perc + 0.01
        yield_down_perc = original_yield_perc - 0.01
        dirty_price_up_perc = self.price(yield_up_perc)
        dirty_price_down_perc = self.price(yield_down_perc)
        price_change_up_perc = dirty_price_up_perc - self._dirty_price_perc
        price_change_down_perc = dirty_price_down_perc - self._dirty_price_perc
        relative_change_up = price_change_up_perc / self._dirty_price_perc
        relative_change_down = price_change_down_perc / self._dirty_price_perc
        self._mod_duration = (abs(relative_change_up) + abs(relative_change_down)) / 2 / FixedIncome.perc_to_regular(0.01)
        return self._mod_duration
    
    def get_DV01(self):
        self._DV01 = self._mod_duration * FixedIncome.perc_to_regular(self._dirty_price_perc)
        return self._DV01
    
    def get_convexity(self):
        self.CF_PV_times_p_2 = self.CF_PV * self._periods * self._periods
        all = (self.CF_PV_times_p + self.CF_PV_times_p_2) / FixedIncome.perc_to_regular(self._dirty_price_perc)
        self._convexity = all.sum() / (4 * (1 + self._yield_regular / self._frequency) ** 2)
        return self._convexity

    @staticmethod
    def accrint(issue, first_interest, settlement, rate, par=100, frequency=2, basis=1):
        ## TO DO: change par=100
        ## TO DO: check if first_interest > issue
        total_days = (first_interest - issue).days
        accrued_days = (settlement - issue).days
        rate_regular = FixedIncome.perc_to_regular(rate)
        accrued_interest_perc = (rate_regular/frequency) * (accrued_days / total_days)
        return FixedIncome.regular_to_perc(accrued_interest_perc)

    @staticmethod
    def diff_month(date1, date2):
        return (date2.year - date1.year) * 12 + date2.month - date1.month
    
    @staticmethod
    def last_day_in_month(original_date):
        next_month = original_date.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)


bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(100+0.5/32), frequency=2, basis=1)
bond_test._coupon_interval
bond_test._couppcd
bond_test._coupncd
bond_test._accrint
bond_test._dirty_price_perc
bond_test.price(0.62334818)
bond_test.get_yield()
bond_test.get_mac_duration()

bond_test = Bond(settlement=date(2020,7,15), maturity=date(2025,6,30), coupon_perc=0.25, 
                 price_perc=(99+26/32), frequency=2, basis=1)
bond_test.get_yield()
print("accrued_interest: {}".format(bond_test._accrint))
print("Mac duration: {}".format(bond_test.get_mac_duration()))
print("Modified duration: {}".format(bond_test.get_mod_duration()))
print("DV01: {}".format(bond_test.get_DV01()))
print("Convexity: {}".format(bond_test.get_convexity()))

print("----------------------")
bond_test = Bond(settlement=date(2020,7,15), maturity=date(2022,6,30), coupon_perc=1/8, 
                 price_perc=(99+30/32), frequency=2, basis=1)
bond_test.get_yield()
print("accrued_interest: {}".format(bond_test._accrint))
print("Mac duration: {}".format(bond_test.get_mac_duration()))
print("Modified duration: {}".format(bond_test.get_mod_duration()))
print("DV01: {}".format(bond_test.get_DV01()))
print("Convexity: {}".format(bond_test.get_convexity()))
print("----------------------")

Bond.accrint(issue=bond_test._couppcd, first_interest=bond_test._coupncd, settlement=bond_test._settlement, 
             rate=0.625, par=100, frequency=2, basis=1)

bond_test = Bond(date(2010,10,10), date(2016,1,7), 4.75, 1, 1)
bond_test._coupon_interval
bond_test._nperiod
bond_test._coupon_dates
bond_test._couppcd
bond_test._coupncd


class Repo(Bond):
    ## TO DO: add margin and haircut
    ## TO DO: consider the case that repo period cover coupon payment date
    ## TO DO: add a constructor with repo start date and repo end date input
    ## TO DO: add repo constructor wihout bond information
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 bond_face_value, repo_period, repo_rate_perc):
        super().__init__(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        self._repo_period = repo_period
        self._repo_rate_perc = repo_rate_perc
        self._face_value = bond_face_value
    
    def repo_start_payment(self, haircut=None):  ## TO DO: add margin and haircut
        self._repo_start_payment = self._face_value * FixedIncome.perc_to_regular(self._dirty_price_perc)
        return self._repo_start_payment
    
    def repo_end_payment(self):
        ## TO DO: change 360 to UK:365
        self._repo_interest = self._repo_start_payment * FixedIncome.perc_to_regular(self._repo_rate_perc) * self._repo_period / 360
        self._repo_end_payment = self._repo_start_payment + self._repo_interest 
        return self._repo_end_payment
    
    def repo_break_even(self):
        self._forward_date = self._settlement + timedelta(days=self._repo_period)
        forward_ai = FixedIncome.perc_to_regular(self.accrint(self._couppcd, self._coupncd, self._forward_date, self._coupon_perc)) * self._face_value
        forward_clean_price = (self._repo_end_payment - forward_ai) / self._face_value
        forward_clean_price_perc = FixedIncome.regular_to_perc(forward_clean_price)
        self._price_change = forward_clean_price_perc - self._clean_price_perc
        ## TO DO: change this, make get_yield as a function that take argument
        forward_DP_regular = self._repo_end_payment / self._face_value
        sol = root(lambda x: FixedIncome.perc_to_regular(self.price(x)) - forward_DP_regular, [0.01] )
        forward_yield_perc = sol.x[0]
        self._forward_yield_regular = FixedIncome.perc_to_regular(forward_yield_perc)
        return forward_yield_perc

repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(99+30/32), frequency=2, basis=1, 
                 bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
repo_test.get_yield()
print("accrued_interest: {}".format(repo_test._accrint))
print("Mac duration: {}".format(repo_test.get_mac_duration()))
print("Modified duration: {}".format(repo_test.get_mod_duration()))
print("DV01: {}".format(repo_test.get_DV01()))
print("Convexity: {}".format(repo_test.get_convexity()))
print("Repo period: {}".format(repo_test._repo_period))
print("Repo interest: {}".format(repo_test._repo_rate_perc))
print("Repo start payment: {}".format(repo_test.repo_start_payment()))
print("Repo end payment: {}".format(repo_test.repo_end_payment()))
print("----------------------")

repo_test = Repo(settlement=date(2020,7,16), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=99.953125, frequency=2, basis=1, 
                 bond_face_value=100000000, repo_period=32, repo_rate_perc=0.145)
repo_test.get_yield()
print("accrued_interest: {}".format(repo_test._accrint))
print("Mac duration: {}".format(repo_test.get_mac_duration()))
print("Modified duration: {}".format(repo_test.get_mod_duration()))
print("DV01: {}".format(repo_test.get_DV01()))
print("Convexity: {}".format(repo_test.get_convexity()))
print("Repo period: {}".format(repo_test._repo_period))
print("Repo interest: {}".format(repo_test._repo_rate_perc))
print("Repo start payment: {}".format(repo_test.repo_start_payment()))
print("Repo end payment: {}".format(repo_test.repo_end_payment()))
print("Repo break even yield: {}".format(repo_test.repo_break_even()))
print("----------------------")


