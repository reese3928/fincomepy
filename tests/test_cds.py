import unittest
import numpy as np
from fincomepy import CDS

class Test(unittest.TestCase):

    def test_return_values(self):
        cds_test = CDS(np.array([5.0]*10), np.array([5.95]*10), face_value_perc=100, rr_perc=50)
        res = cds_test.cds_spread()
        self.assertEqual(res.size, 10)
        self.assertAlmostEqual(res[0], 0.8966, places=3)
        self.assertTrue(abs(res - 0.8966).mean() < 0.0001)

        cds_test2 = CDS.from_bond_spread(np.array([5.0]*10), np.array([0.95]*10), face_value_perc=100, rr_perc=50)
        res2 = cds_test2.cds_spread()
        self.assertTrue(abs(res - res2).mean() < 1e-6)


if __name__ == '__main__':
    unittest.main()
