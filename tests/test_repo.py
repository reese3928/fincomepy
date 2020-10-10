import unittest
from datetime import date, timedelta
from fincomepy import Repo

class Test(unittest.TestCase):

    def test_return_values(self):
        repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
            price_perc=(99+30/32), frequency=2, basis=1, 
            bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
        self.assertTrue(abs(repo_test._perc_dict["accrint"] - 0.1036) < 0.0001)
        self.assertTrue(abs(repo_test._perc_dict["repo_rate"] - 0.145) < 1e-6)
        self.assertTrue(abs(repo_test.start_payment() - 100041100.54) < 0.01)
        self.assertTrue(abs(repo_test.end_payment() - 100041503.49) < 0.01)

        repo_test = Repo(settlement=date(2020,7,16), maturity=date(2030,5,15), coupon_perc=0.625, 
            price_perc=99.953125, frequency=2, basis=1, 
            bond_face_value=100000000, repo_period=32, repo_rate_perc=0.145)
        self.assertTrue(abs(repo_test._perc_dict["accrint"] - 0.1053) < 0.0001)
        self.assertTrue(abs(repo_test.start_payment() - 100058423.91) < 0.01)
        self.assertTrue(abs(repo_test.end_payment() - 100071320.33) < 0.01)
        self.assertTrue(abs(repo_test.break_even_yld() - 0.6343) < 0.01)
        self.assertTrue(abs(repo_test.purchase_pr_with_margin(102) - 98096494.03) < 0.01)
        self.assertTrue(abs(repo_test.purchase_pr_with_haircut(2) - 98057255.43) < 0.01)

        repo_test = Repo(settlement=date(2020,7,17), maturity=date(2028,10,22), coupon_perc= (1 + 5/8), 
            price_perc=113.321, frequency=2, basis=1, 
            bond_face_value=100000000, repo_period=276, repo_rate_perc=0.575, type='UK')
        self.assertTrue(abs(repo_test.start_payment() - 113702830.60) < 0.01)
        self.assertTrue(abs(repo_test.end_payment() - 113382413.14) < 0.01)
    
    def test_from_end_date(self):
        repo_test = Repo(settlement=date(2020,7,17), maturity=date(2028,10,22), coupon_perc= (1 + 5/8), 
            price_perc=113.321, frequency=2, basis=1, 
            bond_face_value=100000000, repo_period=276, repo_rate_perc=0.575, type='UK')
        repo_test2 = Repo.from_end_date(settlement=date(2020,7,17), maturity=date(2028,10,22), coupon_perc= (1 + 5/8), 
            price_perc=113.321, frequency=2, basis=1, 
            bond_face_value=100000000, repo_end_date=date(2021, 4, 19), repo_rate_perc=0.575, type='UK')
        self.assertEqual(repo_test._perc_dict["accrint"], repo_test2._perc_dict["accrint"])
        self.assertEqual(repo_test.start_payment(), repo_test2.start_payment())
        self.assertEqual(repo_test.end_payment(), repo_test2.end_payment())

if __name__ == '__main__':
    unittest.main()


