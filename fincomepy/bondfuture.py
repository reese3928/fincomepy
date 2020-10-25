from datetime import date, timedelta
import numpy as np
import bisect
from fincomepy.fixedincome import FixedIncome
from fincomepy.bond import Bond

class BondFuture(Bond):
    '''
    A class used to perform bond future related calculations.

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
    _repo_end_date: datetime.date
        A date object which specifies the end date of repo.
    _conversion_factor: float
        A float which indicates the conversion factor of future price.
    _type: str
        A string which indicates money market. 
    _forward_pr_perc: float
        A float which specifies the forward price (in percent).
    _future_val_perc: float
        A float which specifies the future price (in percent).
    
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
    forward_price()
        Calculate forward price. 
    full_future_val()
        Calculate full future value.
    net_basis():
        Calculate net basis of bond future.
    implied_repo_rate()
        Calculate implied repo rate.
    '''

    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 repo_period, repo_rate_perc, futures_pr_perc, conversion_factor, type='US'):
        '''
        Constructor for BondFuture.

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
        repo_period: int
            An int which indicates the repo period (in days). 
        repo_rate_perc: float
            A float which specifies the repo interest rate (in percent).
        futures_pr_perc: float
            A float which specifies the future price (in percent).
        conversion_factor: float
            A float which indicates the conversion factor of future price.
        type: str, optional
            A string which specifies the money market of repo. It should be either 'US' or 'UK'.
            Default is 'US'.

        Examples
        --------
        >>> bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        '''

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
        '''
        Constructor for BondFuture.

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
        repo_end_date: datetime.date
            An int which indicates the repo end date. 
        repo_rate_perc: float
            A float which specifies the repo interest rate (in percent).
        futures_pr_perc: float
            A float which specifies the future price (in percent).
        conversion_factor: float
            A float which indicates the conversion factor of future price.
        type: str, optional
            A string which specifies the money market of repo. It should be either 'US' or 'UK'.
            Default is 'US'.

        Examples
        --------
        >>> bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_end_date=date(2020,9,30), repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        '''
        repo_period = (repo_end_date - settlement).days
        return cls(settlement, maturity, coupon_perc, price_perc, frequency, basis, 
            repo_period, repo_rate_perc, futures_pr_perc, conversion_factor, type)
    
    def forward_price(self): 
        '''
        Calculate forward price. 

        Returns
        -------
        float
            A float which contains the forward price (in percent) of bond.
        
        Examples
        --------
        >>> bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        >>> bf_test.forward_price()
        113.45529615319292
        '''
        if self._type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        if self._forward_pr_perc:
            return self._forward_pr_perc
        forward_pr_reg = self._reg_dict["dirty_price"] *  (1 + self._reg_dict["repo_rate"] * self._repo_period / days_in_year)
        self._forward_pr_perc = forward_pr_reg * 100
        return self._forward_pr_perc
    
    def full_future_val(self):
        '''Calculate full future value.

        Returns
        -------
        float
            A float which contains the full future value (in percent) of bond.
        
        Examples
        --------
        >>> bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        >>> bf_test.full_future_val()
        113.444575
        '''
   
        if self._future_val_perc:
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
        '''Calculate net basis of bond future.

        Returns
        -------
        float
            A float which contains the net basis (in 32nd) of bond future.
        
        Examples
        --------
        >>> bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        >>> bf_test.net_basis()
        0.3430769021733795
        '''
        return (self.forward_price() - self.full_future_val()) * 32
    
    def implied_repo_rate(self): 
        '''Calculate implied repo rate.

        Returns
        -------
        float
            A float which contains the implied repo rate (in percent).
        
        Examples
        --------
        >>> bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        >>> bf_test.implied_repo_rate()
        0.09462834553701782
        '''
        if self._type == 'US':
            days_in_year = 360
        else:
            days_in_year = 365
        implied_repo_reg = (self.full_future_val() / self._perc_dict["dirty_price"] - 1) * days_in_year / self._repo_period
        return implied_repo_reg * 100

