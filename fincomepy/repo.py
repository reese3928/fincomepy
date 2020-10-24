from datetime import date, timedelta
import numpy as np
from scipy.optimize import root
from fincomepy.fixedincome import FixedIncome
from fincomepy.bond import Bond

class Repo(Bond):
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 bond_face_value, repo_period, repo_rate_perc, type='US'):
        FixedIncome.__init__(self)
        super().__init__(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        self._repo_period = repo_period
        self._perc_dict["repo_rate"] = repo_rate_perc
        self._face_value = bond_face_value
        self._repo_end_date = self._settlement + timedelta(days=repo_period)
        self._type = type  
        self.update_dict()
        self._start_payment = None
        self._end_payment = None
    
    @classmethod
    def from_end_date(cls, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
        bond_face_value, repo_end_date, repo_rate_perc, type='US'):
        repo_period = (repo_end_date - settlement).days
        return cls(settlement, maturity, coupon_perc, price_perc, frequency, basis, bond_face_value, repo_period, repo_rate_perc, type)
        
    def start_payment(self):
        if self._start_payment:
            return self._start_payment
        self._start_payment = self._face_value * self._reg_dict["dirty_price"]
        return self._start_payment
    
    def end_payment(self): 
        if self._type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        if self._end_payment:
            return self._end_payment
        repo_interest = self._start_payment * self._reg_dict["repo_rate"] * self._repo_period / days_in_year
        end_payment = self._start_payment + repo_interest
        coupon_payment = 0.0
        int_on_coupon = 0.0
        coupon_dates = self.coupon_dates()
        for item in coupon_dates:
            if item <= self._repo_end_date:
                coupon_one_period = self._face_value * self._reg_dict["coupon"] / self._frequency
                coupon_payment += coupon_one_period
                int_on_coupon += coupon_one_period * self._reg_dict["repo_rate"] * (self._repo_end_date - item).days / days_in_year
        self._end_payment = end_payment - coupon_payment - int_on_coupon
        return self._end_payment

    @staticmethod
    def get_start_payment(bond_face_value, dirty_price_perc, margin_perc=None, haircut_perc=None):
        '''Calculate repo start payment based on bond face value and dirty price.

        Parameters
        ----------
        bond_face_value: float
            A float which specifies the face value of bond.
        dirty_price_perc: float
            A float which specifies the dirty price (in percent) of bond.
       
        Returns
        -------
        float
            The start payment of repo.
        
        Examples
        --------
        >>> start_payment = Repo.get_start_payment(bond_face_value=100000000, dirty_price_perc=100.06)
        >>> print(start_payment)
        100060000.0
        '''
        start_payment = bond_face_value * dirty_price_perc * 0.01
        if margin_perc and haircut_perc:
            print("Warning: both margin and haircut are provided. Only margin is used.")
        if margin_perc:
            return start_payment / margin_perc * 100
        if haircut_perc:
            return start_payment * (1.0 - haircut_perc * 0.01)
        return start_payment

    @staticmethod
    def get_end_payment(bond_face_value, dirty_price_perc, repo_rate_perc, repo_period, type="US"):
        '''Calculate repo end payment based on bond face value, dirty price, repo rate, repo period. 
        This function is not able to consider coupon payment during repo period.

        Parameters
        ----------
        bond_face_value: float
            A float which specifies the face value of bond.
        dirty_price_perc: float
            A float which specifies the dirty price (in percent) of bond.
        repo_rate_perc: float
            A float which specifies the repo interest rate (in percent).
        repo_period: int
            An int which indicates the repo period (in days). 
        type: str
            A string which specifies the money market of repo. It should be either 'US' or 'UK'.
        
        Returns
        -------
        float
            The end payment of repo.
        
        Examples
        --------
        >>> end_payment = Repo.get_end_payment(bond_face_value=100000000, dirty_price_perc=100.06,
            repo_period=32, repo_rate_perc=0.145, type='US')
        >>> print(end_payment)
        100072896.62222221
        '''
        if type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        start_payment = Repo.get_start_payment(bond_face_value, dirty_price_perc)
        repo_interest = start_payment * repo_rate_perc * 0.01 * repo_period / days_in_year
        end_payment = start_payment + repo_interest
        return end_payment
    
    def purchase_pr_with_margin(self, margin_perc=None):
        if margin_perc is None:
            return self.start_payment()
        return self.start_payment() / margin_perc * 100
    
    def purchase_pr_with_haircut(self, haircut_perc=None):
        if haircut_perc is None:
            return self.start_payment()
        return self.start_payment() * (1.0 - haircut_perc * 0.01)
        
    def break_even_yld(self, *args, **kwargs):
        self._forward_date = self._settlement + timedelta(days=self._repo_period)
        forward_ai = self.accrint(self._couppcd, self._coupncd, self._forward_date, self._perc_dict["coupon"]) * 0.01 * self._face_value
        forward_clean_price = (self._end_payment - forward_ai) / self._face_value
        forward_clean_price_perc = forward_clean_price * 100
        self._price_change = forward_clean_price_perc - self._perc_dict["clean_price"]
        forward_DP_regular = self._end_payment / self._face_value
        forward_DP_perc = forward_DP_regular * 100
        sol = root(lambda x: self.dirty_price(self._settlement, self._maturity, self._perc_dict["coupon"], 
            x, self._redemption, self._frequency, self._basis) - forward_DP_perc, [0.01], *args, **kwargs)
        forward_yield_perc = sol.x[0]
        assert forward_yield_perc >= 0 and forward_yield_perc <= 100
        return forward_yield_perc

