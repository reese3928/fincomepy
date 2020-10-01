from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
from scipy.optimize import root
import sys
sys.path.append(".")  ## TO DO: check if this is can be added to __init__.py
from fixedincome import FixedIncome

## TO DO: 
# 1. change self._perc_dict["yield"] -> yield
# 2. make regular number as a dict, perc as another dict
# 3. add convexity adjustment (approximate bond price change using DV01 and convexity)

class Bond(FixedIncome):
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis=1):
        ## TO DO: split clean price into 32nd
        super().__init__()
        self._settlement = settlement
        self._maturity = maturity
        self._coupon_interval = 12 / frequency
        self._nperiod = math.ceil((Bond.diff_month(self._settlement, self._maturity))/self._coupon_interval)
        self._perc_dict["coupon"] = coupon_perc
        self._perc_dict["clean_price"] = price_perc
        self._frequency = frequency
        self._basis = basis
        self._couppcd = Bond.couppcd(settlement, maturity, frequency, basis)
        self._coupncd = Bond.coupncd(settlement, maturity, frequency, basis)
        #self._coupon_dates = [self.last_day_in_month(item) for item in self._coupon_dates]
        self._perc_dict["accrint"] = self.accrint(self._couppcd, self._coupncd, self._settlement, self._perc_dict["coupon"], 100, self._frequency, self._basis)
        self._perc_dict["dirty_price"] = self._perc_dict["clean_price"] + self._perc_dict["accrint"]
        self.update_dict()
    
    @staticmethod
    def couppcd(settlement, maturity, frequency, basis):
        coupon_interval = 12 / frequency
        nperiod = math.ceil((Bond.diff_month(settlement, maturity))/coupon_interval)
        pcd = maturity - relativedelta(months=coupon_interval) * nperiod
        if maturity==Bond.last_day_in_month(maturity):
            return Bond.last_day_in_month(pcd)
        return pcd
    
    @staticmethod
    def coupncd(settlement, maturity, frequency, basis):
        coupon_interval = 12 / frequency
        nperiod = math.ceil((Bond.diff_month(settlement, maturity))/coupon_interval)
        ncd = maturity - relativedelta(months=coupon_interval) * (nperiod - 1)
        if maturity==Bond.last_day_in_month(maturity):
            return Bond.last_day_in_month(ncd)
        return ncd



    # coupon_dates = [maturity - relativedelta(months=coupon_interval)*i for i in range(nperiod)]  ## TO DO: add coupon_dates calculation


    def price(self, yield_perc): ## to do change function name to dirty price
        first_period = (self._coupncd - self._settlement).days / (self._coupncd - self._couppcd).days
        self._periods = np.array([first_period + i for i in range(self._nperiod)])
        CF_perc = np.array([self._perc_dict["coupon"] / self._frequency] * self._nperiod)
        CF_perc[-1] += 100  ## change this to par
        #self._perc_dict["CF"] = CF_perc
        #self._perc_dict["yield"] = yield_perc
        #self.update_dict()
        CF_regular = CF_perc*0.01
        yield_regular = yield_perc * 0.01
        self.DF = 1 / (1 + yield_regular / self._frequency) ** self._periods
        self.CF_PV = CF_regular * self.DF
        CF_PV_total = sum(self.CF_PV)
        return CF_PV_total*100  ## TO DO: change this
    
    def get_yield(self):
        sol = root(lambda x: self.price(x)/100 - self._reg_dict["dirty_price"], [0.01] )
        yield_perc = sol.x[0]
        self._perc_dict["yield"] = yield_perc
        self.update_dict()
        return yield_perc
    
    def get_mac_duration(self):
        self.CF_PV_times_p = self.CF_PV * self._periods
        return self.CF_PV_times_p.sum() / self._reg_dict["dirty_price"] / self._frequency

    def get_mod_duration(self):
        original_yield_perc = self.get_yield()
        ## TO DO: make 0.01 as an argument
        yield_up_perc = original_yield_perc + 0.01
        yield_down_perc = original_yield_perc - 0.01
        dirty_price_up_perc = self.price(yield_up_perc)
        dirty_price_down_perc = self.price(yield_down_perc)
        price_change_up_perc = dirty_price_up_perc - self._perc_dict["dirty_price"]
        price_change_down_perc = dirty_price_down_perc - self._perc_dict["dirty_price"]
        relative_change_up = price_change_up_perc / self._perc_dict["dirty_price"]
        relative_change_down = price_change_down_perc / self._perc_dict["dirty_price"]
        self._mod_duration = (abs(relative_change_up) + abs(relative_change_down)) / 2 / (0.01*0.01) ## TO DO: change this
        return self._mod_duration
    
    def get_DV01(self):
        self._DV01 = self._mod_duration * self._reg_dict["dirty_price"]
        return self._DV01
    
    def get_convexity(self):
        self.CF_PV_times_p_2 = self.CF_PV * self._periods * self._periods
        all = (self.CF_PV_times_p + self.CF_PV_times_p_2) / self._reg_dict["dirty_price"]
        self._convexity = all.sum() / (4 * (1 + self._reg_dict["yield"] / self._frequency) ** 2)
        return self._convexity

    @staticmethod
    def accrint(issue, first_interest, settlement, rate, par=100, frequency=2, basis=1):
        ## TO DO: change par=100
        ## TO DO: check if first_interest > issue
        total_days = (first_interest - issue).days
        accrued_days = (settlement - issue).days
        rate_regular = rate/100
        accrued_interest_perc = (rate_regular/frequency) * (accrued_days / total_days)
        return accrued_interest_perc*100

    @staticmethod
    def diff_month(date1, date2):
        return (date2.year - date1.year) * 12 + date2.month - date1.month
    
    @staticmethod
    def last_day_in_month(original_date):
        next_month = original_date.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)




