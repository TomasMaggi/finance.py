# finance

A monolitic webapp based in python, flask and sqlite, consuming a iexcloud financial api, with CRUD and session system.

## how to install in your machine

### install require

first install the required librarys using

```
    pip install -r requieriments.txt
```

### get your api key

then you need a key to be able to consume the api, so create an account on iexcloud, then follow the recommendations of the [official docs](https://iexcloud.zendesk.com/hc/en-us/articles/1500012489741)

### set the key as environment variable

then you need to set an environment variable in your system using the keyapi you got from the site, this depends on your operating system:

* for windows: `set API_KEY=[key]`
* for linux: `export API_KEY=[key]`

### create the db

you need a db to store the users and transactions, so run the db tool:

```
    python create_db
```

### how to run

now that flask can consume the api, type in the console (in the root directory):

```
    flask run
```

## how to use

### "make a user account"

if you don't have an active session, the web will ask you to login with an existing account or to create a new one, to create a new account click on register and type and fill in the corresponding fields, you don't need to confirm your user.

### what you can do now

now that you have an active session, you can:
* check the value of different stocks by clicking on quote in the navigation menu
* "buy" and "sell" stocks by clickng in buy and sell in navbar
* access your transaction history by clickng in history in navbar
* add money to your account in the home
