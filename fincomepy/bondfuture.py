from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
import sys
sys.path.append(".")  ## TO DO: check if this is can be added to __init__.py
from fixedincome import FixedIncome
from bond import Bond

class BondFuture(Bond):
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 repo_period, repo_rate_perc, futures_pr_perc, conversion_factor, type='US'):
        FixedIncome.__init__(self)
        super().__init__(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        self._repo_period = repo_period
        self._perc_dict["repo_rate"] = repo_rate_perc
        self._repo_end_date = self._settlement + timedelta(days=repo_period)
        self._perc_dict["futures_pr_perc"] = futures_pr_perc
        self._conversion_factor = conversion_factor
        self._type = type   
        self.update_dict()
        self._forward_pr_perc = None
    
    #@classmethod
    #def from_end_date(cls, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
    #    bond_face_value, repo_end_date, repo_rate_perc, type='US'):
    #    repo_period = (repo_end_date - settlement).days
    #    return cls(settlement, maturity, coupon_perc, price_perc, frequency, basis, bond_face_value, repo_period, repo_rate_perc, type)
    
    def forward_price(self): 
        if self._type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        if self._forward_pr_perc is not None:
            return self._forward_pr_perc
        forward_pr_reg = self._reg_dict["dirty_price"] *  (1 + self._reg_dict["repo_rate"] * self._repo_period / days_in_year)
        self._forward_pr_perc = forward_pr_reg * 100
        return self._forward_pr_perc
    
 
