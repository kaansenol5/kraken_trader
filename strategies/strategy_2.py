import logging, time

logging.basicConfig(format="%(asctime)s %(message)s", filename='log.txt', level=logging.INFO)


def strategy(bot):
    logging.info("strategy_2 started")
    buy_price = 0
    while True:
        ticker_info = bot.check_ticker(bot.pair)
        balance = bot.check_balance()

        try:
            ticker = ticker_info[bot.other_type_of_pair]
        except KeyError as error:
            print(error)
            exit()

        ticker_high_day = round(float(ticker["h"][1]), 2)
        ticker_low_day = round(float(ticker["l"][1]), 2)
        average_price = (ticker_low_day + ticker_high_day) / 2
        ticker_current = round(float(ticker["a"][0]), 2)
        difference = ticker_current - average_price
        if difference < 0:
            if float(balance[bot.fiat]) > 0.02 / ticker_current:
                if average_price - average_price/100*bot.profit >= ticker_current:

                    amount_to_buy = float(balance[bot.fiat]) / ticker_current / 100 * bot.risk_management
                    buy_price = ticker_current
                    print("wantu buy")
                    bot.place_order("buy", "limit", buy_price - 0.05, amount_to_buy)
            else:
                pass
        elif difference > 0:

            if float(balance[bot.coin]) > 0.02:
                if average_price + average_price / 100 * bot.profit <= ticker_current:
                    amount_to_sell = balance[bot.coin]
                    sell_price = ticker_current
                    if sell_price > buy_price / 100 * 102:
                        print("wantu sell")
                        bot.place_order("sell", "limit", sell_price + 0.05, amount_to_sell)
            else:
                pass

        else:
            logging.info("current price is exactly the average price of last 24 hours, bruh moment")

        time.sleep(4)


