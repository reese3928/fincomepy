from flask import Flask, render_template, url_for, request 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
from fincomepy import *
## TO DO: change this fincomepy to local 
## TO DO: check if different product can be put into separate python files
## TO DO: test the app on goole cloud

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/analysis", methods=['GET', 'POST'])
def analysis():
    res = pd.DataFrame(columns = ["Attributes1", "Workout1","Attributes2", "Workout2"])
    res["Attributes1"] = ["Settlement Date", "Maturity Date", "Coupon", "Market Price", "Coupon Frequency", "Basis", ""]
    res["Workout1"] = ""
    res["Attributes2"] = ["Accrued Interest", "Dirty Price", "Yield", "Macaulay Duration", "Modified Duration", "DV01", "Convexity"]
    res["Workout2"] = ""
    if request.method == 'POST':
        # get input
        settlement = datetime.strptime(request.form['settlement'], '%Y-%m-%d').date()
        maturity = datetime.strptime(request.form['maturity'], '%Y-%m-%d').date()
        coupon_perc = float(request.form['coupon_perc'])
        price_perc = float(request.form['price_perc'])
        frequency = int(request.form['frequency'])
        basis = int(request.form['basis'])
        # construct a bond object
        bond_obj = Bond(settlement=settlement, maturity=maturity, coupon_perc=coupon_perc, 
            price_perc=price_perc, frequency=frequency, basis=basis)
        # create result data frame
        attributes1 = pd.Series({
            "Settlement Date": str(settlement),
            "Maturity Date": str(maturity),
            "Coupon": str(coupon_perc) + '%',
            "Market Price": str(price_perc) + '%',
            "Coupon Frequency": str(frequency),
            "Basis": str(basis),
            "":""
        })
        attributes2 = pd.Series({
            "Accrued Interest": str(round(bond_obj._perc_dict["accrint"], 4)) + '%',
            "Dirty Price": str(round(bond_obj._perc_dict["dirty_price"], 4)) + '%',
            "Yield": str(round(Bond.yld(settlement, maturity, coupon_perc, price_perc, 100, frequency, basis), 4)) + '%',
            "Macaulay Duration": str(round(bond_obj.mac_duration(), 3)),
            "Modified Duration": str(round(bond_obj.mod_duration(), 3)),
            "DV01": str(round(bond_obj.DV01(), 3)),
            "Convexity": str(round(bond_obj.convexity(), 3))
        })
        attributes1 = attributes1.to_frame().reset_index()
        attributes2 = attributes2.to_frame().reset_index()
        res = pd.concat([attributes1, attributes2], axis=1)
        res.columns = ["Attributes1", "Workout1", "Attributes2", "Workout2"]
        render_template('analysis.html', res=res)
    return render_template('analysis.html', res=res)

if __name__ == '__main__':
    app.run(debug=True)
