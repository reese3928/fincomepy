from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
import math

class FixedIncome(object):
    def __init__(self):
        return
    
    @staticmethod
    def perc_to_regular(percentage_values):
        return percentage_values*0.01

    @staticmethod
    def regular_to_perc(regular_values):
        return regular_values*100

class Bond(FixedIncome):
    def __init__(self, settlement, maturity, frequency, basis=1):
        self._settlement = settlement
        self._maturity = maturity
        self._frequency = frequency
        self._basis = basis
        self._coupon_interval = 12 / frequency
        self._periods = math.floor((self.diff_month(self._settlement, self._maturity))/self._coupon_interval)
        self._coupon_dates = [self._maturity - relativedelta(months=self._coupon_interval)*i for i in range(self._periods + 1)]
        self._couppcd = self._coupon_dates[-1] - relativedelta(months=self._coupon_interval)
        self._coupncd = self._coupon_dates[-1]

    @staticmethod
    def diff_month(date1, date2):
        print((date2.year - date1.year) * 12 + date2.month - date1.month)
        return (date2.year - date1.year) * 12 + date2.month - date1.month



bond_test = Bond(date(2010,10,10), date(2016,1,7), 2, 1)
bond_test._coupon_interval
bond_test._periods
bond_test._coupon_dates
bond_test._couppcd
bond_test._coupncd

bond_test = Bond(date(2010,10,10), date(2016,1,7), 1, 1)
bond_test._coupon_interval
bond_test._periods
bond_test._coupon_dates
bond_test._couppcd
bond_test._coupncd



