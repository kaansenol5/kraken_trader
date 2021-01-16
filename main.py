#code shittier than the average redditors ass

import krakenex
import time
import keys
import logging

logging.basicConfig(format="%(asctime)s %(message)s",filename='log.log', encoding='utf-8', level=logging.INFO)


class TraderBot():
    def __init__(self, key, secret, pair):
        self.kraken = krakenex.API(key=key, secret=secret)
        self.pair = pair
        print(self.check_balance())
        print(self.kraken.query_private("OpenOrders")["result"]["open"])
        print(self.check_balance())
        self.main()


    def check_balance(self):
        return (self.kraken.query_private("Balance"))["result"]


    def check_ticker(self,pair):
        return float((self.kraken.query_public("Ticker",{"pair":f"{pair}"}))["result"]["XETHZUSD"]["a"][0])


    def check_open_orders(self):
        return self.kraken.query_private("OpenOrders")["result"]["open"]


    def auto_trade(self):
        price = self.check_ticker(self.pair) #best ask current
        buy_price = round(price - price/100*0, 1 )     #price we want to buy at
        print(buy_price)
        amount_to_buy = float(self.check_balance()["ZUSD"]) / buy_price

        sell_price = round(price + price/100*0, 1)                           #price we wish to sell at

        balance = self.check_balance()
        stop_loss = round(buy_price - buy_price/100*0.5, 2)       #stop loss

        if float(balance["XETH"]) == 0:
            print("aeeqawad")
            print(amount_to_buy)
            order = self.kraken.query_private("AddOrder",{"pair":f"{self.pair}","type":"buy", "ordertype":"limit", "price":f"{buy_price}", "volume":f"{amount_to_buy}","expiretm":"+60"})
            logging.info(
                f"Placed order to buy {amount_to_buy} {self.pair} @ {buy_price}. Current price of {self.pair} is {price}. Position will be closed when {self.pair} is {sell_price}.")

            print(order)
            print(order["result"]["txid"][0])
            print(str(self.check_open_orders()))
            while order["result"]["txid"][0] in self.check_open_orders():
                print("quqaeuq")
                time.sleep(4)
            print("aaaa")
            print(self.kraken.query_private("AddOrder",{"pair":f"{self.pair}", "type":"sell", "ordertype":"limit", "price":f"{sell_price}", "volume":f"{amount_to_buy}"}))
            print(self.kraken.query_private("AddOrder",{"pair":f"{self.pair}","type":"sell", "ordertype":"stop-loss", "price":f"{stop_loss}", "volume":f"{amount_to_buy}"}))


    def main(self):
        while True:
            open_orders = self.check_open_orders()

            if open_orders == {}:
                logging.info("orders seem to be filled")
                self.auto_trade()
            else:
                print("orders are not filled yet. passed")
            time.sleep(6)


pass

TraderBot(keys.apikey,keys.privatekey,"ETHUSD")