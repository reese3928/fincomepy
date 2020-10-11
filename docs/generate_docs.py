import pandas as pd
import os

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
df.to_csv(os.path.join("docs", "zspread_from_zero.csv"), index=False)



