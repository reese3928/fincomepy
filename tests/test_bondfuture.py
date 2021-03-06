import unittest
from datetime import date, timedelta
from fincomepy import BondFuture

class Test(unittest.TestCase):

    def test_return_values(self):
        bf_test = BondFuture(settlement=date(2020,7,17), maturity=date(2027,5,15), coupon_perc=2.375, 
            price_perc=113.015625, frequency=2, basis=1, 
            repo_period=75, repo_rate_perc=0.14, futures_pr_perc=139.4375, conversion_factor=0.8072)
        self.assertAlmostEqual(bf_test._perc_dict["accrint"], 0.4066, places=3)
        self.assertAlmostEqual(bf_test._perc_dict["repo_rate"], 0.14, places=5)
        self.assertAlmostEqual(bf_test.forward_price(), 113.455, places=2)
        self.assertAlmostEqual(bf_test.full_future_val(), 113.444575, places=5)
        self.assertAlmostEqual(bf_test.net_basis(), 0.343, places=2)
        self.assertAlmostEqual(bf_test.implied_repo_rate(), 0.09463, places=4)

        bf_test = BondFuture(settlement=date(2014,1,29), maturity=date(2025,3,7), coupon_perc=5.00, 
            price_perc=119.795, frequency=2, basis=1, 
            repo_period=152, repo_rate_perc=0.588, futures_pr_perc=108.44, 
            conversion_factor=1.086725, type='UK')
        self.assertAlmostEqual(bf_test._perc_dict["accrint"], 1.9889, places=3)
        self.assertAlmostEqual(bf_test.forward_price(), 122.082, places=2)
        self.assertAlmostEqual(bf_test.full_future_val(), 121.911591, places=5)
        self.assertAlmostEqual(bf_test.net_basis()/32, 0.171, places=2)
        self.assertAlmostEqual(bf_test.implied_repo_rate(), 0.252, places=2)

        bf_test = BondFuture(settlement=date(2014,1,29), maturity=date(2023,9,7), coupon_perc=2.25, 
            price_perc=95.355, frequency=2, basis=1, 
            repo_period=152, repo_rate_perc=0.588, futures_pr_perc=108.44, 
            conversion_factor=0.8655782, type='UK')
        self.assertAlmostEqual(bf_test._perc_dict["accrint"], 0.8950, places=3)
        self.assertAlmostEqual(bf_test.forward_price(), 96.486, places=2)
        self.assertAlmostEqual(bf_test.full_future_val(), 95.693509, places=5)
        self.assertAlmostEqual(bf_test.net_basis()/32, 0.792, places=2)
        self.assertAlmostEqual(bf_test.implied_repo_rate(), -1.388, places=2)

if __name__ == '__main__':
    unittest.main()


