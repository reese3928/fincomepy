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

Assuing we have a 5-year bond with 3% annual coupon. Suppose the 1-5 year zero-coupon rates are 1%, 1.5038%, 1.8085%, 2.0652%, and 2.2199% respectively. i.e.

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
zspread_obj.get_zspread()
```

Visualize the z-spread:
```{python}
zspread_obj.plot_zspread()
```

![image](docs/zspread_plot.png)


### Z-spread calculation from par coupon bond

Assuing we have a 5-year bond with 3% annual coupon. Suppose the 1-5 year par-coupon rates are 1%, 1.5%, 1.8%, 2.05%, and 2.2% respectively. i.e.

|   Maturity |   Par Coupon Rate |   Coupon Cash Flow |
|-----------:|------------------:|-------------------:|
|          1 |              1.0% |               3.0% |
|          2 |              1.5% |               3.0% |
|          3 |              1.8% |               3.0% |
|          4 |             2.05% |               3.0% |
|          5 |              2.2% |             103.0% |

Obtain z-spread:
```{python}
zspread_obj2 = ZspreadPar(par_rates, coupon_cf)
zspread_obj2.get_zspread()
```

### Bond price, yield and other related calculations

Suppose we have a bond with following information.

|                  |   Bond Info |
|:-----------------|------------:|
| Settlement       |   2020-7-15 |
| Maturidy         |   2030-5-15 |
| Coupon           |      0.625% |
| Market Price     | 100.015625% |
| Coupon Frequency |           2 |
| Basis            |           1 |

* Previous coupon payment date (EXCEL equivalent of COUPPCD):

```{python}
pcd = Bond.couppcd(settlement=date(2020,7,15), maturity=date(2030,5,15), frequency=2, basis=1)
print(pcd) 
```

* Next coupon payment date (EXCEL equivalent of COUPNCD):
```{python}
ncd = Bond.coupncd(settlement=date(2020,7,15), maturity=date(2030,5,15), frequency=2, basis=1)
print(ncd)
```

* Accrued interest (EXCEL equivalent of ACCRINT)

```{python} 
accrued_int = Bond.accrint(issue=pcd, first_interest=ncd, 
   settlement=date(2020,7,15), rate=0.625, par=1, frequency=2, basis=1)
print(accrued_int)  
```  

* Bond dirty price (EXCEL equivalent of PRICE)
```{python}
# Given bond yield, calculate bond dirty price. Assuming yield is 0.6233%
dirty_price = Bond.dirty_price(settlement=date(2020,7,15), maturity=date(2030,5,15),
      rate=0.625, yld=0.6233, redemption=100, frequency=2, basis=1)
print(dirty_price)
```      

* Bond yield (EXCEL equivalent of YIELD)
```{python}
yld = Bond.yld(settlement=date(2020,7,15), maturity=date(2030,5,15), rate=0.625,
   pr=100.015625, redemption=100, frequency=2, basis=1)
```

```{python} 
    def mod_duration(self, yld_change_perc=0.01):
       
    
    def DV01(self):
     
    
    def convexity(self):
      
    
    def price_change(self, yld_change_perc):
       
   

    @staticmethod
    def parse_price(pr):
     

    
```

TO DO: add basis

### Repo start payment, end payment, and break even yield
### Bond future's net basis and implied repo rate
### CDS spread