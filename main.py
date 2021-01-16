#code shittier than the average redditors ass

import krakenex
import time
import json
import logging

open("log.txt","w+").close()
logging.basicConfig(format="%(asctime)s %(message)s", filename='log.txt', level=logging.INFO)


class TraderBot():
    def __init__(self):
        config_file = open("config.json")
        key_file = open("keys.json")

        config = json.load(config_file)
        keys = json.load(key_file)
        config_file.close()
        key_file.close()

        self.kraken = krakenex.API(key=keys["key"], secret=keys["secret"])
        self.fiat = f"Z{config['fiat']}"
        self.coin = f"X{config['coin']}"
        self.pair = config["coin"]+config["fiat"]
        self.profit = int(config["profit"])
        self.leverage = int(config["leverage"])
        self.other_type_of_pair = f"X{config['coin']}Z{config['fiat']}"
        print(self.check_balance())
        logging.info("Bot init complete")
        self.main()


    def check_balance(self):
        result = self.kraken.query_private("Balance")
        logging.info("Checked balance.")
        try:
            return result["result"]
        except KeyError:
            logging.error(f"{result['error']}, on check_balance()")
            return result["error"]

    def check_ticker(self,pair):
        result = (self.kraken.query_public("Ticker",{"pair":f"{pair}"}))
        logging.info(f"Checked {pair}.")

        try:
            return result["result"][self.other_type_of_pair]["a"][0]
        except KeyError:
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            print(f"{result}, on check_ticker()")
            return result["error"]



    def check_open_orders(self):
        result = self.kraken.query_private("OpenOrders")
        logging.info("Checked open orders.")
        try:
            return result["result"]["open"]
        except KeyError:
            print(f"{result['error']}, on check_open_orders()")
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            return result["error"]

    def place_order(self, type, order_type, price, volume, leverage, expire_time="0"):
        result = self.kraken.query_private("AddOrder",{"pair":self.pair,"type":type, "ordertype":order_type, "price":price, "volume":volume, "expiretm":expire_time,"leverage":leverage})
        logging.info(f"Tried to place {self.pair} order. Type: {type}, Ordertype: {order_type}, Price: {price}, volume: {volume}. Expires in {expire_time} seconds. Transaction id: {result['result']}")
        try:
            return result["result"]
        except KeyError:
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            else:
                logging.info(f"An error occured:   {result}   order not placed.")
                print(result["error"])
            return result["error"]

    def cancel_order(self, txid):
        result = self.kraken.query_private("CancelOrder",{"txid":txid})
        logging.info(f"Cancelled order {txid}")
        return result


    def main(self):
        while True:
            balance = self.check_balance()
            ticker_price = float(self.check_ticker(self.pair))

            if self.check_open_orders() == {}:
                if float(balance[self.fiat]) > 25:

                    buy_volume = float(balance[self.fiat]) / ticker_price * self.leverage
                    buy_price = round(ticker_price - ticker_price / 100 * self.profit, 2)

                    sell_price = round(buy_price + buy_price / 100 * self.profit, 2 )
                    stop_loss_price = round(buy_price - buy_price / 100 * 4, 2)

                    coin_balance_pre_buy = balance[self.coin]
                    buy_order = self.place_order("buy", "limit", buy_price, buy_volume, self.leverage, expire_time="+900")
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

                        if coin_balance > coin_balance_pre_buy:
                            logging.info("Buy order seems to be filled, a sell order will be placed")
                            print(coin_balance)
                            sell_order = self.place_order("sell", "limit", sell_price, coin_balance, self.leverage)
                            sell_order_transaction_id = sell_order["txid"][0]
                            print("sell placed")

                            while sell_order_transaction_id in list(self.check_open_orders()):
                                if float(self.check_ticker(self.pair)) > stop_loss_price:
                                    print("wara")

                                else:
                                    self.cancel_order(sell_order_transaction_id)
                                    self.place_order("sell","stop-loss",stop_loss_price / 100 * 98, coin_balance, self.leverage)
                                    print("stop loss'ed")
                                time.sleep(4)
                        else:
                            logging.info("Latest buy order seems to have expired (or an unknown error occured), a new buy order will be placed if there is enough balance in the account")




            else:
                print("pass")
            time.sleep(5)









TraderBot()