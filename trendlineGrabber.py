import time
import pickle
import os
from dotenv import load_dotenv; load_dotenv()
from coinClass import Coin
# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime,timezone


def getCoinDetails(driver):
    time.sleep(1)
    nameOfCoin = driver.find_element(By.CSS_SELECTOR, '.title-2ahQmZbQ').get_attribute("innerText")
    exchangeOfCoin = driver.find_element(By.CSS_SELECTOR, 'div.title-1WIwNaDF:nth-child(5)').get_attribute("innerText")
    driver.implicitly_wait(20)
    # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    # WebDriverWait(driver, 120, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.price-3PT2D-PK')))
    priceOfCoin = float(driver.find_element(By.CSS_SELECTOR, '.price-3PT2D-PK').get_attribute("innerText"))
    return nameOfCoin, exchangeOfCoin, priceOfCoin


def getCoordinatesFromObjectTree(objectTreeObjects, driver):
    trendlineCoordinates = []

    for object in objectTreeObjects:
        # print(object.get_attribute("innerText"))
        if object.get_attribute("class") != "title-3Onbn19L disabled-3Onbn19L":
            if (object.get_attribute("innerText") == "Trend Line" or object.get_attribute("innerText") == "Ray"):
                webdriver.ActionChains(driver).double_click(object).perform()
                x1 = driver.find_element(By.CSS_SELECTOR, "div.cell-22S1W3v8:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)").get_attribute("value")
                x2 = driver.find_element(By.CSS_SELECTOR, "div.cell-22S1W3v8:nth-child(4) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)").get_attribute("value")
                y1 = driver.find_element(By.CSS_SELECTOR, "div.cell-22S1W3v8:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)").get_attribute("value")
                y2 = driver.find_element(By.CSS_SELECTOR, "div.cell-22S1W3v8:nth-child(4) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)").get_attribute("value")
                trendlineCoordinates.append([float(x1), float(x2), float(y1), float(y2)])

    return trendlineCoordinates


