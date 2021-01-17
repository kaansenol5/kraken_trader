import logging, time


def strategy(bot):
    while True:
        ticker_info = bot.check_ticker(bot.pair)
        balance = bot.check_balance()
        print(balance)
        print(ticker_info)
        try:
            ticker = ticker_info[bot.other_type_of_pair]
        except KeyError as error:
            print(error)
            exit()

        ticker_high_day = round(float(ticker["h"][1]), 2)
        ticker_low_day = round(float(ticker["l"][1]), 2)
        average_price = (ticker_low_day + ticker_high_day) / 2
        ticker_current = round(float(ticker["a"][0]), 2)
        print(average_price)
        if average_price < ticker_current:
            print("wantu buy")
            if float(balance[bot.fiat]) > 0.2 / ticker_current:
                amount_to_buy = balance[bot.fiat] / ticker_current / 100 * bot.risk_management
                bot.place_order("buy", "limit", ticker_current + 1, amount_to_buy)
            else:
                print("no monnai")

        elif average_price > ticker_current:
            print("wantu sell")

            if float(balance[bot.coin]) > 0.2:
                amount_to_sell = balance[bot.coin]
                bot.place_order("buy", "limit", ticker_current - 1, amount_to_sell)
            else:
                print("no crypto")

        else:
            pass

        time.sleep(4)


