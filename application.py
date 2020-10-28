import os

import requests
import urllib.parse
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from functools import wraps

#from helpers import apology, login_required, lookup, usd

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/LogIn")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

db = SQL("sqlite:///user.db")

@app.route("/")
@login_required
def layout():
    return render_template("layout.html")

def is_provided(field):
    if not request.form.get(field):
        return False

@app.route("/SignUp", methods=["GET", "POST"])
def SignUp():
    if request.method == "POST":
        try:
            prim_key = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",username=request.form.get("username"),hash=request.form.get("password"))
        except:
            flash("Username already exists")
            return redirect("/SignUp")
        session["user_id"] = prim_key
        flash("Registration was successful")
        return redirect("/")
    else:
        return render_template("SignUp.html")


@app.route("/LogIn", methods=["GET", "POST"])
def LogIn():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            return redirect("/")
        rows = db.execute("SELECT * FROM users WHERE username = :username AND hash = :hash",username=request.form.get("username"),hash=request.form.get("password"))
        if len(rows) == 0:
            return redirect("/LogIn")
        session["user_id"] = rows[0]["id"]
        flash("Login was successful")
        return redirect("/")
    else:
        return render_template("LogIn.html")


@app.route("/<modalIDD>")
@login_required
def modalIDD(modalIDD):
    rows = db.execute("SELECT place,email,tel,address FROM newModal WHERE modalID=(?)",(modalIDD))
    for row in rows:
        place=row["place"]
        emaiil=row["email"]
        tel=row["tel"]
        address=row["address"]
    return render_template("modal.html",place=place,emaiil=emaiil,tel=tel,address=address)


@app.route("/LogOut")
def LogOut():
    session.clear()
    return redirect("/")