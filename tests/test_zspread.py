import unittest
import numpy as np
from fincomepy import ZspreadZero, ZspreadPar

class Test(unittest.TestCase):

    def test_return_values(self):
        par_rates = np.array([1.00, 1.50, 1.80, 2.05, 2.20])
        zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
        coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        obj = ZspreadZero(zero_discrete, coupon_cf) 
        obj.calc_zspread_from_zero()
        self.assertTrue(abs(obj.calc_zspread_from_zero() - 0.807) < 0.001)
        self.assertTrue(abs(obj._perc_dict["zspread"] - 0.807) < 0.001)
        self.assertTrue(abs(obj.zspread - 0.807) < 0.001)

        obj2 = ZspreadPar(par_rates, coupon_cf)
        obj2.calc_zspread_from_par()
        self.assertTrue(abs(obj2._perc_dict["zspread"] - 0.807) < 0.001)
    
        par_rates = np.array([2.67, 2.80, 2.92, 3.03, 3.13, 3.22, 3.29, 3.35, 3.40, 3.44])
        coupon_cf = np.array([4.0]*9 + [104.0])
        obj3 = ZspreadPar(par_rates, coupon_cf)
        obj3.calc_zspread_from_par()
        self.assertTrue(abs(obj3._perc_dict["zspread"] - 0.566) < 0.001)
        #obj3.plot_zspread()
        #plt.show()
    
    def test_zspread_property(self):
        zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
        coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        obj = ZspreadZero(zero_discrete, coupon_cf) 
        self.assertFalse("zspread" in obj._perc_dict.keys())
        self.assertFalse("zspread" in obj._reg_dict.keys())
        self.assertTrue(abs(obj.zspread - 0.807) < 0.001)
        self.assertTrue("zspread" in obj._perc_dict.keys())
        self.assertTrue("zspread" in obj._reg_dict.keys())

        par_rates = np.array([2.67, 2.80, 2.92, 3.03, 3.13, 3.22, 3.29, 3.35, 3.40, 3.44])
        coupon_cf = np.array([4.0]*9 + [104.0])
        obj2 = ZspreadPar(par_rates, coupon_cf)
        self.assertFalse("zspread" in obj2._perc_dict.keys())
        self.assertFalse("zspread" in obj2._reg_dict.keys())
        self.assertTrue(abs(obj2.zspread - 0.566) < 0.001)
        self.assertTrue("zspread" in obj2._perc_dict.keys())
        self.assertTrue("zspread" in obj2._reg_dict.keys())


if __name__ == '__main__':
    unittest.main()