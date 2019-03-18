import os
import sys
import pprint
import traceback
from copy import deepcopy

pp = pprint.PrettyPrinter(depth=6)

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')
# import ccxt  # noqa: E402
import ccxt.async_support as ccxt  # noqa: E402
import asyncio  # noqa: E402

loop = asyncio.get_event_loop()
# import txaio
# txaio.start_logging(level='debug')

last_ob = None

async def main():

    exchange_id = 'poloniex'
    apiKey = 'do not care'
    secret = 'do not care'
    limit = 100
    symbol = 'BTC/USDT'

    exchange = getattr(ccxt, exchange_id)({
        "apiKey": apiKey,
        "secret": secret,
        "enableRateLimit": True,
        'verbose': False,
        'timeout': 5 * 1000,
        # 'wsproxy': 'http://185.93.3.123:8080/',
    })

    @exchange.on('err')
    def websocket_error(err, conxid):  # pylint: disable=W0612
        print(type(err).__name__ + ":" + str(err))
        traceback.print_tb(err.__traceback__)
        traceback.print_stack()
        loop.stop()

    @exchange.on('ob')
    def websocket_ob(symbol, ob):  # pylint: disable=W0612
        global last_ob
        print("ob updated: " + symbol)
        sys.stdout.flush()
        #pp.pprint(ob)
        if last_ob is not None:
            for side in ['bids', 'asks']:
                for price, _ in last_ob[side][:10]:
                    flgFound = False
                    n = 0
                    for price2, _ in ob[side]:
                        n += 1
                        if price == price2 or n == 100:
                            flgFound = True
                            break
                    if not flgFound:
                        print('Found removal in top 10 of ' + side + ' for ' + str(price))
                        print('Old:')
                        pp.pprint(last_ob)
                        print('-----')
                        print('New:')
                        pp.pprint(ob)
                        quit()

        last_ob = deepcopy(ob)

    sys.stdout.flush()

    print("subscribe: " + symbol)
    sys.stdout.flush()
    await exchange.websocket_subscribe('ob', symbol, {'limit': limit})
    print("subscribed: " + symbol)
    sys.stdout.flush()
    ob = await exchange.websocket_fetch_order_book(symbol, limit)  # noqa: F841 pylint: disable=W0612
    print("ob fetched: " + symbol)
    # print(ob)
    sys.stdout.flush()
#    await asyncio.sleep(15)

 #   print("unsubscribe: " + symbol)
  #  sys.stdout.flush()
   # await exchange.websocket_unsubscribe('ob', symbol)
#    print("unsubscribed: " + symbol)
#    sys.stdout.flush()

#    await exchange.close()

print("before start")
loop.run_until_complete(main())
loop.run_forever()
# loop.stop()
# loop.close()
print("after complete")
