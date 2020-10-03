from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
import sys
from scipy.optimize import root
sys.path.append(".")  ## TO DO: check if this is can be added to __init__.py
from fixedincome import FixedIncome
from bond import Bond

class Repo(Bond):
    ## TO DO: add margin and haircut
    ## TO DO: consider the case that repo period cover coupon payment date
    ## TO DO: add a constructor with repo start date and repo end date input
    ## TO DO: add repo constructor wihout bond information
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 bond_face_value, repo_period, repo_rate_perc):
        FixedIncome.__init__(self)
        super().__init__(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        self._repo_period = repo_period
        self._perc_dict["repo_rate"] = repo_rate_perc
        self._face_value = bond_face_value
        self.update_dict()
    
    def start_payment(self, haircut=None):  ## TO DO: add margin and haircut
        self._start_payment = self._face_value * self._reg_dict["dirty_price"]
        return self._start_payment
    
    def end_payment(self):
        ## TO DO: change 360 to UK:365
        self._repo_interest = self._start_payment * self._reg_dict["repo_rate"] * self._repo_period / 360
        self._end_payment = self._start_payment + self._repo_interest 
        return self._end_payment
    
    def break_even(self):
        self._forward_date = self._settlement + timedelta(days=self._repo_period)
        forward_ai = self.accrint(self._couppcd, self._coupncd, self._forward_date, self._perc_dict["coupon"]) * 0.01 * self._face_value
        forward_clean_price = (self._end_payment - forward_ai) / self._face_value
        forward_clean_price_perc = forward_clean_price * 100
        self._price_change = forward_clean_price_perc - self._perc_dict["clean_price"]
        forward_DP_regular = self._end_payment / self._face_value
        forward_DP_perc = forward_DP_regular * 100
        sol = root(lambda x: self.dirty_price(self._settlement, self._maturity, self._perc_dict["coupon"], 
            x, self._redemption, self._frequency, self._basis) - forward_DP_perc, [0.01])
        forward_yield_perc = sol.x[0]
        assert forward_yield_perc >= 0 and forward_yield_perc <= 100
        return forward_yield_perc

