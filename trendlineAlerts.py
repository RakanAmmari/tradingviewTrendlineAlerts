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

telegramTokenList = os.environ.get("telegramBotTokens").split(",")  # Create a list of Telegram bot tokens.
telegramChatIDList = os.environ.get("telegramChatIDs").split(",")  # Create a list of Telegram chat IDs, in the same order as the bot tokens.

def sendAlertIfPriceCrossed():
    # Load list of coins and time modified into variable every 15 mins.
    with open("listOfCoins.pkl", "rb") as pickleFile:
        coinsList, pickle_time = pickle.load(pickleFile)

    # Replace any symbol not available on CoinMarketCap with the correct symbol so that price is successfully retrieved.
    for i in range(len(coinsList)):
        if coinsList[i].name in correctCMCSymbol:
            coinsList[i].name = correctCMCSymbol[coinsList[i].name]

    # Print out the time pickle file was last saved at.
    print("pickle time: ", datetime.fromtimestamp(pickle_time).strftime("%A, %B %d, %Y %I:%M:%S"))

    # Record and print the time now.
    time_now = int(time.time())
    print("time: ", datetime.fromtimestamp(time_now).strftime("%A, %B %d, %Y %I:%M:%S"))

    # To calculate how many bars need to be subtracted from x1 and x2, calculate time since pickle file was last modified
    # and check how many 15 minute bars they are.
    time_difference = time_now - pickle_time
    time_difference = (time_difference - (time_difference % 60))/60
    bars_difference = ceil(time_difference/15)

    print("time difference: ", time_difference)
    print("bars difference: ", bars_difference)

    # Create a list of coin names so that later a string can be formed of comma separated coin names. Used for CoinMarketCap API call.
    coins_list = []
    for coin in coinsList:
        coins_list.append(coin.name)
    coins_string = ','.join(coins_list)
    prices = cmcAPI.getPrices(coins_string)  # CoinMarketCap API call.

    # If coin's symbol on TradingView doesn't match CoinMarketCap's, remove it from coins_list (list of names) and from coinsList (list of coin objects)
    # and send a Telegram notification informing the user.
    if prices['status']['error_code'] == 400:
        # Create a list of them (in case it was more than one).
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
            # Subtract the number of bars from x1 and x2 so that the current bar is always 299 (TradingView's system, not sure why.)
            trendline[0] -= bars_difference
            trendline[1] -= bars_difference

            # 1. Calculate the b of each trendline in coin.
            b = trendline[2] - trendline[4] * trendline[0]
            # 2. Calculate trendline price.
            trendline_price = (trendline[4] * 299) + b

            # 3. Compare current price with trendline price.
            # 4. Send telegram alert if cross happens with regard to 'Above' and 'Below'.
            # 5. If a trendline is triggered, change "Above" to "Below" and vice versa.
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

    # Writing to pickle file to save new crossDirection and time modified
    pickleFile = open("listOfCoins.pkl", "wb")
    pickle.dump([coinsList, time_now], pickleFile)


def main():
    while True:
    # Every 15 minutes
        while datetime.now().minute not in {0, 15, 30, 45}:
            # Sleep 30 seconds before checking again.
            sleep(30)

        # Heartbeat message.
        # msg = f"Checking trendlines."
        # for i in range(len(telegramTokenList)):
        #     requests.get(
        #         f'https://api.telegram.org/bot{telegramTokenList[i]}/sendMessage?chat_id={telegramChatIDList[i]}&parse_mode=Markdown&text={msg}')

        # Run the main task of retrieving prices, calculating trendline prices, and sending Telegram alert if the price crossed a trendline.
        sendAlertIfPriceCrossed()

        # In order to not keep checking every 30 seconds, wait 12 minutes first. Probably reduces resource usage.
        sleep(60 * 12)


if __name__ == '__main__':
    main()
