import backtrader as bt
from strategy import SmaCrossStrategy  # 引入策略
from data_loader import load_data  # 引入数据加载模块
from broker import configure_broker  # 引入交易商模块
from sizer import configure_sizer  # 引入开平仓模块
from analyzer import add_analyzers, print_best_analyzer_results  # 引入分析器模块
from optimizer import select_best_strategy  # 引入最优策略选择模块

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 加载原始1分钟数据
    data_1min = load_data()

    # 添加1分钟数据到Cerebro，并且对其进行重新采样
    cerebro.adddata(data_1min)  # 原始1分钟数据

    # 使用optstrategy进行参数调优
    cerebro.addstrategy(SmaCrossStrategy)
    cerebro.optstrategy(
        SmaCrossStrategy,
        short_period=range(5, 7),  # 对短期均线周期进行调优
        long_period=range(10, 12),  # 对长期均线周期进行调优
    )

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
    optimized_runs = cerebro.run(stdstats=False)

    # 打印优化后的分析器结果
    print_best_analyzer_results(optimized_runs)

    # 使用封装后的优化器模块选择最优策略
    best_strategy, best_value = select_best_strategy(optimized_runs, criterion='return')

    # 确保有最优策略后进行绘图
    if best_strategy:
        # 从best_strategy中提取最优参数
        best_short_period = best_strategy.params.short_period
        best_long_period = best_strategy.params.long_period

        # 使用最优参数重新运行策略并绘图
        cerebro = bt.Cerebro()
        cerebro.adddata(data_1min)
        cerebro.addstrategy(SmaCrossStrategy,
                            short_period=best_short_period,
                            long_period=best_long_period)

        configure_broker(cerebro, leverage)
        configure_sizer(cerebro)

        # 只重新运行最优策略一次以生成绘图数据
        cerebro.run()

        # 绘制回测图表 candlestick line
        cerebro.plot(style='line', barup='green', bardown='red', figsize=(32, 20), dpi=100, volume=False)
    else:
        print("没有找到最优策略")
