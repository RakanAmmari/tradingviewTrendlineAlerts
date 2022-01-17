import os
import os.path
import time
import pickle
from datetime import datetime
from math import ceil
from time import sleep
import requests
from dotenv import load_dotenv
import cmcAPI
from coinMarketCapReplacements import correctCMCSymbol
load_dotenv()

telegramTokenList = os.environ.get("telegramBotTokens").split(",")
telegramChatIDList = os.environ.get("telegramChatIDs").split(",")

def task():
    # pickleFile = open("listOfCoins.pkl", "rb")
    # coinsList = pickle.load(pickleFile)  # Replace this with two vars, one for coinsList and one for time created.
    with open("listOfCoins.pkl", "rb") as pickleFile:  # Python 3: open(..., 'rb')
        coinsList, timeCreated = pickle.load(pickleFile)

    for i in range(len(coinsList)):
        if coinsList[i].name in correctCMCSymbol:
            coinsList[i].name = correctCMCSymbol[coinsList[i].name]

    pickle_time = timeCreated
    print("pickle time: ", datetime.fromtimestamp(pickle_time).strftime("%A, %B %d, %Y %I:%M:%S"))

    time_now = int(time.time())
    print("time: ", datetime.fromtimestamp(time_now).strftime("%A, %B %d, %Y %I:%M:%S"))

    time_difference = time_now - pickle_time
    time_difference = (time_difference - (time_difference % 60))/60  # (time_now - time.mktime(pickle_time))/60
    bars_difference = ceil(time_difference/15)

    print("time difference: ", time_difference)
    print("bars difference: ", bars_difference)

    coins_list = []

    for coin in coinsList:
        coins_list.append(coin.name)

    coins_string = ','.join(coins_list)
    prices = cmcAPI.getPrices(coins_string)

    if prices['status']['error_code'] == 400:
        # Send telegram notify informing user about invalid symbol
        invalidSymbols = prices['status']['error_message'].split(":")[1].split('"')[1]

        msg = f"{invalidSymbols} is not available on CoinMarketCap.\nYou will not be notified regarding its trendlines."
        for i in range(len(telegramTokenList)):
            requests.get(
                f'https://api.telegram.org/bot{telegramTokenList[i]}/sendMessage?chat_id={telegramChatIDList[i]}&parse_mode=Markdown&text={msg}')

        for invalidSymbol in invalidSymbols:
            coins_list.remove(invalidSymbol)

            for coin in coinsList:
                if coin.name == invalidSymbol:
                    coinsList.remove(coin)

        coins_string = ','.join(coins_list)
        prices = cmcAPI.getPrices(coins_string)

    coinNameAndTrendlinePrices = {}  # No use other than for printing the coin names and trendline prices later on

    for coin in coinsList:
        # 1. If quoteCurrency is USD -> Continue
        # 2. If quoteCurrency is BTC or ETH -> convert current price to BTC or ETH
        if coin.quoteCurrency == 'BTC':
            price = prices['data'][coin.name]['quote']['USD']['price']/prices['data']['BTC']['quote']['USD']['price']
        elif coin.quoteCurrency == 'ETH':
            price = prices['data'][coin.name]['quote']['USD']['price']/prices['data']['ETH']['quote']['USD']['price']
        else:
            price = prices['data'][coin.name]['quote']['USD']['price']

        coinNameAndTrendlinePrices[coin.name] = []

        for trendline in coin.trendlines:
            trendline[0] -= bars_difference
            trendline[1] -= bars_difference
            # 1. Calculate the b of each trendline in coin.
            b = trendline[2] - trendline[4] * trendline[0]
            # 2. Compare current price with trendline price.
            trendline_price = (trendline[4] * 299) + b
            # 3. Send telegram alert if cross happens with regard to 'Above' and 'Below'.
            # 4. If a trendline is triggered, change "Above" to "Below" and vice versa.

            if trendline[6] == "Above" and price >= trendline_price:
                price = round(price, 8)
                trendline_price = round(trendline_price, 8)
                msg = f"ALERT! {coin.name}/{coin.quoteCurrency} has crossed ABOVE a trendline! Run to TradingView urgently please!\nCurrent price: {price}\nTrendline price: {trendline_price}"
                for i in range(len(telegramTokenList)):
                    requests.get(f'https://api.telegram.org/bot{telegramTokenList[i]}/sendMessage?chat_id={telegramChatIDList[i]}&parse_mode=Markdown&text={msg}')
                trendline[6] = "Below"

            elif trendline[6] == "Below" and price <= trendline_price:
                price = round(price, 8)
                trendline_price = round(trendline_price, 8)
                msg = f"ALERT! {coin.name}/{coin.quoteCurrency} has crossed BELOW a trendline! Run to TradingView urgently please!\nCurrent price: {price}\nTrendline price: {trendline_price}"
                for i in range(len(telegramTokenList)):
                    requests.get(f'https://api.telegram.org/bot{telegramTokenList[i]}/sendMessage?chat_id={telegramChatIDList[i]}&parse_mode=Markdown&text={msg}')
                trendline[6] = "Above"

            coinNameAndTrendlinePrices[coin.name].append(trendline_price)

    print(coinNameAndTrendlinePrices)

    # Writing to pickle file to save new crossDirection
    pickleFile = open("listOfCoins.pkl", "wb")
    pickle.dump([coinsList, time_now], pickleFile)


def main():
    # Every 15 minutes
    while True:
        while datetime.now().minute not in {0, 15, 30, 45}:
            # Wait 30 seconds until we are synced up with the 'every 15 minutes' clock
            sleep(30)

        # msg = f"Checking trendlines."
        # for i in range(len(telegramTokenList)):
        #     requests.get(
        #         f'https://api.telegram.org/bot{telegramTokenList[i]}/sendMessage?chat_id={telegramChatIDList[i]}&parse_mode=Markdown&text={msg}')

        task()

        sleep(60 * 12)  # Wait for 12 minutes


if __name__ == '__main__':
    main()
