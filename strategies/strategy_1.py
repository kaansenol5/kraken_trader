import logging, time


def strategy(self):
    while True:
        balance = self.check_balance()
        ticker_price = float(self.check_ticker(self.pair))

        if self.check_open_orders() == {}:
            if float(balance[self.fiat]) > 25:

                buy_volume = float(balance[self.fiat]) / ticker_price * self.leverage / 100 * self.risk_management
                buy_price = round(ticker_price - ticker_price / 100 * self.profit, 2)

                sell_price = round(buy_price + buy_price / 100 * self.profit, 2)
                stop_loss_price = round(buy_price - buy_price / 100 * 4, 2)

                coin_balance_pre_buy = balance[self.coin]
                buy_order = self.place_order("buy", "limit", buy_price, buy_volume, expire_time="+900")
                print("buy placed")
                buy_order_transaction_id = buy_order["txid"][0]
                print(buy_order_transaction_id)
                print(list(self.check_open_orders()))

                while buy_order_transaction_id in list(self.check_open_orders()):
                    time.sleep(4)

                if buy_order_transaction_id not in list(self.check_open_orders()):
                    new_balance = self.check_balance()

                    coin_balance = new_balance[self.coin]

                    if coin_balance > coin_balance_pre_buy:
                        logging.info("Buy order seems to be filled, a sell order will be placed")
                        print(coin_balance)
                        sell_order = self.place_order("sell", "limit", sell_price, coin_balance)
                        sell_order_transaction_id = sell_order["txid"][0]
                        print("sell placed")

                        while sell_order_transaction_id in list(self.check_open_orders()):
                            if float(self.check_ticker(self.pair)) > stop_loss_price:
                                pass

                            else:
                                self.cancel_order(sell_order_transaction_id)
                                self.place_order("sell", "stop-loss", stop_loss_price / 100 * 98, coin_balance)
                                print("stop loss'ed")
                            time.sleep(4)
                    else:
                        logging.info(
                            "Latest buy order seems to have expired (or an unknown error occured), a new buy order will be placed if there is enough balance in the account")




        else:
            print("pass")
        time.sleep(5)