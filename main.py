import backtrader as bt
from strategy import BaseStrategy, SmaCrossStrategy  # 引入策略
from data_loader import load_data  # 引入数据加载模块
from broker import configure_broker  # 引入交易商模块
from sizer import configure_sizer  # 引入开平仓模块
from analyzer import add_analyzers, print_analyzer_results  # 引入分析器模块
from visualization import plot_equity_curve, plot_drawdown_curve, plot_trade_analysis, plot_combined_equity_and_drawdown


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 加载原始1分钟数据
    data_1min = load_data()

    # 添加1分钟数据到Cerebro，并且对其进行重新采样
    cerebro.adddata(data_1min)  # 原始1分钟数据

    # 添加策略
    # cerebro.addstrategy(SmaCrossStrategy, short_period=15, long_period=50)

    # 使用optstrategy进行参数调优
    cerebro.optstrategy(
        SmaCrossStrategy,
        short_period=range(5, 10),  # 对短期均线周期进行调优
        long_period=range(15, 30,)  # 对长期均线周期进行调优
    )

    # 添加分析器
    add_analyzers(cerebro)

    # 添加观察者
    cerebro.addobserver(bt.observers.Value)  # 监控账户价值变化
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Benchmark)


    # 配置 Broker 和 Sizer 模块
    # 允许用户选择杠杆倍数
    leverage = 125  # 可以是 1 到 125 倍，动态调整
    configure_broker(cerebro, leverage)
    configure_sizer(cerebro)

    # 配置 Writer 模块，将回测数据输出到控制台
    # cerebro.addwriter(bt.WriterFile, out=None)  # out=None 表示输出到控制台

    # 运行回测
    result = cerebro.run(stdstats=False)  # 默认 stdstats = True

    # 提取并打印分析器结果
    strat = result[0]
    print_analyzer_results(strat)


    # 打印最终资金
    # final_value = cerebro.broker.getvalue()
    # print(f'最终资金: {final_value:.2f}')

    # # 绘制可视化图表
    # plot_equity_curve(strat)
    # plot_drawdown_curve(strat)
    # plot_trade_analysis(strat)
    # plot_combined_equity_and_drawdown(strat)

    # 绘制回测图表
    # 参数 style 'candlestick' K线, 'renko' 美国线, 'line' 折线
    cerebro.plot(style='candlestick', barup='green', bardown='red', figsize=(32, 20), dpi=100, volume=False)
