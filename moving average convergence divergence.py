from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math

# Import the backtrader platform
import backtrader as bt
from backtrader.indicators import EMA

class MACD(bt.Indicator):
    lines = ('value',)
    params = (('first_period', 12), ('second_period', 26))

    def __init__(self, first_period=12, second_period=26):
        ema1 = EMA(self.data, period=self.p.first_period)
        ema2 = EMA(self.data, period=self.p.second_period)
        self.l.value = ema1 - ema2

# Create a Stratey
class MyStrategy(bt.Strategy):
    params = (
        ('compare_period', 9), ('holding', False), ('quantity', 0))

    def log(self, txt, dt=None):
        ''' Logging function not this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        #self.holding = False
        self.dataclose = self.datas[0].close
        self.macd = MACD(first_period=12, second_period=26)
        self.ema = EMA(self.macd, period=self.p.compare_period)

    def next(self):

        self.log('Close, %.2f' % self.dataclose[0])
        self.log('MACD, %.2f' % self.macd.l.value[0])
        self.log('EMA, %.2f' % self.ema.l[0][0])
        self.log('CASH, %.2f' % cerebro.broker.get_cash())


        if self.p.holding == False and self.macd.l.value[0] >= self.ema.l[0][0] and cerebro.broker.get_cash() > 0:
            # Do something
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.p.quantity = math.floor(cerebro.broker.get_cash() / self.dataclose)
            self.log('QUANTITY, %d' % self.p.quantity)

            self.p.holding = True
            order = self.buy(size = self.p.quantity)


        elif self.p.holding == True and self.macd.l.value[0] < self.ema.l[0][0]:
            # Do something else
            self.log('SELL CREATE, %.2f' % self.dataclose[0])

            self.p.holding = False
            order = self.sell(size = self.p.quantity)



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MyStrategy)

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname='SPY.csv',

        # Do not pass values before this date
        fromdate=datetime.datetime(2019, 3, 29),
        # Do not pass values before this date
        todate=datetime.datetime(2021, 3, 26),
        
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #clock the data
    cerebro.plot()