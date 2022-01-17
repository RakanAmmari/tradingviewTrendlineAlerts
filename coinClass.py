class Coin:
    number_of_coins = 0

    def __init__(self, name="", exchange=""):
        self.exchange = exchange
        self.trendlines = []

        four_letters = ["USDT", "BUSD", "USDC"]
        three_letters = ["BTC", "ETH", "USD"]

        if name[-4:] in four_letters:
            self.name = name[0:-4]
            self.quoteCurrency = name[-4:]

        elif name[-3:] in three_letters:
            self.name = name[0:-3]
            self.quoteCurrency = name[-3:]

        Coin.number_of_coins += 1

    def addTrendline(self, trendline, priceWhenAdded):
        self.x1 = trendline[0]
        self.x2 = trendline[1]
        self.y1 = trendline[2]
        self.y2 = trendline[3]

        self.slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.b = self.y1 - self.slope * self.x1

        if priceWhenAdded < (self.slope * 299) + self.b:
            self.crossDirection = "Above"
        else:
            self.crossDirection = "Below"

        self.trendlines.append([self.x1, self.x2, self.y1, self.y2, self.slope, self.b, self.crossDirection])

