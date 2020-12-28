import pandas as pd
from datetime import datetime
from flask import request 

def get_bond_info():
    settlement = datetime.strptime(request.form['settlement'], '%Y-%m-%d').date()
    maturity = datetime.strptime(request.form['maturity'], '%Y-%m-%d').date()
    coupon_perc = float(request.form['coupon_perc'])
    price_perc = float(request.form['price_perc'])
    frequency = int(request.form['frequency'])
    basis = int(request.form['basis'])
    return (settlement, maturity, coupon_perc, price_perc, frequency, basis)

def get_repo_info():
    repo_period = int(request.form['repo_period'])
    repo_rate_perc = float(request.form['repo_rate_perc'])
    type = request.form['type']
    return (repo_period, repo_rate_perc, type)

def get_bond_series(settlement, maturity, coupon_perc, price_perc, frequency, basis):
    return pd.Series({
        "Settlement Date": str(settlement),
        "Maturity Date": str(maturity),
        "Coupon": str(coupon_perc) + '%',
        "Market Price": str(price_perc) + '%',
        "Coupon Frequency": str(frequency),
        "Basis": str(basis),
    })

def process_df(attributes1, attributes2):
    df1 = attributes1.to_frame().reset_index()
    df2 = attributes2.to_frame().reset_index()
    res = pd.concat([df1, df2], axis=1)
    res.columns = ["Attributes1", "Workout1", "Attributes2", "Workout2"]
    return res