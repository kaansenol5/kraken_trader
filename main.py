#code shittier than the average redditors ass

import krakenex
import time
import keys
import logging

#logging.basicConfig(format="%(asctime)s %(message)s",filename='log.log', encoding='utf-8', level=logging.INFO)


class TraderBot():
    def __init__(self, key, secret, coin, fiat, profit):
        self.kraken = krakenex.API(key=key, secret=secret)
        self.fiat = f"Z{fiat}"
        self.coin = f"X{coin}"
        self.pair = coin+fiat
        self.profit = profit
        self.other_type_of_pair = f"X{coin}Z{fiat}"

        print(self.check_balance())
        self.main()


    def check_balance(self):
        result = self.kraken.query_private("Balance")
        try:
            return result["result"]
        except KeyError:
            logging.error(f"{result['error']}, on check_balance()")
            return result["error"]

    def check_ticker(self,pair):
        result = (self.kraken.query_public("Ticker",{"pair":f"{pair}"}))

        try:
            return result["result"][self.other_type_of_pair]["a"][0]
        except KeyError:
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            print(f"{result['error']}, on check_ticker()")
            return result["error"]



    def check_open_orders(self):
        result = self.kraken.query_private("OpenOrders")

        try:
            return result["result"]["open"]
        except KeyError:
            print(f"{result['error']}, on check_open_orders()")
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            return result["error"]

    def place_order(self, type, order_type, price, volume, expire_time="0"):
        result = self.kraken.query_private("AddOrder",{"pair":self.pair,"type":type, "ordertype":order_type, "price":price, "volume":volume, "expiretm":expire_time})
        try:
            return result["result"]
        except KeyError:
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            print(result["error"])
            return result["error"]

    def cancel_order(self, txid):
        result = self.kraken.query_private("CancelOrder",{"txid":txid})
        return result
    def main(self):
        while True:
            print("globlobglab")
            balance = self.check_balance()
            ticker_price = float(self.check_ticker(self.pair))

            if self.check_open_orders() == {}:
                if float(balance[self.fiat]) > 25:

                    buy_volume = float(balance[self.fiat]) / ticker_price
                    buy_price = round(ticker_price - ticker_price / 100 * self.profit, 2)

                    sell_price = round(buy_price + buy_price / 100 * self.profit, 2 )
                    stop_loss_price = round(buy_price - buy_price / 100 * 4, 2)

                    buy_order = self.place_order("buy", "limit", buy_price, buy_volume)
                    print("buy placed")
                    buy_order_transaction_id = buy_order["txid"][0]
                    print(buy_order_transaction_id)
                    print(list(self.check_open_orders()))

                    while buy_order_transaction_id in list(self.check_open_orders()):
                        print("aaa")
                        time.sleep(4)

                    if buy_order_transaction_id not in list(self.check_open_orders()):
                        new_balance = self.check_balance()

                        coin_balance = new_balance[self.coin]
                        print(coin_balance)
                        sell_order = self.place_order("sell", "limit", sell_price, coin_balance)
                        sell_order_transaction_id = sell_order["txid"][0]
                        print("sell placed")

                        while sell_order_transaction_id in list(self.check_open_orders()):
                            if float(self.check_ticker(self.pair)) > stop_loss_price:
                                print("wara")

                            else:
                                self.cancel_order(sell_order_transaction_id)
                                self.place_order("sell","stop-loss",stop_loss_price / 100 * 98, coin_balance)
                                print("stop loss'ed")
                            time.sleep(4)




            else:
                print("pass")
            time.sleep(5)









TraderBot(keys.apikey,keys.privatekey,"ETH","USD", 0.5)