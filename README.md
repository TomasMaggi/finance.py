# finance

A monolitic webapp based in python, flask and sqlite, consuming a iexcloud financial api, with CRUD and session system.

## how to use

### install require

first install the required librarys using

```
    pip install -r requieriments.txt
```

### get your api key

then you need a key to be able to consume the api, so create an account on iexcloud, then follow the recommendations of the [official docs](https://iexcloud.zendesk.com/hc/en-us/articles/1500012489741)

### set the key as environment variable

then you need to set an environment variable in your system using the keyapi you got from the site, this depends on your operating system:

* for windows: set API_KEY=[key]
* for linux: export API_KEY=[key]

### how to run

now that flask can consume the api, type in the console (in the root directory):

```
    flask run
```
