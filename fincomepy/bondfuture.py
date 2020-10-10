from datetime import date, timedelta
import numpy as np
import sys
import bisect
from fincomepy.fixedincome import FixedIncome
from fincomepy.bond import Bond

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
        self._future_val_perc = None
    
    @classmethod
    def from_end_date(cls, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
        repo_end_date, repo_rate_perc, futures_pr_perc, conversion_factor, type='US'):
        repo_period = (repo_end_date - settlement).days
        return cls(settlement, maturity, coupon_perc, price_perc, frequency, basis, 
            repo_period, repo_rate_perc, futures_pr_perc, conversion_factor, type)
    
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
    
    def full_future_val(self):
        if self._future_val_perc is not None:
            return self._future_val_perc
        if self._type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        invoice_pr_perc = self._perc_dict["futures_pr_perc"] * self._conversion_factor
        temp = list(self.coupon_dates())
        temp.reverse()
        ind = bisect.bisect_left(temp, self._repo_end_date)
        coupon_dates = temp[:ind]
        coupon_FV = 0.0 
        if len(coupon_dates) == 0:
            accrint_perc = Bond.accrint(self._couppcd, self._coupncd, self._repo_end_date, 
                self._perc_dict["coupon"], par=1, frequency=2, basis=1)
        else:
            for item in coupon_dates:
                reinvestment_days = (self._repo_end_date - item).days
                coupon_FV_one_period_reg = self._reg_dict["coupon"] / self._frequency * \
                    (1 + self._reg_dict["repo_rate"] * reinvestment_days / days_in_year)
                coupon_FV += coupon_FV_one_period_reg * 100
            ncd = Bond.coupncd(self._repo_end_date, self._maturity, self._frequency, self._basis)
            accrint_perc = Bond.accrint(coupon_dates[-1], ncd, self._repo_end_date, self._perc_dict["coupon"], 
                1, self._frequency, self._basis)
        self._future_val_perc = invoice_pr_perc + accrint_perc + coupon_FV
        return self._future_val_perc

    def net_basis(self):
        return (self.forward_price() - self.full_future_val()) * 32
    
    def implied_repo_rate(self): 
        if self._type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        implied_repo_reg = (self.full_future_val() / self._perc_dict["dirty_price"] - 1) * days_in_year / self._repo_period
        return implied_repo_reg * 100

    
 
