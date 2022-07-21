import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

from itertools import groupby
from operator import itemgetter
from cs50 import SQL

"""render a cat img if something went wrong as apology"""
def apology(message, code=400):
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

"""consult the api for the requested symbol and add a easy to use format"""
def lookup(symbol):

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

"""get a list with dicts with symbols and shares
   return a list with all those dicts normalized in no repeated symbols and sum shares"""
def Normalize(rawList):
    newList = list()

    items = sorted(rawList,key=itemgetter('symbol'))

    for key,value in groupby(items,key=itemgetter('symbol')):
        newDict = {key : 0}
        for k in value:
            newDict[key] += k['share']

        newList.append(newDict)

    return newList

"""take two list with symbols and shares, and calc the diference of shares with same symbols
   return a list of the diference"""
def diferenceDicts(list1,list2):
    list1 = Normalize(list1)
    list2 = Normalize(list2)

    for i in range(len(list2)):
        for j in  range(len(list1)):
            if list1[j].keys() == list2[i].keys():
                for k in list2[i]:
                    list1[j][k] = list1[j][k] - list2[i][k]
    return list1

"""read the symbol, consult the apy that symbol, and fill the list with the data, return a filled list"""
def fillList(myList):
    for item in myList:
        temp = dict()#saves the call of the api
        temp2 = int()#saves the amount of symbols buyed
        temp3 = str()#saves the key to be deleted

        #access temporaly to te unique key in the dict, because dict.keys() dont work properly
        for key in item:
            temp = lookup(key)
            temp2 = item[key]
            temp3 = key

        item['symbol'] = temp['symbol']
        item['name'] = temp['name']
        item['share'] = temp2
        item['price'] = temp['price']

        item.pop(temp3)

    return myList

"""this is a special method for history"""
def fill(List):
    newList = list()
    for item in List:
        temp = lookup(item['symbol'])
        item['name'] = temp['name']
        item['price'] = temp['price']

        newList.append(item)

    return newList

"""used by buy and sell to change the stocks of the user"""
def getPortafolio(userID):
    db = SQL("sqlite:///finance.db")

    RawBuy = db.execute("SELECT id,symbol,share from transactions WHERE user_id = ? AND operation = 'BUY'",userID)
    RawSell = db.execute("SELECT id,symbol,share from transactions WHERE user_id = ? AND operation = 'SELL'",userID)
    
    #format the outputs form the db
    normalizedList = diferenceDicts(RawBuy,RawSell)
    normalizedList = fillList(normalizedList)

    return normalizedList