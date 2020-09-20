import numpy as np
from scipy.optimize import root

def perc_to_regular(percentage_values):
    return percentage_values*0.01

def regular_to_perc(regular_values):
    return regular_values*100

def total_CF_zspread(x, ori_rates_regular, CF_regular, maturity):
    CF_each_period = CF_regular/(1 + ori_rates_regular + x)**maturity
    return np.sum(CF_each_period)


def zSpread(original_rates, CF):
    maturity = np.arange(original_rates.size) + 1
    ori_rates_regular = perc_to_regular(original_rates)
    CF_regular = perc_to_regular(CF)
    sol = root(lambda x: total_CF_zspread(x, ori_rates_regular, CF_regular, maturity) - 1.0, [0.0] )
    return regular_to_perc(sol.x)


zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])

res = zSpread(zero_discrete, coupon_cf)
print(res)




