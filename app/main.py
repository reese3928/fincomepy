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

        # TO DO: make input on the left side, output on the right side
        res = bond_obj.mac_duration()
        return render_template('analysis.html', res=res)
    return render_template('analysis.html')



if __name__ == '__main__':
    app.run(debug=True)
