import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, getPortafolio, fillList, fill

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# checks for the db before start
if not exists("finance.db"):
    raise RuntimeError("db not created")

# configure the conection with the db
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    userID = session["user_id"]

    portafolio = getPortafolio(userID)
    cash = db.execute("SELECT cash FROM users WHERE id = ?",userID)[0]['cash']

    return render_template("index.html",data = portafolio,cash = cash)

"""
disclaimer

if we get a POST is because the client made some change in their databse
else is a GET and is because is loading the page

if there is no method distinction, assume that we can only do GET to the url
"""

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        amount = request.form.get("shares")

        output = lookup(symbol)

        if not output:
            return apology("that symbol don´t exist")

        if not amount.isnumeric():
            return apology("the amount is invalid")

        amount = int(amount)

        if not amount > 0:
            return apology("the amount is invalid")

        userID = session["user_id"]

        currentMoney = db.execute("SELECT cash FROM users WHERE id = ?",userID)[0]["cash"]
        currentMoney = currentMoney - (amount * output["price"])

        if currentMoney < 0:
            return apology("you cant afford that")

        db.execute("UPDATE users SET cash = ? WHERE id = ?",currentMoney,userID)
        db.execute("INSERT INTO transactions(user_ID,symbol,share,operation,date) VALUES(?,?,?,?,datetime('now'))",userID,output["symbol"],amount,"BUY")

        return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():

    userID = session["user_id"]
    history = db.execute("SELECT symbol,share,operation,date FROM transactions WHERE user_id = ?",userID)
    history = fill(history)

    return render_template("history.html",data=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        Symbol = request.form.get("symbol")

        if not Symbol:
            return apology("no symbol entered")
        else:
            output = lookup(Symbol)

            if not output:
                return apology("invalid symbol")

            return render_template("quoted.html",symbol=output)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if not user:
            return apology("username required")

        for item in db.execute("SELECT username FROM users"):
            if user == item["username"]:
                return apology("username alredy exist")

        if not password or not confirm:
            return apology("password required")

        if password != confirm:
            return apology("passworn and confirm dont are equal")

        db.execute("INSERT INTO users(username,hash) VALUES(:x,:y)",x=user, y=generate_password_hash(password))

        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?",user)[0]['id']

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get('symbol')
        shares = request.form.get('shares')
        userID = session["user_id"]
        
        portafolio = getPortafolio(userID)

        if not symbol:
            return apology("symbol not selected")

        if not shares or int(shares) < 1:
            return apology("invalid shares")

        shares = int(shares)
        symbol = lookup(symbol)

        if not symbol:
            return apology('that symbol dont exist')

        for item in portafolio:
            if item['symbol'] == symbol['symbol']:
                if item['share'] < shares:
                    return apology('you dont have so much shares')

        currentMoney = db.execute("SELECT cash FROM users WHERE id = ?",userID)[0]['cash']
        currentMoney = currentMoney + symbol['price'] * shares

        db.execute("UPDATE users SET cash = ? WHERE id = ?",currentMoney,userID)
        db.execute("INSERT INTO transactions(user_ID,symbol,share,operation,date) VALUES(?,?,?,?,datetime('now'))",userID,symbol['symbol'],shares,"SELL")

        return redirect("/")

    else:
        userID = session["user_id"]

        portafolio = getPortafolio(userID)

        return render_template("sell.html",data = portafolio)


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def depostit():
    if request.method == "POST":
        amount = request.form.get("amount")
        userID = session["user_id"]

        if not amount or not amount.isnumeric():
            return apology("bad amount sended")

        cash = db.execute("SELECT cash FROM users WHERE id = ?",userID)[0]['cash']

        cash = int(amount) + cash

        db.execute("UPDATE users SET cash = ? WHERE id = ?",cash,userID)

        return redirect("/")
    else:
        return render_template("deposit.html")