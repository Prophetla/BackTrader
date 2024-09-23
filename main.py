import datetime
import backtrader as bt
from data_loader import configure_data
from strategy import SystemOne, SystemTwo, PriceClusterStrategy
from broker import configure_broker
from sizer import configure_sizer
from analyzer import add_analyzers, print_result


# 自定义 Trades 观察器
class CustomTrades(bt.observers.Trades):
    plotinfo = dict(plot=True, subplot=True,
                    plotname='Trades - Net Profit/Loss',
                    plotymargin=0.10,
                    plothlines=[0.0])
    plotlines = dict(
        pnlplus=dict(marker='+', color='#8FBC8F', markersize=4.0, fillstyle='full'),
        pnlminus=dict(marker='x', color='#CD5C5C', markersize=4.0, fillstyle='full')
    )


class CustomBuySell(bt.observers.BuySell):
    plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)
    plotlines = dict(
        buy=dict(marker='+', markersize=10,
                 # color='black',
                 fillstyle='full'),
        sell=dict(marker='x', markersize=10,
                  # color='black',
                  fillstyle='full')
    )


def configure_trades(cerebro):
    # 使用自定义的 Trades 观察器g
    cerebro.addobserver(CustomTrades)


def configure_buysell(cerebro):
    # 使用自定义的 Trades 观察器
    cerebro.addobserver(CustomBuySell)


def initialize_backtest():
    """
    初始化回测环境。通过参数控制是否进行优化。
    """
    cerebro = bt.Cerebro()

    # 数据文件路径
    kline_file_path = '/Users/prophetl/PycharmProjects/BackTrader/F-BTCUSDT-1m-202001-202408.csv'
    # kline_file_path = '/Users/prophetl/PycharmProjects/BackTrader/F-ETHUSDT-1m-202001-202408.csv'
    start_date = datetime.datetime(2024, 1, 1)
    end_date = datetime.datetime(2024, 2, 2)
    # end_date = start_date+ datetime.timedelta(hours=48)

    # 配置数据
    configure_data(cerebro, kline_file_path, start_date, end_date)

    # 添加策略
    cerebro.addstrategy(SystemOne)
    # cerebro.addstrategy(PriceClusterStrategy)

    # 配置 Broker
    configure_broker(cerebro)
    # 配置 Sizer
    configure_sizer(cerebro)
    # 添加分析器
    add_analyzers(cerebro)
    # 添加观察者
    cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.TimeReturn)
    # cerebro.addobserver(bt.observers.DrawDown)
    # 配置自定义 Trades 观察器
    configure_trades(cerebro)
    configure_buysell(cerebro)

    return cerebro


def run_backtest():
    """运行回测"""

    cerebro = initialize_backtest()

    results = cerebro.run(stdstats=False)  # 选 False 的情况下，必须要手动添加 Broker

    print_result(results)
    cerebro.plot(
        strategy=results[-1],
        # style='line',
        style='candlebar',
        barup='black',
        bardown='black',
        volume=True,
        grid=False,
        subtxtsize=4,
        barupfill=None,
        bardownfill='black',

    )


if __name__ == '__main__':
    # 运行普通回测
    run_backtest()
