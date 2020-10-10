import unittest
from datetime import date, timedelta
from fincomepy import Bond

class Test(unittest.TestCase):

    def test_return_values(self):
        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(100+0.5/32), frequency=2, basis=1)
        self.assertEqual(bond_test._couppcd, date(2020, 5, 15))
        self.assertEqual(bond_test._coupncd, date(2020, 11, 15))
        self.assertTrue(abs(bond_test._perc_dict["accrint"] - 0.1036) < 0.0001)
        self.assertTrue(abs(bond_test._perc_dict["dirty_price"] - 100.1192) < 0.0001)
        dirty_price = Bond.dirty_price(settlement=date(2020,7,15), maturity=date(2030,5,15),
                      rate=0.625, yld=0.62334818, redemption=100, frequency=2, basis=1)
        self.assertTrue(abs(dirty_price - 100.1192) < 0.0001)
        yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2030,5,15), rate=0.625,
                    pr=(100+0.5/32), redemption=100, frequency=2, basis=1)
        self.assertTrue(abs(yld - 0.6233) < 0.0001)
        yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2030,5,15), rate=0.625,
                    pr=(100+0.5/32), redemption=105, frequency=2, basis=1)
        self.assertTrue(abs(yld - 1.1060) < 0.0001)
        self.assertTrue(bond_test._mac_duration is None)
        self.assertTrue(bond_test._yld is None)
        self.assertTrue(abs(bond_test.mac_duration() - 9.5437) < 0.0001)
        self.assertFalse(bond_test._mac_duration is None)
        self.assertFalse(bond_test._yld is None)
        # test price_change
        self.assertTrue(abs(bond_test.price_change(yld_change_perc=0.1) - (-0.9477)) < 0.0001)

        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2025,6,30), coupon_perc=0.25, 
                 price_perc=(99+26/32), frequency=2, basis=1)
        yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2025,6,30), rate=0.25, 
                 pr=(99+26/32), redemption=100, frequency=2, basis=1)
        self.assertTrue(abs(yld - 0.2881) < 0.0001)
        self.assertTrue(abs(bond_test._perc_dict["accrint"] - 0.0102 < 0.0001))
        self.assertTrue(abs(bond_test.mac_duration() - 4.9312 < 0.0001))
        self.assertTrue(bond_test._mod_duration is None)
        self.assertTrue(abs(bond_test.mod_duration() - 4.9241 < 0.0001))
        self.assertFalse(bond_test._mod_duration is None)
        self.assertTrue(bond_test._DV01 is None)
        self.assertTrue(abs(bond_test.DV01() - 4.9154 < 0.0001))
        self.assertFalse(bond_test._DV01 is None)
        self.assertTrue(bond_test._convexity is None)
        self.assertTrue(abs(bond_test.convexity() - 26.8053 < 0.0001))
        self.assertFalse(bond_test._convexity is None)

        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2022,6,30), coupon_perc=1/8, 
                 price_perc=(99+30/32), frequency=2, basis=1)
        self.assertTrue(abs(bond_test._perc_dict["accrint"] - 0.0051 < 0.0001))
        self.assertTrue(abs(bond_test.mac_duration() - 1.9574 < 0.0001))
        self.assertTrue(abs(bond_test.mod_duration() - 1.9558 < 0.0001))
        self.assertTrue(abs(bond_test.DV01() - 1.9547 < 0.0001))
        self.assertTrue(abs(bond_test.convexity() - 4.8053 < 0.0001))
        self.assertTrue(abs(bond_test._yld - 0.1569 < 0.0001))

        # Bond.accrint(issue=bond_test._couppcd, first_interest=bond_test._coupncd, settlement=bond_test._settlement, 
        #     rate=0.625, par=100, frequency=2, basis=1)

        # bond_test = Bond(date(2010,10,10), date(2016,1,7), 4.75, 1, 1)
        # bond_test._coupon_interval
        # bond_test._nperiod
        # bond_test._coupon_dates
        # bond_test._couppcd
        # bond_test._coupncd

    def test_couppcd(self):
        pcd = Bond.couppcd(settlement=date(2020,7,15), maturity=date(2030,5,15), frequency=2, basis=1)
        self.assertEqual(pcd, date(2020, 5, 15))
        ncd = Bond.coupncd(settlement=date(2020,7,15), maturity=date(2030,5,15), frequency=2, basis=1)
        self.assertEqual(ncd, date(2020, 11, 15))
        accrued_interest = Bond.accrint(issue=pcd, first_interest=ncd, settlement=date(2020,7,15),
                                        rate=0.625, par=1, frequency=2, basis=1)
        self.assertTrue(abs(accrued_interest - 0.1036) < 0.0001)
    
    def test_parse_price(self):
        bond_test1 = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(100+0.5/32), frequency=2, basis=1)
        bond_test2 = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc="100-00+", frequency=2, basis=1)
        self.assertEqual(bond_test1._perc_dict["clean_price"], bond_test2._perc_dict["clean_price"])
        bond_test1 = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=100, frequency=2, basis=1)
        bond_test2 = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc="100", frequency=2, basis=1)
        self.assertEqual(bond_test1._perc_dict["clean_price"], bond_test2._perc_dict["clean_price"])
        bond_test1 = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(99+26/32), frequency=2, basis=1)
        bond_test2 = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc="99-26", frequency=2, basis=1)
        self.assertEqual(bond_test1._perc_dict["clean_price"], bond_test2._perc_dict["clean_price"])

    def test_invalid_input(self):
        with self.assertRaises(Exception):
            Bond.accrint(issue=date(2020, 11, 15), first_interest=date(2020, 5, 15), 
                         settlement=date(2020,7,15), rate=0.625, par=1, frequency=2, basis=1)
        with self.assertRaises(Exception):
            Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=[100+0.5/32], frequency=2, basis=1)
    
    def test_day_count(self):
        settlement = date(2020,7,15)
        maturity = date(2025, 3, 20)
        coupon = 0.25
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.07948 < 1e-5))
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertTrue(abs(value0 - 0.07986 < 1e-5))
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.08125 < 1e-5))
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.08014 < 1e-5))
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.07986 < 1e-5))

        maturity = date(2025, 3, 31)
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.07240 < 1e-5))
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertTrue(abs(value0 - 0.07292 < 1e-5))
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.07361 < 1e-5))
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.07260 < 1e-5))
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.07292 < 1e-5))

        maturity = date(2025, 6, 30)
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.01019 < 1e-5))
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertTrue(abs(value0 - 0.01042 < 1e-5))
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.01042 < 1e-5))
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.01027 < 1e-5))
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.01042 < 1e-5))

        settlement = date(2020,7,15)
        maturity = date(2028, 2, 29)
        coupon = 0.25
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.09307< 1e-5))
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertTrue(abs(value0 - 0.09375 < 1e-5))
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.09514 < 1e-5))
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.09384 < 1e-5))
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.09444 < 1e-5))

        settlement = date(2020,7,15)
        maturity = date(2025, 3, 20)
        coupon = 0.25
        market_pr = 99.8125
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.2903438 < 1e-7))
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertTrue(abs(value1 - 0.2903567 < 1e-7))
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.2904045 < 1e-7))
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.2904045 < 1e-7))
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.2904045 < 1e-7))

        maturity = date(2025, 3, 31)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.2901024 < 1e-7))
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertTrue(abs(value1 - 0.2901198 < 1e-7))
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.2901433 < 1e-7))
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.2901433 < 1e-7))
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.2901433 < 1e-7))

        maturity = date(2025, 3, 31)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.2901024 < 1e-7))
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertTrue(abs(value1 - 0.2901198 < 1e-7))
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.2901433 < 1e-7))
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.2901433 < 1e-7))
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.2901433 < 1e-7))

        maturity = date(2025, 6, 30)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.2881048 < 1e-7))
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertTrue(abs(value1 - 0.2881117 < 1e-7))
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.2881117 < 1e-7))
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.2881117 < 1e-7))
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.2881117 < 1e-7))

        maturity = date(2028, 2, 29)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertTrue(abs(value1 - 0.2748547 < 1e-7))
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertTrue(abs(value1 - 0.2748635 < 1e-7))
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertTrue(abs(value2 - 0.2748815 < 1e-7))
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertTrue(abs(value3 - 0.2748815 < 1e-7))
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertTrue(abs(value4 - 0.2748815 < 1e-7))
        

if __name__ == '__main__':
    unittest.main()