from main import app
from flask import render_template

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("inicio.html")
