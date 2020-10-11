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

* [Xu Ren](https://github.com/reese3928) (xuren2120@gmail.com)

Usage
----------

### Z-spread calculation from zero coupon bond

Assuing we have a 5-year bond with 3% annual coupon. Suppose the 1-5 year zero coupon rates are 1%, 1.5038%, 1.8085%, 2.0652%, and 2.2199% respectively. i.e.

|   Maturity |   Zero Coupon Rate |   Coupon Cash Flow |
|-----------:|-------------------:|-------------------:|
|          1 |               1.0% |               3.0% |
|          2 |            1.5038% |               3.0% |
|          3 |            1.8085% |               3.0% |
|          4 |            2.0652% |               3.0% |
|          5 |            2.2199% |             103.0% |

To calculate z-spread, first construct a ZspreadZero object:
```{python}
zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
zspread_obj = ZspreadZero(zero_discrete, coupon_cf) 
```

Obtain z-spread:
```{python}
zspread_obj.calc_zspread_from_zero()
```

Visualize the z-spread:
```{python}
zspread_obj.plot_zspread()
```

![image](docs/zspread_plot.png)



