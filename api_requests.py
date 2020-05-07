import requests


def request_search_data (keyword):

    function = "function=SYMBOL_SEARCH"
    symbol = "&keywords=" + keyword
    key = "&apikey=DBBCEP6J972FNU4I"
    url = "https://www.alphavantage.co/query?" + function + symbol + key

    response = requests.get(url)

    match_list = response.json()['bestMatches']

    match_symbols = []
    for matches in match_list:
        sym = matches['1. symbol']
        match_symbols.append(sym)

    return match_symbols


def request_full_stock_data (stock):
    function = "function=GLOBAL_QUOTE"
    symbol = "&symbol=" + stock
    key = "&apikey=DBBCEP6J972FNU4I"
    url = "https://www.alphavantage.co/query?" + function + symbol + key

    response = requests.get(url)

    return response.json()['Global Quote']


