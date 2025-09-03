from flask import Flask, jsonify, render_template
from qkd_backend.qkd_runner import exp1, exp2, exp3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run/exp1")
def run_experiment1():
    result = exp1.run_exp1()   # calls your Python function
    return jsonify(result)

@app.route("/run/exp2")
def run_experiment2():
    result = exp2.run_exp2()
    return jsonify(result)

@app.route("/run/exp3")
def run_experiment3():
    result = exp3.run_exp3()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
