import numpy as np
from scipy.optimize import root
import matplotlib.pyplot as plt
import sys
sys.path.append(".")  ## TO DO: check if this is can be added to __init__.py
from fixedincome import FixedIncome

class ZspreadZero(FixedIncome):
    def __init__(self, zero_rates_perc, CF_perc, maturity=None):
        self._zero_rates_perc = zero_rates_perc
        self._CF_perc = CF_perc
        if maturity is None:
            self._maturity = np.arange(self._zero_rates_perc.size) + 1
        else:
            self._maturity = maturity
        self._zspread_perc = None
    
    def calc_zspread_from_zero(self):
        zero_rates_regular = FixedIncome.perc_to_regular(self._zero_rates_perc)
        CF_regular = FixedIncome.perc_to_regular(self._CF_perc)
        ## TO DO: add solver as an option
        sol = root(lambda x: self.total_CF_zspread(x, zero_rates_regular, CF_regular, self._maturity) - 1.0, [0.01] )
        zspread = sol.x
        assert zspread >= 0 and zspread <=1
        self._zspread_perc = FixedIncome.regular_to_perc(sol.x)

    def plot_zspread(self):
        plt.plot(self._maturity, self._zero_rates_perc, label="Zero-Coupon Rates")
        plt.plot(self._maturity, self._zspread_perc + self._zero_rates_perc, label="Bond Pricing Rates")
        plt.xlabel("Maturity")
        plt.ylabel(r"Rates(%)")
        plt.legend()
    
    @staticmethod
    def total_CF_zspread(zspread, zero_rates_regular, CF_regular, maturity):
        CF_each_period = CF_regular/(1 + zero_rates_regular + zspread)**maturity
        return np.sum(CF_each_period)


class ZspreadPar(ZspreadZero):
    def __init__(self, par_rates_perc, CF_perc, price_perc=100, face_value_perc=100, compound="discrete", maturity=None):
        self._par_rates_perc = par_rates_perc
        self._CF_perc = CF_perc
        self._price_perc = price_perc
        self._face_value_perc = face_value_perc
        self._compound = compound
        if maturity is None:
            self._maturity = np.arange(self._par_rates_perc.size) + 1
        else:
            self._maturity = maturity
        self._discount_factor = None
    
    def calc_zspread_from_par(self):
        price_regular = FixedIncome.perc_to_regular(self._price_perc)
        face_value_regular = FixedIncome.perc_to_regular(self._face_value_perc)
        par_rates_regular = FixedIncome.perc_to_regular(self._par_rates_perc)
        discount_factor = []
        discount_factor.append(face_value_regular/((face_value_regular) + par_rates_regular[0]))
        for i in range(1, par_rates_regular.size):
            df = (price_regular - par_rates_regular[i]*sum(discount_factor))/(face_value_regular + par_rates_regular[i])
            discount_factor.append(df)
        discount_factor = np.array(discount_factor)
        self._discount_factor = discount_factor
        if self._compound == "discrete":
            zero_rates_regular = (1/discount_factor)**(1/self._maturity) - 1
        else:
            zero_rates_regular = -np.log(discount_factor)/self._maturity
        self._zero_rates_perc = FixedIncome.regular_to_perc(zero_rates_regular)  ## TO DO: remove this regular to percentage exchange
        self.calc_zspread_from_zero()

