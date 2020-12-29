from flask import Flask, render_template, url_for, request 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
from helper import get_bond_info, get_repo_info, get_bond_series, process_df
import sys
sys.path.append('../fincomepy')
from fincomepy import Bond, Repo, BondFuture, ZspreadPar, ZspreadZero, CDS
## TO DO: future work: add download to result table and figure
## TO DO: add instruction for the input excel file in zero coupon spread

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
        settlement, maturity, coupon_perc, price_perc, frequency, basis = get_bond_info()
        # construct a bond object
        bond_obj = Bond(settlement=settlement, maturity=maturity, coupon_perc=coupon_perc, 
            price_perc=price_perc, frequency=frequency, basis=basis)
        # create result data frame
        attributes1 = get_bond_series(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        attributes1[""] = ""
        attributes2 = pd.Series({
            "Accrued Interest": str(round(bond_obj._perc_dict["accrint"], 4)) + '%',
            "Dirty Price": str(round(bond_obj._perc_dict["dirty_price"], 4)) + '%',
            "Yield": str(round(Bond.yld(settlement, maturity, coupon_perc, price_perc, 100, frequency, basis), 4)) + '%',
            "Macaulay Duration": str(round(bond_obj.mac_duration(), 3)),
            "Modified Duration": str(round(bond_obj.mod_duration(), 3)),
            "DV01": str(round(bond_obj.DV01(), 3)),
            "Convexity": str(round(bond_obj.convexity(), 3))
        })
        res = process_df(attributes1, attributes2)
        render_template('bond.html', res=res, bf=False)
    return render_template('bond.html', res=res, bf=False)

@app.route("/repo", methods=['GET', 'POST'])
def repo():
    res = pd.DataFrame(columns = ["Attributes1", "Workout1","Attributes2", "Workout2"])
    res["Attributes1"] = ["Settlement Date", "Maturity Date", "Coupon", "Market Price", "Coupon Frequency", "Basis", "Face Value"]
    res["Workout1"] = ""
    res["Attributes2"] = ["Repo Rate", "Repo Period", "Repo End Date", "Money Market", "Purchase Price", "End Payment", "Break Even Yield"]
    res["Workout2"] = ""
    if request.method == 'POST':
        # get input
        settlement, maturity, coupon_perc, price_perc, frequency, basis = get_bond_info()
        bond_face_value = float(request.form['bond_face_value'])
        repo_period, repo_rate_perc, type = get_repo_info()
        # construct a repo object
        repo_obj = Repo(settlement=settlement, maturity=maturity, coupon_perc=coupon_perc, 
            price_perc=price_perc, frequency=frequency, basis=basis,
            bond_face_value=bond_face_value, repo_period=repo_period, 
            repo_rate_perc=repo_rate_perc, type=type)
        # create result data frame
        attributes1 = get_bond_series(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        attributes1["Face Value"] = str(bond_face_value)
        attributes2 = pd.Series({
            "Repo Rate": str(repo_rate_perc) + '%',
            "Repo Period": str(repo_period),
            "Repo End Date": str(repo_obj._repo_end_date),
            "Money Market": type,
            "Purchase Price": str(round(repo_obj.start_payment(), 2)),
            "End Payment": str(round(repo_obj.end_payment(), 2)),
            "Break Even Yield": str(round(repo_obj.break_even_yld(), 4)),
        })
        res = process_df(attributes1, attributes2)
        render_template('repo.html', res=res, bf=False)
    return render_template('repo.html', res=res, bf=False)

@app.route("/bond_future", methods=['GET', 'POST'])
def bond_future():
    res = pd.DataFrame(columns = ["Attributes1", "Workout1","Attributes2", "Workout2"])
    res["Attributes1"] = ["Settlement Date", "Maturity Date", "Coupon", "Market Price", "Coupon Frequency", 
        "Basis", "Repo Rate", "Repo Period", "Repo End Date", "Money Market", "Forward Price", ""]
    res["Workout1"] = ""
    res["Attributes2"] = ["Last Delievery Date", "Maturity Date", "Previous Coupon Date", "Next Coupon Date", "Futures Price", 
        "Conversion Factor", "Invoice Price", "Accrued at Delievery", "Full Futures Value", "Arbitrage PL", "Net Basis", "Implied Repo"]
    res["Workout2"] = ""
    if request.method == 'POST':
        # get input
        settlement, maturity, coupon_perc, price_perc, frequency, basis = get_bond_info()
        repo_period, repo_rate_perc, type = get_repo_info()
        futures_pr_perc = float(request.form['futures_pr_perc'])
        conversion_factor = float(request.form['conversion_factor'])
        # construct a bond future object
        bf_obj = BondFuture(settlement=settlement, maturity=maturity, coupon_perc=coupon_perc, 
            price_perc=price_perc, frequency=frequency, basis=basis, repo_period=repo_period, 
            repo_rate_perc=repo_rate_perc, futures_pr_perc=futures_pr_perc,
            conversion_factor=conversion_factor, type=type)
        # create result data frame
        attributes1 = get_bond_series(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        attributes1["Repo Rate"] = str(repo_period)
        attributes1["Repo Period"] = str(repo_period)
        attributes1["Repo End Date"] = str(bf_obj._repo_end_date)
        attributes1["Money Market"] = type
        attributes1["Forward Price"] = str(round(bf_obj.forward_price(), 4)) 
        attributes1[""] = ""
        # calculate accrued interest
        accrint_perc = Bond.accrint(bf_obj._couppcd, bf_obj._coupncd, bf_obj._repo_end_date, 
                bf_obj._perc_dict["coupon"], 1, frequency, basis)
        attributes2 = pd.Series({
            "Last Delievery Date": str(bf_obj._repo_end_date),
            "Maturity Date": str(maturity), 
            "Previous Coupon Date": str(bf_obj._couppcd), 
            "Next Coupon Date": str(bf_obj._coupncd), 
            "Futures Price": str(futures_pr_perc) + '%', 
            "Conversion Factor": str(conversion_factor), 
            "Invoice Price": str(round(bf_obj._invoice_pr_perc, 4)) + '%', 
            "Accrued at Delievery": str(round(accrint_perc, 4)) + '%', 
            "Full Futures Value": str(round(bf_obj.full_future_val(), 4)) + '%', 
            "Arbitrage PL": str(round(bf_obj.full_future_val() - bf_obj.forward_price(), 4)) + '%', 
            "Net Basis": str(round(bf_obj.net_basis(), 4)), 
            "Implied Repo": str(round(bf_obj.implied_repo_rate(), 4)) + '%'
        })
        res = process_df(attributes1, attributes2)
        render_template('bond_future.html', res=res, bf=True)
    return render_template('bond_future.html', res=res, bf=True)

@app.route("/zspread", methods=['GET', 'POST'])
def zspread(): 
    return render_template('zspread.html')

## TO DO: future work, check if zspread_par.html and zspread_zero.html can be combined together
@app.route("/zspread_zero", methods=['GET', 'POST'])
def zspread_zero():
    res1 = ""
    if request.method == 'POST':
        df = pd.read_csv(request.files['zero_coupon_df'])
        face_value_perc = float(request.form['face_value_perc'])
        zspr_obj1 = ZspreadZero(df.iloc[:,0].values, df.iloc[:,1].values, face_value_perc) 
        res1 = str(round(zspr_obj1.get_zspread(), 4))
        render_template('zspread_zero.html', res=res1)      
    return render_template('zspread_zero.html', res=res1)

@app.route("/zspread_par", methods=['GET', 'POST'])
def zspread_par():
    res1 = ""
    if request.method == 'POST':
        df = pd.read_csv(request.files['par_coupon_df'])
        face_value_perc = float(request.form['face_value_perc'])
        zspr_obj1 = ZspreadPar(df.iloc[:,0].values, df.iloc[:,1].values, face_value_perc) 
        res1 = str(round(zspr_obj1.get_zspread(), 4))
        render_template('zspread_par.html', res=res1)      
    return render_template('zspread_par.html', res=res1)

@app.route("/cds", methods=['GET', 'POST'])
def cds():
    res = pd.DataFrame(columns = ["Maturity", "CDS"])
    if request.method == 'POST':
        df = pd.read_csv(request.files['cds_input_df'])
        face_value_perc = float(request.form['face_value_perc'])
        rr_perc = float(request.form['rr_perc'])
        cds_obj = CDS(df.iloc[:,1].values, df.iloc[:,2].values, face_value_perc, rr_perc, df.iloc[:,0].values)
        cds_array = cds_obj.cds_spread()
        res = pd.DataFrame.from_dict({
            "Maturity": df.iloc[:,0].values,
            "CDS": [str(round(item, 4)) + '%' for item in cds_array]
        }) 
        return render_template('cds.html', res=res)      
    return render_template('cds.html', res=res)


if __name__ == '__main__':
    app.run(debug=True)
