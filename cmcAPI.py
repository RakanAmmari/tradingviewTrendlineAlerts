from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import os
from dotenv import load_dotenv
load_dotenv()

###########################################################

def getPrices(strippedCoinNameString):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
    	'symbol':strippedCoinNameString,
    }
    headers = {
    	'Accepts': 'application/json',
    	'X-CMC_PRO_API_KEY': os.environ.get('coinmarketcapAPIKey'),
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        prices = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return prices