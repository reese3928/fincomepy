from datetime import date, timedelta
import numpy as np
from scipy.optimize import root
from fincomepy.fixedincome import FixedIncome
from fincomepy.bond import Bond

class Repo(Bond):
    '''
    A class used to perform repo related calculations.

    Attributes
    ----------
    _reg_dict : dict
        A dictionary which contains the regular quantities. The keys of _reg_dict should be the
        same as that of _perc_dict.
    _perc_dict : dict
        A dictionary which contains the quantities in percent. The keys of _perc_dict should be the
        same as that of _reg_dict.
    _settlement: datetime.date
        A date object which specifies the bond settlement date.
    _maturity: datetime.date
        A date object which specifies the maturity date.
    _frequency: int
        An integer which specifies coupon payment frequency.
    _basis: int
        An integer which indicates day count convention. 
    _redemption: float
        A float which specifies bond redemption (in percent). 
    _couppcd: datetime.date
        A date object which indicates the previous coupon payment date.
    _coupncd: datetime.date
        A date object which indicates the next coupon payment date.
    _yld: float
        A float which indicates bond yield (in percent).
    _mac_duration: float
        A float which indicates the Macaulay duration of a bond.
    _mod_duration: float
        A float which indicates the modified duration of a bond.
    _DV01: float
        A float which indicates the DV01 of a bond.
    _convexity: float
        A float which indicates the convexity of a bond.
    _repo_period: int
        An int which indicates the repo period (in days). 
    _face_value: float
        A float which specifies the face value of bond.
    _repo_end_date: datetime.date
        A date object which specifies the end date of repo.
    _type: str
        A string which indicates money market. 
    _start_payment: float
        A float which specifies repo start payment.
    _end_payment: float
        A float which specifies repo end payment.
    
    Methods
    -------
    couppcd(settlement, maturity, frequency, basis)
        Get the previous coupon payment date.
    coupncd(settlement, maturity, frequency, basis)
        Get the next coupon payment date.
    accrint(issue, first_interest, settlement, rate, par, frequency, basis)
        Calculate the accrued interest of coupon.
    dirty_price(settlement, maturity, rate, yld, redemption, frequency, basis)
        Calculate the dirty price of a bond.
    yld(settlement, maturity, rate, pr, redemption, frequency, basis, *args, **kwargs)
        Calculate the yield of a bond.
    mac_duration()
        Calculate the Macaulay duration of a bond.
    mod_duration(yld_change_perc)
        Calculate the modified duration of a bond.
    DV01()
        Calculate the DV01 of a bond.
    convexity()
        Calculate the convexity of a bond.
    price_change(yld_change_perc)
        Calculate the bond price change based on yield change.
    diff_month(date1, date2)
        Get the month difference between two dates.
    last_day_in_month(original_date)
        Get the last day for the input month.
    coupon_dates()
        Obtain the coupon payment dates of a bond.
    start_payment()
        Calculate repo start payment.
    end_payment()
        Calculate repo end payment.
    get_start_payment(bond_face_value, dirty_price_perc, margin_perc, haircut_perc)
        Calculate repo start payment based on bond face value and dirty price.
    get_end_payment(bond_face_value, dirty_price_perc, repo_rate_perc, repo_period, type)
        Calculate repo end payment based on bond face value, dirty price, repo rate, repo period.
    purchase_pr_with_margin(margin_perc)
        Calculate repo start payment with margin.
    purchase_pr_with_haircut(haircut_perc)
        Calculate repo start payment with haircut.
    break_even_yld(*args, **kwargs)
        Calculate bond break even yield.
    '''

    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 bond_face_value, repo_period, repo_rate_perc, type='US'):
        '''
        Constructor for Repo.

        Parameters
        ----------
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        maturity: datetime.date
            A date object which specifies the maturity date of the bond.
        coupon_perc: float
            A float which indicates the coupon rate (in percent) of the bond.
        price_perc: int, float, or str
            The clean price (in percent) of the bond.
            If it is a string, it should be in 32nd convention. The internal function 
            will parse the price in 32nd convention into regular price automatically.
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int, optional
            An integer which indicates day count convention. Default is 1.
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        bond_face_value: float
            A float which specifies the face value of bond.
        repo_period: int
            An int which indicates the repo period (in days). 
        repo_rate_perc: float
            A float which specifies the repo interest rate (in percent).
        type: str, optional
            A string which specifies the money market of repo. It should be either 'US' or 'UK'.
            Default is 'US'.

        Examples
        --------
        >>> repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), 
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        '''
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
        '''
        Constructor for Repo.

        Parameters
        ----------
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        maturity: datetime.date
            A date object which specifies the maturity date of the bond.
        coupon_perc: float
            A float which indicates the coupon rate (in percent) of the bond.
        price_perc: int, float, or str
            The clean price (in percent) of the bond.
            If it is a string, it should be in 32nd convention. The internal function 
            will parse the price in 32nd convention into regular price automatically.
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int, optional
            An integer which indicates day count convention. Default is 1.
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        bond_face_value: float
            A float which specifies the face value of bond.
        repo_end_date: datetime.date
            A date object which indicates the repo end date. 
        repo_rate_perc: float
            A float which specifies the repo interest rate (in percent).
        type: str, optional
            A string which specifies the money market of repo. It should be either 'US' or 'UK'.
            Default is 'US'.

        Examples
        --------
        >>> repo_test = Repo.from_end_date(settlement=date(2020,7,15), maturity=date(2030,5,15),
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_end_date=date(2020,7,16), repo_rate_perc=0.145)
        '''
        repo_period = (repo_end_date - settlement).days
        return cls(settlement, maturity, coupon_perc, price_perc, frequency, basis, bond_face_value, repo_period, repo_rate_perc, type)
        
    def start_payment(self):
        '''Calculate repo start payment.

        Returns
        -------
        float
            A float which specifies repo start payment.
        
        Examples
        --------
        >>> repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), 
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        >>> repo_test.start_payment()
        100041100.54347825
        '''
        if self._start_payment:
            return self._start_payment
        self._start_payment = self._face_value * self._reg_dict["dirty_price"]
        return self._start_payment
    
    def end_payment(self): 
        '''Calculate repo end payment.

        Returns
        -------
        float
            A float which specifies repo end payment.
        
        Examples
        --------
        >>> repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), 
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        >>> repo_test.end_payment()
        100041503.48679988
        '''
        days_in_year = 360 if self._type == 'US' else 365
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
        margin_perc: float, optional
            A float which specifies the margin (in percent) of purchase price.
            Default is None. 
        haircut_perc: float, optional
            A float which specifies the haircut (in percent) of purchase price.
            Default is None. 

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
        type: str, optional
            A string which specifies the money market of repo. It should be either 'US' or 'UK'.
            Default is 'US'.
        
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
        days_in_year = 360 if type == 'US' else 365
        start_payment = Repo.get_start_payment(bond_face_value, dirty_price_perc)
        repo_interest = start_payment * repo_rate_perc * 0.01 * repo_period / days_in_year
        end_payment = start_payment + repo_interest
        return end_payment
    
    def purchase_pr_with_margin(self, margin_perc=None):
        '''Calculate repo start payment with margin.

        Parameters
        ----------
        margin_perc: float, optional
            A float which specifies the margin (in percent) of purchase price.
            Default is None. 

        Returns
        -------
        float
            The purchase price of repo.
        
        Examples
        --------
        >>> repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), 
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        >>> repo_test.purchase_pr_with_margin(margin_perc=102)
        98079510.33674338
        '''
        if not margin_perc:
            return self.start_payment()
        return self.start_payment() / margin_perc * 100
    
    def purchase_pr_with_haircut(self, haircut_perc=None):
        '''Calculate repo start payment with haircut.

        Parameters
        ----------
        haircut_perc: float, optional
            A float which specifies the haircut (in percent) of purchase price.
            Default is None. 

        Returns
        -------
        float
            The purchase price of repo.
        
        Examples
        --------
        >>> repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), 
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        >>> repo_test.purchase_pr_with_haircut(haircut_perc=2)
        98040278.53260869
        '''
        if not haircut_perc:
            return self.start_payment()
        return self.start_payment() * (1.0 - haircut_perc * 0.01)
        
    def break_even_yld(self, *args, **kwargs):
        '''Calculate bond break even yield.

        Parameters
        ----------
        *args : optional
            Positional argument passed to scipy.optimize.root.
        **kwargs : optional
            Keyword argument passed to scipy.optimize.root. 

        Returns
        -------
        float
            The break even yield (in percent) of bond.
        
        Examples
        --------
        >>> repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), 
                coupon_perc=0.625, price_perc=(99+30/32), frequency=2, basis=1, 
                bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        >>> repo_test.break_even_yld()
        0.6315109737743813
        '''
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

