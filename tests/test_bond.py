import unittest
from datetime import date, timedelta
from fincomepy import Bond

class Test(unittest.TestCase):

    def test_return_values(self):
        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(100+0.5/32), frequency=2, basis=1)
        self.assertEqual(bond_test._couppcd, date(2020, 5, 15))
        self.assertEqual(bond_test._coupncd, date(2020, 11, 15))
        self.assertAlmostEqual(bond_test._perc_dict["accrint"], 0.1036, places=4)
        self.assertAlmostEqual(bond_test._perc_dict["dirty_price"], 100.1192, places=4)
        dirty_price = Bond.dirty_price(settlement=date(2020,7,15), maturity=date(2030,5,15),
                      rate=0.625, yld=0.62334818, redemption=100, frequency=2, basis=1)
        self.assertAlmostEqual(dirty_price, 100.1192, places=4)
        yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2030,5,15), rate=0.625,
                    pr=(100+0.5/32), redemption=100, frequency=2, basis=1)
        self.assertAlmostEqual(yld, 0.6233, places=4)
        yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2030,5,15), rate=0.625,
                    pr=(100+0.5/32), redemption=105, frequency=2, basis=1)
        self.assertAlmostEqual(yld, 1.1060, places=4)
        self.assertTrue(bond_test._mac_duration is None)
        self.assertTrue(bond_test._yld is None)
        self.assertAlmostEqual(bond_test.mac_duration(), 9.5437, places=3)
        self.assertFalse(bond_test._mac_duration is None)
        self.assertFalse(bond_test._yld is None)
        # test price_change
        self.assertAlmostEqual(bond_test.price_change(yld_change_perc=0.1), -0.9477, places=4)

        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2025,6,30), coupon_perc=0.25, 
                 price_perc=(99+26/32), frequency=2, basis=1)
        yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2025,6,30), rate=0.25, 
                 pr=(99+26/32), redemption=100, frequency=2, basis=1)
        self.assertAlmostEqual(yld, 0.2881, places=4)
        self.assertAlmostEqual(bond_test._perc_dict["accrint"], 0.0102, places=4)
        self.assertAlmostEqual(bond_test.mac_duration(), 4.9312, places=4)
        self.assertTrue(bond_test._mod_duration is None)
        self.assertAlmostEqual(bond_test.mod_duration(), 4.9241, places=4)
        self.assertFalse(bond_test._mod_duration is None)
        self.assertTrue(bond_test._DV01 is None)
        self.assertAlmostEqual(bond_test.DV01(), 4.9154, places=4)
        self.assertFalse(bond_test._DV01 is None)
        self.assertTrue(bond_test._convexity is None)
        self.assertAlmostEqual(bond_test.convexity(), 26.8053, places=1)
        self.assertFalse(bond_test._convexity is None)

        bond_test = Bond(settlement=date(2020,7,15), maturity=date(2022,6,30), coupon_perc=1/8, 
                 price_perc=(99+30/32), frequency=2, basis=1)
        self.assertAlmostEqual(bond_test._perc_dict["accrint"], 0.0051, places=4)
        self.assertAlmostEqual(bond_test.mac_duration(), 1.9574, places=4)
        self.assertAlmostEqual(bond_test.mod_duration(), 1.9558, places=4)
        self.assertAlmostEqual(bond_test.DV01(), 1.9547, places=4)
        self.assertAlmostEqual(bond_test.convexity(), 4.8053, places=2)
        self.assertAlmostEqual(bond_test._yld, 0.1569, places=3)

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
        self.assertAlmostEqual(accrued_interest, 0.1036, places=4)

        bonds = [
            {
                "settlement": date(2020,8,10), "maturity": date(2046,8,15), "frequency": 2, "basis": 1,
                "pcd": date(2020, 2, 15), "ncd": date(2020, 8, 15)
            },
            {
                "settlement": date(2020,8,10), "maturity": date(2046,8,15), "frequency": 1, "basis": 1,
                "pcd": date(2019, 8, 15), "ncd": date(2020, 8, 15)
            },
            {
                "settlement": date(2020,8,15), "maturity": date(2046,8,15), "frequency": 2, "basis": 1,
                "pcd": date(2020, 8, 15), "ncd": date(2021, 2, 15)
            },
            {
                "settlement": date(2020,8,15), "maturity": date(2046,8,15), "frequency": 1, "basis": 1,
                "pcd": date(2020, 8, 15), "ncd": date(2021, 8, 15)
            },
            {
                "settlement": date(2020,8,15), "maturity": date(2046,8,31), "frequency": 2, "basis": 1,
                "pcd": date(2020, 2, 29), "ncd": date(2020, 8, 31)
            },
            {
                "settlement": date(2020,8,15), "maturity": date(2046,8,31), "frequency": 1, "basis": 1,
                "pcd": date(2019, 8, 31), "ncd": date(2020, 8, 31)
            },
            {
                "settlement": date(2020,8,31), "maturity": date(2046,8,31), "frequency": 2, "basis": 1,
                "pcd": date(2020, 8, 31), "ncd": date(2021, 2, 28)
            },
            {
                "settlement": date(2020,8,31), "maturity": date(2046,8,31), "frequency": 1, "basis": 1,
                "pcd": date(2020, 8, 31), "ncd": date(2021, 8, 31)
            },
            {
                "settlement": date(2020,8,17), "maturity": date(2050,8,15), "frequency": 2, "basis": 1,
                "pcd": date(2020, 8, 15), "ncd": date(2021, 2, 15)
            },
            {
                "settlement": date(2020,8,17), "maturity": date(2050,8,15), "frequency": 1, "basis": 1,
                "pcd": date(2020, 8, 15), "ncd": date(2021, 8, 15)
            },
            {
                "settlement": date(2050,8,14), "maturity": date(2050,8,15), "frequency": 2, "basis": 1,
                "pcd": date(2050, 2, 15), "ncd": date(2050, 8, 15)
            },
            {
                "settlement": date(2050,8,14), "maturity": date(2050,8,15), "frequency": 1, "basis": 1,
                "pcd": date(2049, 8, 15), "ncd": date(2050, 8, 15)
            }
        ]

        for bond in bonds:
            pcd = Bond.couppcd(settlement=bond["settlement"], maturity=bond["maturity"], 
                frequency=bond["frequency"], basis=bond["basis"])
            self.assertEqual(pcd, bond["pcd"])
            ncd = Bond.coupncd(settlement=bond["settlement"], maturity=bond["maturity"], 
                frequency=bond["frequency"], basis=bond["basis"])
            self.assertEqual(ncd, bond["ncd"])
            bond_obj = Bond(settlement=bond["settlement"], maturity=bond["maturity"], coupon_perc=1.375, 
                price_perc=99.8, frequency=bond["frequency"], basis=bond["basis"], redemption=100)
            coupon_dts = bond_obj.coupon_dates()
            self.assertEqual(bond["ncd"], coupon_dts[-1])

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
        self.assertAlmostEqual(value1, 0.07948, places=5)
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.07986, places=5)
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.08125, places=5)
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.08014, places=5)
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.07986, places=5)

        maturity = date(2025, 3, 31)
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.07240, places=5)
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.07292, places=5)
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.07361, places=5)
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.07260, places=5)
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.07292, places=5)

        maturity = date(2025, 6, 30)
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.01019, places=5)
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.01042, places=5)
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.01042, places=5)
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.01027, places=5)
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.01042, places=5)

        settlement = date(2020,7,15)
        maturity = date(2028, 2, 29)
        coupon = 0.25
        pcd = Bond.couppcd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        ncd = Bond.coupncd(settlement=settlement, maturity=maturity, frequency=2, basis=1)
        value1 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.09307, places=5)
        value0 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.09375, places=5)
        value2 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.09514, places=5)
        value3 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.09384, places=5)
        value4 = Bond.accrint(pcd, ncd, settlement, coupon, par=1, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.09444, places=5)

        settlement = date(2020,7,15)
        maturity = date(2025, 3, 20)
        coupon = 0.25
        market_pr = 99.8125
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.2903438, places=7)
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.2903567, places=7)
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.2897113, places=7)
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.2901097, places=7)
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.2903567, places=7)

        maturity = date(2025, 3, 31)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.2901024, places=7)
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.2901198, places=7)
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.2896270, places=7)
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.2900242, places=7)
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.2901198, places=7)

        maturity = date(2025, 6, 30)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.2881048, places=7)
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.2881117, places=7)
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.287, places=3)
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.288, places=3)
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.2881117, places=7)

        maturity = date(2028, 2, 29)
        value1 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=1)
        self.assertAlmostEqual(value1, 0.2748547, places=7)
        value0 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=0)
        self.assertAlmostEqual(value0, 0.2748635, places=7)
        value2 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=2)
        self.assertAlmostEqual(value2, 0.274, places=3)
        value3 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=3)
        self.assertAlmostEqual(value3, 0.275, places=3)
        value4 = Bond.yld(settlement, maturity, coupon, market_pr, 100, frequency=2, basis=4)
        self.assertAlmostEqual(value4, 0.275, places=3)
        

if __name__ == '__main__':
    unittest.main()