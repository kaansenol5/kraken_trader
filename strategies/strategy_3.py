import logging, time

logging.basicConfig(format="%(asctime)s %(message)s", filename='log.txt', level=logging.INFO)

#TODO: make this thing in the next 365 days i hope

class Pair():
    def __init__(self, kraken, pair):
        self.name = pair
        self.ticker = kraken.check_ticker(pair)[pair]
        self.high = round(float(self.ticker["h"][1]), 2)
        self.low = round(float(self.ticker["l"][1]), 2)
        self.average = (self.high+self.low) / 2
        self.current = round(float(self.ticker["a"][0]))
        self.difference = self.average - self.current


def strategy(bot):
    pair_names = ["XETHXXBT","XXBTZUSD","XLTCXXBT","XLTCZUSD","LTCETH"]


    while True:
        pairs = []
        for pair_name in pair_names:
            print(pair_name)
            pairs.append(Pair(bot, pair_name))
        balance = bot.check_balance
        for pair in pairs:
            if pair.difference < 0:
                print(f"{pair.name} is a buy")
            else:
                print(f"{pair.name} is a sell" )

