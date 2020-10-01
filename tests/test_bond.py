import unittest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
from scipy.optimize import root
import sys
sys.path.append("fincomepy")  ## TO DO: change this
from fincomepy import Bond

class Test(unittest.TestCase):

    def test_return_values(self):
        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(100+0.5/32), frequency=2, basis=1)
        self.assertTrue(abs(bond_test._coupon_interval - 6.0) < 0.00001)
        self.assertEqual(bond_test._couppcd, date(2020, 5, 15))
        self.assertEqual(bond_test._couppcd, date(2020, 11, 15))
        self.assertTrue(abs(bond_test._accrint - 0.1036) < 0.0001)
        self.assertTrue(abs(bond_test._dirty_price_perc - 100.1192) < 0.0001)
        self.assertTrue(abs(bond_test.price(0.62334818) - 100.1192) < 0.0001)
        self.assertTrue(abs(bond_test.get_yield() - 0.6233) < 0.0001)
        self.assertTrue(abs(bond_test.get_mac_duration() - 9.5437) < 0.0001)

        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2025,6,30), coupon_perc=0.25, 
                 price_perc=(99+26/32), frequency=2, basis=1)
        self.assertTrue(abs(bond_test.get_yield() - 0.2881) < 0.0001)
        self.assertTrue(abs(bond_test._accrint - 0.0102 < 0.0001))
        self.assertTrue(abs(bond_test.get_mac_duration() - 4.9312 < 0.0001))
        self.assertTrue(abs(bond_test.get_mod_duration() - 4.9241 < 0.0001))
        self.assertTrue(abs(bond_test.get_DV01() - 4.9154 < 0.0001))
        self.assertTrue(abs(bond_test.get_convexity() - 26.8053 < 0.0001))

        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2022,6,30), coupon_perc=1/8, 
                 price_perc=(99+30/32), frequency=2, basis=1)
        self.assertTrue(abs(bond_test.get_yield() - 0.1569 < 0.0001))
        self.assertTrue(abs(bond_test._accrint - 0.0051 < 0.0001))
        self.assertTrue(abs(bond_test.get_mac_duration() - 1.9574 < 0.0001))
        self.assertTrue(abs(bond_test.get_mod_duration() - 1.9558 < 0.0001))
        self.assertTrue(abs(bond_test.get_DV01() - 1.9547 < 0.0001))
        self.assertTrue(abs(bond_test.get_convexity() - 4.8053 < 0.0001))

        Bond.accrint(issue=bond_test._couppcd, first_interest=bond_test._coupncd, settlement=bond_test._settlement, 
             rate=0.625, par=100, frequency=2, basis=1)

bond_test = Bond(date(2010,10,10), date(2016,1,7), 4.75, 1, 1)
bond_test._coupon_interval
bond_test._nperiod
bond_test._coupon_dates
bond_test._couppcd
bond_test._coupncd



        
    
    #def test_zspread_property(self):
        


if __name__ == '__main__':
    unittest.main()