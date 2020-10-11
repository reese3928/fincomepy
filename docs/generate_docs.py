import pandas as pd
import os
from fincomepy import ZspreadZero
import numpy as np
import matplotlib.pyplot as plt
import sys

df = pd.DataFrame.from_dict({
    "Maturity": [1, 2, 3, 4, 5],
    "Zero Coupon Rate": [1.0, 1.5038, 1.8085, 2.0652, 2.2199],
    "Coupon Cash Flow": [3.0, 3.0, 3.0, 3.0, 103.0]
    })
df["Zero Coupon Rate"] = df["Zero Coupon Rate"].astype(str)
df["Zero Coupon Rate"] += "%"
df["Coupon Cash Flow"] = df["Coupon Cash Flow"].astype(str)
df["Coupon Cash Flow"] += "%"
df = df[["Maturity", "Zero Coupon Rate", "Coupon Cash Flow"]]
df.set_index("Maturity", inplace=True)
df.to_csv(os.path.join("docs", "zspread_from_zero.csv"))
with open('docs/zspread_from_zero.md', 'w') as f:
    print(df.to_markdown(colalign=("right", "right", "right")), file=f)

zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
zspread_obj = ZspreadZero(zero_discrete, coupon_cf) 
zspread_obj.calc_zspread_from_zero()
zspread_obj.plot_zspread()
plt.savefig(os.path.join("docs", "zspread_plot.png"))
plt.close()


