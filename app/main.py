from flask import Flask, render_template, url_for, request 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
from fincomepy import *
## TO DO: change this fincomepy to local 
## TO DO: check if different product can be put into separate python files
## TO DO: test the app on goole cloud
## TO DO: test the package on windows (check if makefile, config still works)
## TO DO: add download to result table and figure
## TO DO: put bond.html, repo.html ... to products folder

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/analysis")
def analysis():
    return render_template('analysis.html')

@app.route("/bond", methods=['GET', 'POST'])
def bond():
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
        render_template('bond.html', res=res)
    return render_template('bond.html', res=res)

## TO DO: if haircut is set then block margin
@app.route("/repo", methods=['GET', 'POST'])
def repo():
    res = pd.DataFrame(columns = ["Attributes1", "Workout1","Attributes2", "Workout2"])
    res["Attributes1"] = ["Settlement Date", "Maturity Date", "Coupon", "Market Price", "Coupon Frequency", "Basis", "Face Value"]
    res["Workout1"] = ""
    res["Attributes2"] = ["Repo Start Date", "Repo Period", "Repo End Date", "Money Market", "Purchase Price", "End Payment", "Break Even Yield"]
    res["Workout2"] = ""
    if request.method == 'POST':
        # get input
        settlement = datetime.strptime(request.form['settlement'], '%Y-%m-%d').date()
        maturity = datetime.strptime(request.form['maturity'], '%Y-%m-%d').date()
        coupon_perc = float(request.form['coupon_perc'])
        price_perc = float(request.form['price_perc'])
        frequency = int(request.form['frequency'])
        basis = int(request.form['basis'])
        bond_face_value = float(request.form['bond_face_value'])
        repo_period = int(request.form['repo_period'])
        repo_rate_perc = float(request.form['repo_rate_perc'])
        type = request.form['type']

        # construct a repo object
        repo_obj = Repo(settlement=settlement, maturity=maturity, coupon_perc=coupon_perc, 
            price_perc=price_perc, frequency=frequency, basis=basis,
            bond_face_value=bond_face_value, repo_period=repo_period, 
            repo_rate_perc=repo_rate_perc, type=type)
        # create result data frame
        attributes1 = pd.Series({
            "Settlement Date": str(settlement),
            "Maturity Date": str(maturity),
            "Coupon": str(coupon_perc) + '%',
            "Market Price": str(price_perc) + '%',
            "Coupon Frequency": str(frequency),
            "Basis": str(basis),
            "Face Value": str(bond_face_value)
        })
        attributes2 = pd.Series({
            "Repo Start Date": str(settlement),
            "Repo Period": str(repo_period),
            "Repo End Date": str(repo_obj._repo_end_date),
            "Money Market": type,
            "Purchase Price": str(round(repo_obj.start_payment(), 2)),
            "End Payment": str(round(repo_obj.end_payment(), 2)),
            "Break Even Yield": str(round(repo_obj.break_even_yld(), 4)),
        })
        attributes1 = attributes1.to_frame().reset_index()
        attributes2 = attributes2.to_frame().reset_index()
        res = pd.concat([attributes1, attributes2], axis=1)
        res.columns = ["Attributes1", "Workout1", "Attributes2", "Workout2"]
        render_template('repo.html', res=res)
    return render_template('repo.html', res=res)

if __name__ == '__main__':
    app.run(debug=True)