def main() -> None:
    # print(time.mktime(time.gmtime()))
    coinsList = []

    print("Retrieving trendlines. Please wait...")

    # Selenium WebDriver Setup
    browserDriverPath = 'C:\\Program Files (x86)\\chromedriver.exe'
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--window-size=1920x1080")
    options.add_argument("start-maximized")  # start-fullscreen
    service = ChromeService(executable_path=browserDriverPath)
    driver = webdriver.Chrome(service=service, options=options)

    # Open TradingView
    driver.get("http://www.tradingview.com")
    driver.implicitly_wait(20)
    # Click on user menu to access sign in
    driver.find_element(By.CSS_SELECTOR, "button.tv-header__user-menu-button:nth-child(1)").click()
    driver.find_element(By.CSS_SELECTOR, "div.item-2IihgTnv:nth-child(1)").click()
    # Choose email option
    driver.find_element(By.CSS_SELECTOR, ".tv-signin-dialog__toggle-email").click()
    # Enter email and password and click on sign-in
    driver.find_element(By.NAME, 'username').send_keys(os.environ.get("tradingViewEmail"))
    driver.find_element(By.NAME, 'password').send_keys(os.environ.get("tradingViewPassword"))
    driver.find_element(By.CSS_SELECTOR, ".tv-button__loader").click()
    # Open "Chart", since clicking on Chart did not work. Make sure this works as intended and does not just open AAPL.
    time.sleep(2)
    driver.get("http://www.tradingview.com/chart/")
    # Choose 15m timeframe
    driver.find_element(By.CSS_SELECTOR, "html.is-authenticated.is-not-pro.is-not-trial.feature-no-touch.feature-no-mobiletouch.theme-light.is-not-trial-available body.chart-page.unselectable.i-no-scroll div.js-rootresizer__contents div.layout__area--top div.toolbar-LZaMRgb9 div.overflowWrap-LZaMRgb9 div.inner-i5o9yNmy div.wrapOverflow-3obNZqvj div.wrap-3obNZqvj div.scrollWrap-3obNZqvj.noScrollBar-3obNZqvj div.content-i5o9yNmy div.wrap-1ETeWwz2 div.group-3uonVBsm div#header-toolbar-intervals.wrap-3jbioG5e div.menu-2R6OKuTS.button-1SoiPS-f.apply-common-tooltip div.arrow-1SoiPS-f").click()  # Open timeframe dropdown menu
    driver.implicitly_wait(20)
    driver.find_element(By.CSS_SELECTOR, ".dropdown-2R6OKuTS > div:nth-child(11) > div:nth-child(1) > div:nth-child(1)").click()  # Choose 15m option from dropdown menu
    # Make sure watchlist is initially selected. If not, select it.
    classOfWatchlistButton = driver.find_element(By.CSS_SELECTOR, "div.button-DABaJZo4:nth-child(1)").get_attribute("class")
    if classOfWatchlistButton == "button-DABaJZo4 isTab-DABaJZo4 isGrayed-DABaJZo4 apply-common-tooltip common-tooltip-vertical":
        driver.find_element(By.CSS_SELECTOR, "div.button-DABaJZo4:nth-child(1)").click()

    # Get first coin name, exchange, and its trendlines, so it acts as an exit condition of the loop.
    firstCoinName, firstCoinExchange, firstCoinPrice = getCoinDetails(driver)

    firstCoinName = Coin(firstCoinName, firstCoinExchange)
    coinsList.append(firstCoinName)

    driver.find_element(By.CSS_SELECTOR, "div.button-DABaJZo4:nth-child(18) > span:nth-child(2) > svg:nth-child(1)").click()  # Click on Object Tree icon
    time.sleep(2)
    objects = driver.find_elements(By.CLASS_NAME, "title-3Onbn19L")  # Get all elements in object tree
    trendlineCoordinates = getCoordinatesFromObjectTree(objects, driver)

    for trendline in trendlineCoordinates:
        firstCoinName.addTrendline(trendline, firstCoinPrice)

    while True:
        driver.find_element(By.CSS_SELECTOR, "div.button-DABaJZo4:nth-child(1) > span:nth-child(2) > svg:nth-child(1)").click()  # Click on "Watchlist and details"
        webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()  # To switch to next coin

        driver.implicitly_wait(20)
        coinName, coinExchange, coinPrice = getCoinDetails(driver)

        # print("coinName: " + coinName)
        # print("coinExchange: " + coinExchange)
        # print("firstCoinName: " + firstCoinName.name + firstCoinName.quoteCurrency)
        # print("firstCoinExchange: " + firstCoinName.exchange)
        if coinName == firstCoinName.name + firstCoinName.quoteCurrency and coinExchange == firstCoinName.exchange:
            break

        coinName = Coin(coinName, coinExchange)
        coinsList.append(coinName)

        driver.find_element(By.CSS_SELECTOR, "div.button-DABaJZo4:nth-child(18) > span:nth-child(2) > svg:nth-child(1)").click()  # Click on Object Tree icon
        time.sleep(2)
        objects = driver.find_elements(By.CLASS_NAME, "title-3Onbn19L")  # Get all elements in object tree
        trendlineCoordinates = getCoordinatesFromObjectTree(objects, driver)

        for trendline in trendlineCoordinates:
            coinName.addTrendline(trendline, coinPrice)

    # At this point, "coinsList" is a list of objects (of type 'Coin' class). Each object has name, exchange, and a list
    # of trendlines. "coinsList" can now be iterated through.
    time_now = int(time.time())

    pickleFile = open('listOfCoins.pkl', "wb")
    pickle.dump([coinsList, time_now], pickleFile)
    pickleFile.close()

    driver.close()

    print("Trendlines retrieved.")


if __name__ == '__main__':
    main()
