from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
from scipy.optimize import root
from fincomepy.fixedincome import FixedIncome

class Bond(FixedIncome):
    '''
    A class used to perform bond related calculations.

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
    '''

    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis=1, redemption=100, yld=None):
        '''
        Constructor for Bond.

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
        redemption: float, optional
            A float which specifies bond redemption (in percent). 
            Default is 100.
        yld: float, optional
            A float which specifies bond yield (in percent). 
            Default is None.

        Examples
        --------
        >>> bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15),
            coupon_perc=0.625, price_perc=100.015625, frequency=2, basis=1)
        '''
        super().__init__()
        self._settlement = settlement
        self._maturity = maturity
        self._perc_dict["coupon"] = coupon_perc
        self._perc_dict["clean_price"] = self._parse_price(price_perc)
        self._frequency = frequency
        self._basis = basis
        self._redemption = redemption
        self._couppcd = Bond.couppcd(settlement, maturity, frequency, basis)
        self._coupncd = Bond.coupncd(settlement, maturity, frequency, basis)
        self._perc_dict["accrint"] = Bond.accrint(issue=self._couppcd, first_interest=self._coupncd, settlement=self._settlement,
            rate=self._perc_dict["coupon"], par=1, frequency=self._frequency, basis=self._basis)
        self._perc_dict["dirty_price"] = self._perc_dict["clean_price"] + self._perc_dict["accrint"]
        self.update_dict()
        self._yld = yld
        self._mac_duration = None
        self._mod_duration = None
        self._DV01 = None
        self._convexity = None
    
    @staticmethod
    def couppcd(settlement, maturity, frequency, basis):
        '''Get the previous coupon payment date.

        Parameters
        ----------
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        maturity: datetime.date
            A date object which specifies the maturity date of the bond.
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int
            An integer which indicates day count convention. 
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        
        Returns
        -------
        datetime.date
            The previous coupon payment date.
        
        Examples
        --------
        >>> pcd = Bond.couppcd(settlement=date(2020,7,15), maturity=date(2030,5,15), frequency=2, basis=1)
        >>> print(pcd) 
        2020-05-15
        '''
        coupon_interval = 12 / frequency
        nperiod = Bond.get_nperiod(settlement, maturity, coupon_interval)
        pcd = maturity - relativedelta(months=coupon_interval) * nperiod
        if maturity == Bond.last_day_in_month(maturity):
            return Bond.last_day_in_month(pcd)
        return pcd
    
    @staticmethod
    def coupncd(settlement, maturity, frequency, basis):
        '''Get the next coupon payment date.

        Parameters
        ----------
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        maturity: datetime.date
            A date object which specifies the maturity date of the bond.
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int
            An integer which indicates day count convention. 
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        
        Returns
        -------
        datetime.date
            The next coupon payment date.
        
        Examples
        --------
        >>> ncd = Bond.coupncd(settlement=date(2020,7,15), maturity=date(2030,5,15), frequency=2, basis=1)
        >>> print(ncd)
        2020-11-15
        '''
        coupon_interval = 12 / frequency
        nperiod = Bond.get_nperiod(settlement, maturity, coupon_interval)
        ncd = maturity - relativedelta(months=coupon_interval) * (nperiod - 1)
        if maturity == Bond.last_day_in_month(maturity):
            return Bond.last_day_in_month(ncd)
        return ncd
    
    @staticmethod
    def accrint(issue, first_interest, settlement, rate, par=1.0, frequency=2, basis=1):
        '''Calculate the accrued interest of coupon.

        Parameters
        ----------
        issue: datetime.date
            A date object which specifies the issue date of the bond.
        first_interest: datetime.date
            A date object which specifies the first interest payment date of the bond.
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        rate: float
            A float which indicates the coupon rate (in percent) of the bond.
        par: float
            A float which indicates the par of the bond.
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int, optional
            An integer which indicates day count convention. Default is 1.
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        
        Returns
        -------
        float
            The accured interest (in percent).
        
        Examples
        --------
        >>> accrued_int = Bond.accrint(issue=pcd, first_interest=ncd, 
            settlement=date(2020,7,15), rate=0.625, par=1, frequency=2, basis=1)
        >>> print(accrued_int)  
        0.10360054347826086
        '''
        if issue > first_interest:
            raise Exception('issue date cannot be later than first interest date.')
        if basis == 2:
            return (settlement - issue).days / 360 * rate
        if basis == 3:
            return (settlement - issue).days / 365 * rate
        if basis in [0, 4]:
            total_days = 360 / frequency
        else:
            total_days = Bond._day_count(issue, first_interest, basis)
        accrued_days = Bond._day_count(issue, settlement, basis)
        accrued_interest = (rate / frequency) * (accrued_days / total_days)
        return accrued_interest * par
    
    @staticmethod
    def _day_count(date1, date2, basis):
        if basis == 0:
            Y1, M1, D1 = date1.year, date1.month, date1.day
            Y2, M2, D2 = date2.year, date2.month, date2.day
            if date1 == Bond.last_day_in_month(date1) and date2 == Bond.last_day_in_month(date2) \
                and date1.month == 2 and date2.month == 2:
                D2 = 30
            if date1 == Bond.last_day_in_month(date1) and date1.month == 2:
                D1 = 30
            if D2 == 31 and (D1 == 30 or D1 == 31):
                D2 = 30
            if D1 == 31:
                D1 = 30
            return 360 * (Y2 - Y1) + 30 * (M2 - M1) + (D2 - D1)
        if basis == 4:
            D1, D2 = date1.day, date2.day
            if D1 == 31:
                D1 = 30
            if D2 == 31:
                D2 = 30
            return 360 * (date2.year - date1.year) + 30 * (date2.month - date1.month) + (D2 - D1)
        return (date2 - date1).days

    @staticmethod
    def dirty_price(settlement, maturity, rate, yld, redemption, frequency, basis):
        '''Calculate the dirty price of a bond.

        Parameters
        ----------
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        maturity: datetime.date
            A date object which specifies the maturity date of the bond.
        rate: float
            A float which indicates the coupon rate (in percent) of the bond.
        yld: float
            A float which specifies bond yield (in percent). 
        redemption: float
            A float which specifies bond redemption (in percent). 
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int
            An integer which indicates day count convention. 
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        
        Returns
        -------
        float
            The bond dirty price (in percent).
        
        Examples
        --------
        >>> # Given bond yield, calculate bond dirty price. Assuming yield is 0.6233%
        >>> dirty_price = Bond.dirty_price(settlement=date(2020,7,15), maturity=date(2030,5,15),
               rate=0.625, yld=0.6233, redemption=100, frequency=2, basis=1)
        >>> print(dirty_price)
        100.11968449222717
        '''
        pcd = Bond.couppcd(settlement, maturity, frequency, basis)
        ncd = Bond.coupncd(settlement, maturity, frequency, basis)
        first_period = Bond._first_period(pcd, ncd, settlement, frequency, basis)
        coupon_interval = 12 / frequency  
        nperiod = Bond.get_nperiod(settlement, maturity, coupon_interval)  
        periods = np.array([first_period + i for i in range(nperiod)])
        CF_perc = np.array([rate / frequency] * nperiod)
        CF_perc[-1] += redemption 
        CF_regular = CF_perc * 0.01
        yld_regular = yld * 0.01
        DF = 1 / (1 + yld_regular / frequency) ** periods
        CF_PV = CF_regular * DF
        CF_PV_total = sum(CF_PV)
        return CF_PV_total * 100  

    @staticmethod
    def _first_period(pcd, ncd, settlement, frequency, basis):
        if basis == 1:
            denom_days = (ncd - pcd).days
        elif basis in [0, 2, 4]:
            denom_days = 360 / frequency
        else:
            denom_days = 365 / frequency
        if basis in [1, 2, 3]:
            num_days = (ncd - settlement).days
        else:
            Y1, M1, D1 = settlement.year, settlement.month, settlement.day
            Y2, M2, D2 = ncd.year, ncd.month, ncd.day
            if settlement == Bond.last_day_in_month(settlement):
                D1 = 30
            if ncd == Bond.last_day_in_month(ncd):
                D2 = 30
            num_days = 360 * (Y2 - Y1) + 30 * (M2 - M1) + (D2 - D1)
        return num_days / denom_days

    @staticmethod
    def yld(settlement, maturity, rate, pr, redemption, frequency, basis, *args, **kwargs):
        '''Calculate the yield of a bond.

        Parameters
        ----------
        settlement: datetime.date
            A date object which specifies the bond settlement date of the bond.
        maturity: datetime.date
            A date object which specifies the maturity date of the bond.
        rate: float
            A float which indicates the coupon rate (in percent) of the bond.
        pr: float
            A float which specifies the clean price of the bond (in percent). 
        redemption: float
            A float which specifies bond redemption (in percent). 
        frequency: int
            An integer which specifies coupon payment frequency of the bond.
        basis: int
            An integer which indicates day count convention. 
            0: 30/360
            1: actual/actual
            2: actual/360
            3: actual/365
            4: 30E/360
        *args : optional
            Positional argument passed to scipy.optimize.root.
        **kwargs : optional
            Keyword argument passed to scipy.optimize.root. 
        
        Returns
        -------
        float
            The bond yield (in percent).
        
        Examples
        --------
        >>> yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2030,5,15), rate=0.625,
            pr=100.015625, redemption=100, frequency=2, basis=1)
        >>> print(yld)
        0.62334818110842
        '''
        pcd = Bond.couppcd(settlement, maturity, frequency, basis)
        ncd = Bond.coupncd(settlement, maturity, frequency, basis)
        accrued_interest = Bond.accrint(issue=pcd, first_interest=ncd, settlement=settlement, rate=rate, par=1, frequency=frequency, basis=basis)
        dirty_price_target = accrued_interest + pr
        sol = root(lambda x: Bond.dirty_price(settlement, maturity, rate, x, redemption, frequency, basis) - dirty_price_target, 
            [0.01], *args, **kwargs)
        yld = sol.x[0]
        assert yld >= 0 and yld <= 100
        return yld

    def _intermediate_values(self):
        coupon_interval = 12 / self._frequency  
        nperiod = Bond.get_nperiod(self._settlement, self._maturity, coupon_interval)
        first_period = Bond._first_period(self._couppcd, self._coupncd , self._settlement, self._frequency, self._basis)
        periods = np.array([first_period + i for i in range(nperiod)])
        CF_perc = np.array([self._perc_dict["coupon"] / self._frequency] * nperiod)
        CF_perc[-1] += self._redemption
        CF_regular = CF_perc * 0.01
        if self._yld is None:
            self._yld = self.yld(self._settlement, self._maturity, self._perc_dict["coupon"], self._perc_dict["clean_price"],
                                 self._redemption, self._frequency, self._basis)
        yield_regular = self._yld * 0.01
        DF = 1 / (1 + yield_regular / self._frequency) ** periods
        return (periods, CF_regular, DF)
    
    def mac_duration(self):
        '''Calculate the Macaulay duration of a bond.
        
        Returns
        -------
        float
            The Macaulay duration of a bond.
        
        Examples
        --------
        >>> bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15),
            coupon_perc=0.625, price_perc=100.015625, frequency=2, basis=1)
        >>> bond_test.mac_duration()
        9.543778095004477
        '''
        if self._mac_duration:
            return self._mac_duration
        periods, CF_regular, DF = self._intermediate_values()
        CF_PV = CF_regular * DF
        CF_PV_times_p = CF_PV * periods
        self._mac_duration = CF_PV_times_p.sum() / self._reg_dict["dirty_price"] / self._frequency
        return self._mac_duration

    def mod_duration(self, yld_change_perc=0.01):
        '''Calculate the modified duration of a bond.

        Parameters
        ----------
        yld_change_perc: float, optional
            A float which specifies the yield change when calculating modified duration.
            Default is 0.01.
        
        Returns
        -------
        float
            The modified duration of a bond.
        
        Examples
        --------
        >>> bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15),
            coupon_perc=0.625, price_perc=100.015625, frequency=2, basis=1)
        >>> bond_test.mod_duration()
        9.51412677103921
        '''
        if self._mod_duration:
            return self._mod_duration
        if not self._yld:
            original_yield_perc = self.yld(self._settlement, self._maturity, self._perc_dict["coupon"], self._perc_dict["clean_price"],
                                           self._redemption, self._frequency, self._basis)
        else:
            original_yield_perc = self._yld
        yield_up_perc = original_yield_perc + yld_change_perc
        yield_down_perc = original_yield_perc - yld_change_perc
        dirty_price_up_perc = self.dirty_price(self._settlement, self._maturity, self._perc_dict["coupon"], yield_up_perc,
                                               self._redemption, self._frequency, self._basis)  
        dirty_price_down_perc = self.dirty_price(self._settlement, self._maturity, self._perc_dict["coupon"], yield_down_perc,
                                               self._redemption, self._frequency, self._basis) 
        price_change_up_perc = dirty_price_up_perc - self._perc_dict["dirty_price"]
        price_change_down_perc = dirty_price_down_perc - self._perc_dict["dirty_price"]
        relative_change_up = price_change_up_perc / self._perc_dict["dirty_price"]
        relative_change_down = price_change_down_perc / self._perc_dict["dirty_price"]
        self._mod_duration = (abs(relative_change_up) + abs(relative_change_down)) / 2 / (yld_change_perc * 0.01) 
        return self._mod_duration
    
    def DV01(self):
        '''Calculate the DV01 of a bond.
        
        Returns
        -------
        float
            The DV01 of a bond.
        
        Examples
        --------
        >>> bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15),
            coupon_perc=0.625, price_perc=100.015625, frequency=2, basis=1)
        >>> bond_test.DV01()
        9.525470040389195
        '''
        if self._DV01:
            return self._DV01
        if self._mod_duration is None:
            self.mod_duration()
        self._DV01 = self._mod_duration * self._reg_dict["dirty_price"]
        return self._DV01
    
    def convexity(self):
        '''Calculate the convexity of a bond.
        
        Returns
        -------
        float
            The convexity of a bond.
        
        Examples
        --------
        >>> bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15),
            coupon_perc=0.625, price_perc=100.015625, frequency=2, basis=1)
        >>> bond_test.convexity()
        97.06268930241025
        '''
        if self._convexity:
            return self._convexity
        periods, CF_regular, DF = self._intermediate_values()
        CF_PV = CF_regular * DF
        CF_PV_times_p = CF_PV * periods
        CF_PV_times_p_2 = CF_PV * periods * periods
        all = (CF_PV_times_p + CF_PV_times_p_2) / self._reg_dict["dirty_price"]
        if not self._yld:
            self._yld = self.yld(self._settlement, self._maturity, self._perc_dict["coupon"], self._perc_dict["clean_price"],
                                 self._redemption, self._frequency, self._basis)
        yield_regular = self._yld * 0.01
        self._convexity = all.sum() / (4 * (1 + yield_regular / self._frequency) ** 2)
        return self._convexity
    
    def price_change(self, yld_change_perc):
        '''Calculate the bond price change based on yield change.

        Parameters
        ----------
        yld_change_perc: float
            A float which specifies the yield change when calculating bond price change.
        
        Returns
        -------
        float
            The price change of a bond.
        
        Examples
        --------
        >>> bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15),
            coupon_perc=0.625, price_perc=100.015625, frequency=2, basis=1)
        >>> # For 0.1% change in yield, the bond price will change by:    
        >>> bond_test.price_change(yld_change_perc=0.1)
        -0.9476880833978572
        '''
        DV01 = self.DV01()
        convexity = self.convexity()
        yld_change_reg = yld_change_perc * 0.01
        price_change_reg = (-1) * DV01 * yld_change_reg + self._reg_dict["dirty_price"] * convexity / 2 * (yld_change_reg ** 2)
        return price_change_reg * 100
            
    @staticmethod
    def diff_month(date1, date2):
        '''Get the month difference between two dates.

        Parameters
        ----------
        date1: datetime.date
            First date.
        date2: datetime.date
            Second date.
        
        Returns
        -------
        int
            Difference in months between date1 and date2.
        '''
        return (date2.year - date1.year) * 12 + date2.month - date1.month
    
    @staticmethod
    def last_day_in_month(original_date):
        '''Get the last day for the input month.

        Parameters
        ----------
        original_date: datetime.date
            Input date.
        
        Returns
        -------
        datetime.date
            The last date in the input month.
        '''
        next_month = original_date.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    @staticmethod
    def _parse_price(pr):
        if not isinstance(pr, (int, float, str)):
            raise Exception('price should be int, float, or str.')
        if isinstance(pr, (int, float)):
            return pr
        quotelist = pr.split('-')
        assert len(quotelist) <= 2
        quotelist = [item.strip() for item in quotelist]
        if len(quotelist) == 1:
            return int(quotelist[0])
        firstnum = quotelist[0]
        secondnum = quotelist[1]
        if secondnum.endswith('+'):
            return int(firstnum) + (int(secondnum[:-1]) + 0.5) / 32
        return int(firstnum) + int(secondnum) / 32

    def coupon_dates(self):
        '''Obtain the coupon payment dates of a bond.

        Returns
        -------
        list
            A list of coupon payment dates.
        '''
        coupon_interval = 12 / self._frequency
        periods = Bond.get_nperiod(self._settlement, self._maturity, coupon_interval)
        coupon_dates = [self._maturity - relativedelta(months=coupon_interval) * i for i in range(periods)]
        if self._maturity == Bond.last_day_in_month(self._maturity):
            coupon_dates = [Bond.last_day_in_month(item) for item in coupon_dates]
        return coupon_dates

    @staticmethod
    def get_nperiod(settlement, maturity, coupon_interval):
        assert settlement < maturity
        nperiod = 0
        while maturity - relativedelta(months=coupon_interval) * nperiod > settlement:
            nperiod += 1
        return nperiod


