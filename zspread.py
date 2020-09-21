import numpy as np
from scipy.optimize import root

def perc_to_regular(percentage_values):
    return percentage_values*0.01

def regular_to_perc(regular_values):
    return regular_values*100

def total_CF_zspread(zspread, zero_rates_regular, CF_regular, maturity):
    CF_each_period = CF_regular/(1 + zero_rates_regular + zspread)**maturity
    return np.sum(CF_each_period)

def zSpread_from_zero_rates(zero_rates_perc, CF_perc, maturity=None):
    if maturity is None:
        maturity = np.arange(zero_rates_perc.size) + 1
    zero_rates_regular = perc_to_regular(zero_rates_perc)
    CF_regular = perc_to_regular(CF_perc)
    sol = root(lambda x: total_CF_zspread(x, zero_rates_regular, CF_regular, maturity) - 1.0, [0.0] )
    return regular_to_perc(sol.x)

def zSpread_from_par_rates(par_rates_perc, CF_perc, price_perc=100, face_value_perc=100, compound="discrete"):
    price_regular = perc_to_regular(price_perc)
    face_value_regular = perc_to_regular(face_value_perc)
    maturity = np.arange(par_rates_perc.size) + 1
    par_rates_regular = perc_to_regular(par_rates_perc)
    discount_factor = []
    discount_factor.append(face_value_regular/((face_value_regular) + par_rates_regular[0]))
    for i in range(1, par_rates_regular.size):
        df = (price_regular - par_rates_regular[i]*sum(discount_factor))/(face_value_regular + par_rates_regular[i])
        discount_factor.append(df)
    discount_factor = np.array(discount_factor)
    if compound == "discrete":
        zero_rates_regular = (1/discount_factor)**(1/maturity) - 1
    else:
        zero_rates_regular = -np.log(discount_factor)/maturity
    zero_rates_perc = regular_to_perc(zero_rates_regular)  ## TO DO: remove this regular to percentage exchange
    return zSpread_from_zero_rates(zero_rates_perc, CF_perc, maturity=maturity)
    

par_rates = np.array([1.00, 1.50, 1.80, 2.05, 2.20])
zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])

res = zSpread_from_zero_rates(zero_discrete, coupon_cf)
print(res)

res = zSpread_from_par_rates(par_rates, coupon_cf)
print(res)


par_rates = np.array([2.67, 2.80, 2.92, 3.03, 3.13, 3.22, 3.29, 3.35, 3.40, 3.44])
coupon_cf = np.array([4.0]*9 + [104.0])
res = zSpread_from_par_rates(par_rates, coupon_cf)
print(res)