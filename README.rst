==========
fincomepy
==========

A set of tools to perform fixed income securities related calculation in Python. Products covered:

* Z-spread calculation from zero coupon bond
* Z-spread calculation from par coupon bond
* Bond price, yield and other related calculations
* Repo start payment, end payment, and break even yield
* Bond future's net basis and implied repo rate
* CDS spread

Author
----------

* `Xu Ren <https://github.com/reese3928>`__ <xuren2120@gmail.com>

Usage
----------

Z-spread calculation from zero coupon bond
###########################################

.. csv-table::
   :widths: 20, 40, 40
   :header-rows: 1
   :align: right
    
    Maturity,Zero Coupon Rate,Coupon Cash Flow
    1,1.0%,3.0%
    2,1.5038%,3.0%
    3,1.8085%,3.0%
    4,2.0652%,3.0%
    5,2.2199%,103.0%





We use the following code::

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



Still under development    

Contribution is welcomed

