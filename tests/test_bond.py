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


if __name__ == '__main__':
    unittest.main()