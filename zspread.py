import numpy as np
from scipy.optimize import root
import matplotlib.pyplot as plt

class FixedIncome(object):
    def __init__(self):
        return
    
    @staticmethod
    def perc_to_regular(percentage_values):
        return percentage_values*0.01

    @staticmethod
    def regular_to_perc(regular_values):
        return regular_values*100
    

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
        zero_rates_regular = self.perc_to_regular(self._zero_rates_perc)
        CF_regular = self.perc_to_regular(self._CF_perc)
        ## TO DO: add solver as an option
        sol = root(lambda x: self.total_CF_zspread(x, zero_rates_regular, CF_regular, self._maturity) - 1.0, [0.0] )
        zspread = sol.x
        assert zspread >= 0 and zspread <=1
        self._zspread_perc = self.regular_to_perc(sol.x)

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
        price_regular = self.perc_to_regular(self._price_perc)
        face_value_regular = self.perc_to_regular(self._face_value_perc)
        par_rates_regular = self.perc_to_regular(self._par_rates_perc)
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
        self._zero_rates_perc = self.regular_to_perc(zero_rates_regular)  ## TO DO: remove this regular to percentage exchange
        self.calc_zspread_from_zero()



    
par_rates = np.array([1.00, 1.50, 1.80, 2.05, 2.20])
zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])

obj = ZspreadZero(zero_discrete, coupon_cf)
obj.calc_zspread_from_zero()
print(obj._zspread_perc)


obj = ZspreadPar(par_rates, coupon_cf)
obj.calc_zspread_from_par()
print(obj._zspread_perc)
    
par_rates = np.array([2.67, 2.80, 2.92, 3.03, 3.13, 3.22, 3.29, 3.35, 3.40, 3.44])
coupon_cf = np.array([4.0]*9 + [104.0])
obj2 = ZspreadPar(par_rates, coupon_cf)
obj2.calc_zspread_from_par()
print(obj2._zspread_perc)
obj2.plot_zspread()
plt.show()


