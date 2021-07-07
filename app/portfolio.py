# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 10:22:27 2020

@author: TerryLaw
"""

from datetime import datetime, timezone, timedelta

import ffn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib.gridspec as gridspec
import yfinance as yfin
yfin.pdr_override()


def calculate_invincible_portfolio():
    if datetime.now(timezone.utc).astimezone().tzinfo.utcoffset(None)==timedelta(seconds=28800):
        prices = ffn.get('GLD, SPY, TLT', start='2005-01-01', end=datetime.today())
    else:
        prices = ffn.get('GLD, SPY, TLT', start='2004-12-31', end=datetime.today())
    
    prices = prices.reset_index()
    prices['portfolio'] = 100
    prices['gld_rb'] = 0
    prices['spy_rb'] = 0
    prices['tlt_rb'] = 0
    prices['portfolio_rb'] = 100

    symbols = ['gld', 'spy', 'tlt']

    for i in prices.index:
        if i == 0:
            for symbol in symbols:
                prices.loc[i, symbol + '_rb'] = prices[symbol][0]

            prices.loc[i, 'portfolio_rb'] = 100
            
        else:
            prices.loc[i, 'portfolio'] = prices['portfolio_rb'][i-1] * ((prices['spy'][i] / prices['spy_rb'][i-1] + prices['tlt'][i] / prices['tlt_rb'][i-1] + prices['gld'][i] / prices['gld_rb'][i-1]) / 3)
            
            # Quarter-end rebalancing
            if(i != len(prices)-1 and prices.Date[i].month % 3 == 0 and prices.Date[i+1].month % 3 == 1):
                for symbol in symbols:
                    prices.loc[i, symbol + '_rb'] = prices[symbol][i]

                prices.loc[i, 'portfolio_rb'] = prices['portfolio'][i]
            else:
                for symbol in symbols:
                    prices.loc[i, symbol + '_rb'] = prices[symbol + '_rb'][i-1]

                prices.loc[i, 'portfolio_rb'] = prices['portfolio_rb'][i-1]

    
    symbols.append('portfolio')
    export(prices, 'invincible_portfolio', symbols)


def calculate_invincible_portfolio2():
    if datetime.now(timezone.utc).astimezone().tzinfo.utcoffset(None)==timedelta(seconds=28800):
        prices = ffn.get('GLD, SPY, QQQ, TLT, IEF', start='2005-01-01', end=datetime.today())
    else:
        prices = ffn.get('GLD, SPY, QQQ, TLT, IEF', start='2004-12-31', end=datetime.today())
    
    prices = prices.reset_index()
    prices['portfolio'] = 100
    prices['gld_rb'] = 0
    prices['spy_rb'] = 0
    prices['qqq_rb'] = 0
    prices['tlt_rb'] = 0
    prices['ief_rb'] = 0
    prices['portfolio_rb'] = 100

    symbols = ['gld', 'spy', 'qqq', 'tlt', 'ief']

    for i in prices.index:
        if i == 0:
            for symbol in symbols:
                prices.loc[i, symbol + '_rb'] = prices[symbol][0]

            prices.loc[i, 'portfolio_rb'] = 100
            
        else:
            prices.loc[i, 'portfolio'] = prices['portfolio_rb'][i-1] * ((prices['spy'][i] / prices['spy_rb'][i-1] + prices['qqq'][i] / prices['qqq_rb'][i-1] + prices['tlt'][i] / prices['tlt_rb'][i-1] + prices['ief'][i] / prices['ief_rb'][i-1] + prices['gld'][i] / prices['gld_rb'][i-1]) / 5)
            
            # Quarter-end rebalancing
            if(i != len(prices)-1 and prices.Date[i].month % 3 == 0 and prices.Date[i+1].month % 3 == 1):
                for symbol in symbols:
                    prices.loc[i, symbol + '_rb'] = prices[symbol][i]

                prices.loc[i, 'portfolio_rb'] = prices['portfolio'][i]
            else:
                for symbol in symbols:
                    prices.loc[i, symbol + '_rb'] = prices[symbol + '_rb'][i-1]

                prices.loc[i, 'portfolio_rb'] = prices['portfolio_rb'][i-1]

    
    symbols.append('portfolio')
    export(prices, 'invincible_portfolio_5x20', symbols)



def export(prices, portfolio, symbols):
    weekday = datetime.today().weekday()

    prices.to_csv('static/' + portfolio + str(weekday) + '.csv')
    prices.to_csv('static/' + portfolio + '_latest.csv')
    prices.to_json('static/' + portfolio + '.json', orient='index')
    prices.tail(2).to_json('static/' + portfolio + '_latest.json', orient='records')



    prices.set_index('Date', inplace=True)

    perf = prices.loc[:, symbols].calc_stats()

    plot_equity_curve(prices, perf, 1, portfolio)
    plot_equity_curve(prices, perf, 3, portfolio)
    plot_equity_curve(prices, perf, 5, portfolio)
    plot_equity_curve(prices, perf, 10, portfolio)
    plot_equity_curve(prices, perf, 20, portfolio)
                    

    # fig = plt.figure(constrained_layout=True, figsize=(10, 5))
    # spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[3, 1])

    # ax1 = fig.add_subplot(spec[0, 0])
    # ax1.plot(prices['portfolio'], label=portfolio, linewidth=2)
    # ax1.legend(loc='upper left')
    # ax1.grid(True)

    # ax2 = fig.add_subplot(spec[1, 0])
    # ax2.plot(perf['portfolio'].prices.to_drawdown_series(), label='Drawdown')
    # ax2.legend(loc='lower left')
    # ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    # ax2.grid(True)


    # plt.savefig('static/' + portfolio + '_' + str(weekday) + '.png')
    # plt.savefig('static/' + portfolio + '_latest.png')
    # plt.close()


    for symbol in symbols:
        perf[symbol].stats.to_csv('static/' + symbol + '_stats_' + str(weekday) + '.csv')
        perf[symbol].stats.to_json('static/' + symbol + '_stats.json')
        perf[symbol].return_table.to_csv('static/' + symbol + '_monthly_returns_' + str(weekday) + '.csv')
        perf[symbol].return_table.to_json('static/' + symbol + '.json', orient='index')


    perf['portfolio'].stats.to_csv('static/' + portfolio + '_stats_' + str(weekday) + '.csv')
    perf['portfolio'].stats.to_json('static/' + portfolio + '_stats.json')
    perf['portfolio'].return_table.to_csv('static/' + portfolio + '_monthly_returns_' + str(weekday) + '.csv')
    perf['portfolio'].return_table.to_json('static/' + portfolio + '_monthly_returns.json', orient='index')



def plot_equity_curve(prices, perf, years, portfolio):
    weekday = datetime.today().weekday()

    fig = plt.figure(constrained_layout=True, figsize=(10, 5))
    spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[3, 1])

    ax1 = fig.add_subplot(spec[0, 0])
    ax1.plot(prices['portfolio'].tail(years*252), label=portfolio+' ('+str(years)+' year)', linewidth=2)
    ax1.legend(loc='upper left')
    ax1.grid(True)

    ax2 = fig.add_subplot(spec[1, 0])
    ax2.plot(perf['portfolio'].prices.to_drawdown_series().tail(years*252), label='Drawdown')
    ax2.legend(loc='lower left')
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax2.grid(True)


    if(years == 20):
        plt.savefig('static/' + portfolio + '_' + str(weekday) + '.png')
        plt.savefig('static/' + portfolio + '_latest.png')
    else:
        plt.savefig('static/' + portfolio + '_' + str(years) + '_' + str(weekday) + '.png')
        plt.savefig('static/' + portfolio + '_' + str(years) + '_latest.png')

    plt.close()

# calculate_invincible_portfolio()