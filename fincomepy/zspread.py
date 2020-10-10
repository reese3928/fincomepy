import numpy as np
from scipy.optimize import root
import matplotlib.pyplot as plt
from fincomepy.fixedincome import FixedIncome

class ZspreadZero(FixedIncome):
    def __init__(self, zero_rates_perc, CF_perc, face_value_perc=100, maturity=None):
        super().__init__()
        self._perc_dict["zero_rates"] = zero_rates_perc
        self._perc_dict["CF"] = CF_perc
        self._perc_dict["face_value"] = face_value_perc
        if maturity is None:
            self._maturity = np.arange(self._perc_dict["zero_rates"].size) + 1
        else:
            self._maturity = maturity
        self.update_dict()
    
    @property
    def zspread(self):
        if "zspread" in self._perc_dict.keys():
            return self._perc_dict["zspread"]
        return self.calc_zspread_from_zero()

    def calc_zspread_from_zero(self):
        ## TO DO: add solver as an option
        sol = root(lambda x: self.total_CF_zspread(x, self._reg_dict["zero_rates"], self._reg_dict["CF"], 
                   self._maturity) - self._reg_dict["face_value"], [0.01] )
        zspread = sol.x[0]
        assert zspread >= 0 and zspread <=1
        self._reg_dict["zspread"] = zspread
        self.update_dict()
        return self._perc_dict["zspread"]

    def plot_zspread(self, maturity=None, zero_rates_perc=None, zspread=None):
        if maturity is None:
            maturity = self._maturity
        if zero_rates_perc is None:
            zero_rates_perc = self._perc_dict["zero_rates"]
        if zspread is None:
            zspread = self.zspread
        plt.plot(maturity, zero_rates_perc, label="Zero-Coupon Rates")
        plt.plot(maturity, zspread + zero_rates_perc, label="Bond Pricing Rates")
        plt.xlabel("Maturity")
        plt.ylabel(r"Rates(%)")
        plt.legend()
    
    @staticmethod
    def total_CF_zspread(zspread, zero_rates_regular, CF_regular, maturity):
        CF_each_period = CF_regular/ (1 + zero_rates_regular + zspread) ** maturity
        return np.sum(CF_each_period)


class ZspreadPar(ZspreadZero):
    def __init__(self, par_rates_perc, CF_perc, face_value_perc=100, compound="discrete", maturity=None):
        FixedIncome.__init__(self)
        self._perc_dict["par_rates"] = par_rates_perc
        self._perc_dict["CF"] = CF_perc
        self._perc_dict["face_value"] = face_value_perc
        self._compound = compound
        if maturity is None:
            self._maturity = np.arange(self._perc_dict["par_rates"].size) + 1
        else:
            self._maturity = maturity
        self._discount_factor = None
        self.update_dict()
    
    @property
    def zspread(self):
        if "zspread" in self._perc_dict.keys():
            return self._perc_dict["zspread"]
        return self.calc_zspread_from_par()
    
    def calc_zspread_from_par(self):
        discount_factor = []
        discount_factor.append(self._reg_dict["face_value"] / (self._reg_dict["face_value"] + self._reg_dict["par_rates"][0]))
        for i in range(1, self._reg_dict["par_rates"].size):
            df = (self._reg_dict["face_value"] - self._reg_dict["par_rates"][i] * sum(discount_factor)) / \
                 (self._reg_dict["face_value"] + self._reg_dict["par_rates"][i])
            discount_factor.append(df)
        discount_factor = np.array(discount_factor)
        self._discount_factor = discount_factor
        if self._compound == "discrete":
            self._reg_dict["zero_rates"] = (1/discount_factor)**(1/self._maturity) - 1
        else:
            self._reg_dict["zero_rates"] = -np.log(discount_factor)/self._maturity
        self.calc_zspread_from_zero()
        return self._perc_dict["zspread"]


