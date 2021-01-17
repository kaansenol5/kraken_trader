import logging, time


def strategy(bot):
    while True:
        balance = bot.check_balance()
        ticker_price = float(bot.check_ticker(bot.pair)[bot.other_type_of_pair]["a"][0])

        if bot.check_open_orders() == {}:
            if float(balance[bot.fiat]) > 25:

                buy_volume = float(balance[bot.fiat]) / ticker_price * bot.leverage / 100 * bot.risk_management
                buy_price = round(ticker_price - ticker_price / 100 * bot.profit, 2)

                sell_price = round(buy_price + buy_price / 100 * bot.profit, 2)
                stop_loss_price = round(buy_price - buy_price / 100 * 4, 2)

                coin_balance_pre_buy = balance[bot.coin]
                buy_order = bot.place_order("buy", "limit", buy_price, buy_volume, expire_time="+900")
                print("buy placed")
                buy_order_transaction_id = buy_order["txid"][0]
                print(buy_order_transaction_id)
                print(list(bot.check_open_orders()))

                while buy_order_transaction_id in list(bot.check_open_orders()):
                    time.sleep(4)

                if buy_order_transaction_id not in list(bot.check_open_orders()):
                    new_balance = bot.check_balance()

                    coin_balance = new_balance[bot.coin]

                    if coin_balance > coin_balance_pre_buy:
                        logging.info("Buy order seems to be filled, a sell order will be placed")
                        print(coin_balance)
                        sell_order = bot.place_order("sell", "limit", sell_price, coin_balance)
                        sell_order_transaction_id = sell_order["txid"][0]
                        print("sell placed")

                        while sell_order_transaction_id in list(bot.check_open_orders()):
                            if float(bot.check_ticker(bot.pair)[bot.other_type_of_pair]["a"][0]) > stop_loss_price:
                                pass

                            else:
                                bot.cancel_order(sell_order_transaction_id)
                                bot.place_order("sell", "stop-loss", stop_loss_price / 100 * 98, coin_balance)
                                print("stop loss'ed")
                            time.sleep(4)
                    else:
                        logging.info(
                            "Latest buy order seems to have expired (or an unknown error occured), a new buy order will be placed if there is enough balance in the account")




        else:
            print("pass")
        time.sleep(5)