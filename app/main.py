from flask import Flask, render_template, url_for, request 
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about", methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        number1 = float(request.form['number1'])
        number2 = float(request.form['number2'])
        res = number1 * number2
        return render_template('home.html', res=res)
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)
