import unittest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import math
import sys
from scipy.optimize import root
sys.path.append("fincomepy")  ## TO DO: change this
from fincomepy import BondFuture

class Test(unittest.TestCase):

    def test_return_values(self):
        bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        self.assertTrue(abs(bf_test._perc_dict["accrint"] - 0.4066) < 0.0001)
        self.assertTrue(abs(bf_test._perc_dict["repo_rate"] - 0.14) < 1e-6)
        self.assertTrue(abs(bf_test.forward_price() - 113.455) < 0.001)
        
    

if __name__ == '__main__':
    unittest.main()


