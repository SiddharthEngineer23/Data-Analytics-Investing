from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math

# Import the backtrader platform
import backtrader as bt
from backtrader.indicators import EMA

class ExponentialMovingAverage(bt.Indicator):
    # lines = ('value',)

    # params = (('period', 20), ('k', 2.0/21), ('inverseK', 19.0/21))

    # def __init__(self, period=20):
    #     self.p.period = period
    #     self.p.k = 2.0/(self.p.period + 1)
    #     self.p.inverseK = (1 - self.p.k)

    # def next(self):
    #     if(math.isnan(self.lines.value[-1])):
    #         self.lines.value[0] = self.data.close[0]
    #     else:
    #         self.lines.value[0] = self.lines.value[-1] * self.p.inverseK + self.data.close[0] * self.p.k

    lines = ('value',)
    params = (('period', 9), )

    def __init__(self, period=9):
        ema1 = EMA(self.data, period=12)
        ema2 = EMA(self.data, period=26)
        self.l.value = ema1 - ema2

# Create a Stratey
class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 15), ('holding', False), ('time', 20), ('price', 0),
    )

    def log(self, txt, dt=None):
        ''' Logging function not this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        #self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        self.ema = ExponentialMovingAverage(period=20)

    def next(self):

        self.log('Close, %.2f' % self.dataclose[0])
        self.log('EMA, %.2f' % self.ema.l.value[0])

        if self.p.holding == False and self.data.close[0] < self.ema.l.value[0]:
            # Do something
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            order = self.buy()

            self.p.holding = True
            self.p.time = 20
            self.p.price = self.dataclose[0]

        elif self.p.holding == True:
            # Do something else
            if (self.dataclose[0]) >= (1.05 * self.p.price):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                order = self.sell()
                self.p.holding = False
            elif (self.dataclose[0]) <= (0.9 * self.p.price):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                order = self.sell()
                self.p.holding = False
            elif self.p.time == 0:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                order = self.sell()
                self.p.holding = False
        
        else:
            self.p.time = self.p.time - 1



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MyStrategy)

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname='oracle.csv',

        # Do not pass values before this date
        fromdate=datetime.datetime(2001, 8, 2),
        # Do not pass values before this date
        todate=datetime.datetime(2002, 8, 1),
        
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #clock the data
    cerebro.plot()