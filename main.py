#code shittier than the average redditors ass

import krakenex
import time
import json
import logging
import strategies.strategy_1
import strategies.strategy_2


class TraderBot():
    def __init__(self):
        open("log.txt", "w+").close()

        logging.basicConfig(format="%(asctime)s %(message)s", filename='log.txt', level=logging.INFO)

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
        self.risk_management = config["risk_management"]
        self.strategy_to_use = config["strategy_to_use"]
        print(self.check_balance())
        logging.info("Bot init complete")

        if self.strategy_to_use == "strategy_1":
            strategies.strategy_1.strategy(self)
        elif self.strategy_to_use == "strategy_2":
            strategies.strategy_2.strategy(self)
        else:
            print("No such strategy")

    def check_balance(self):
        result = self.kraken.query_private("Balance")
        logging.debug("Checked balance.")
        try:
            return result["result"]
        except KeyError:
            logging.error(f"{result['error']}, on check_balance()")
            return result["error"]

    def check_ticker(self,pair):
        result = (self.kraken.query_public("Ticker",{"pair":f"{pair}"}))
        logging.debug(f"Checked {pair}.")

        try:
            return result["result"]
        except KeyError:
            if result["error"] == "[EAPI:Rate limit exceeded]":
                print("rate limited, waiting 15 minutes")
                time.sleep(900)
            print(f"{result}, on check_ticker()")
            return result["error"]



    def check_open_orders(self):
        result = self.kraken.query_private("OpenOrders")
        logging.debug("Checked open orders.")
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
        logging.info(f"Tried to place {self.pair} order. Type: {type}, Ordertype: {order_type}, Price: {price}, volume: {volume}. Expires in {expire_time} seconds.")
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
        logging.debug(f"Cancelled order {txid}")
        return result












TraderBot()