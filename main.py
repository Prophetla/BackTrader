import backtrader as bt
from strategy import SmaCrossStrategy
from data_loader import load_data
from broker import configure_broker
from sizer import configure_sizer
from analyzer import add_analyzers, print_result

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 加载原始1分钟数据
    data_1min = load_data()

    # 添加1分钟数据到Cerebro，并且对其进行重新采样
    cerebro.adddata(data_1min)  # 原始1分钟数据

    # 添加策略
    cerebro.addstrategy(SmaCrossStrategy,short_period=6, long_period=12, )

    # 添加分析器
    add_analyzers(cerebro)

    # 添加观察者
    cerebro.addobserver(bt.observers.Value)  # 监控账户价值变化
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Benchmark)

    # 配置 Broker 和 Sizer 模块
    leverage = 125  # 可以是 1 到 125 倍，动态调整
    configure_broker(cerebro, leverage)
    configure_sizer(cerebro)

    # 运行回测和参数调优
    results = cerebro.run(stdstats=False)

    print_result(results)

    cerebro.plot()