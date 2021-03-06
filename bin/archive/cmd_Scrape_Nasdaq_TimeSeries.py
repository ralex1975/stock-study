#!/usr/bin/env python

import logging
from libCommon import log_exception
from libFinance import STOCK_TIMESERIES, NASDAQ
from libDebug import trace, cpu

'''
   Web Scraper
   Use RESTful interface to download stock and fund stock market prices for the past 10 years
   Store as pkl files
'''

@trace
@log_exception
def main(local, *stock_list) :
    logging.info(stock_list)
    reader = STOCK_TIMESERIES.init()

    for stock in stock_list :
        filename = '{}/historical_prices/{}.pkl'.format(local,stock)
        ret = reader.extract_from_yahoo(stock)
        logging.debug(ret.tail(5))
        STOCK_TIMESERIES.save(filename, stock, ret)

    if len(stock_list) > 0 : return

    nasdaq = NASDAQ.init()

    for stock in nasdaq() :
        filename = '{}/historical_prices/{}.pkl'.format(local,stock)
        ret = reader.extract_from_yahoo(stock)
        STOCK_TIMESERIES.save(filename, stock, ret)

if __name__ == "__main__" :
   import logging
   from libCommon import ENVIRONMENT

   env = ENVIRONMENT()
   log_filename = '{pwd_parent}/log/{name}.log'.format(**vars(env))
   log_msg = '%(module)s.%(funcName)s(%(lineno)s) %(levelname)s - %(message)s'
   logging.basicConfig(filename=log_filename, filemode='w', format=log_msg, level=logging.DEBUG)

   stock_list = env.argv[1:]
   main('{}/local'.format(env.pwd_parent), *stock_list)

