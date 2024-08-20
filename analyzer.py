import backtrader as bt


def add_analyzers(cerebro):
    """
    向 cerebro 添加所有的分析器。
    """
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.GrossLeverage, _name='GrossLeverage')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN')


def print_best_analyzer_results(optimized_runs, criterion='return', output_file='/Users/prophetl/PycharmProjects/BackTrader/results.txt'):
    """
    打印最优策略的分析结果或单一策略的分析结果到txt文件
    :param optimized_runs: 优化后的策略列表或单一策略运行结果
    :param criterion: 选择最优策略的标准, 'return' 或 'sqn'
    :param output_file: 输出结果的文件路径
    """
    with open(output_file, 'w') as f:
        # 如果 optimized_runs 是单一策略的运行结果，直接打印分析结果
        if isinstance(optimized_runs, list) and isinstance(optimized_runs[0], bt.Strategy):
            strat = optimized_runs[0]
            f.write("未进行参数优化，直接打印单一策略的分析结果：\n")
            _print_analyzer_results(strat, f)
        else:
            # 否则假设进行了参数优化，选择最优策略并打印结果
            best_strategy = None
            best_value = -float('inf')

            # 根据指定标准找到最优策略
            for strat_list in optimized_runs:  # 遍历优化运行结果的外层列表
                for strat in strat_list:  # 遍历每个策略实例
                    if criterion == 'return':
                        # 使用年化收益作为最优标准
                        returns = strat.analyzers.Returns.get_analysis()
                        annual_return = returns.get('rnorm100', 0)
                        if annual_return > best_value:
                            best_value = annual_return
                            best_strategy = strat
                    elif criterion == 'sqn':
                        # 使用 SQN 作为最优标准
                        sqn_value = strat.analyzers.SQN.get_analysis()
                        sqn = sqn_value['sqn']
                        if sqn > best_value:
                            best_value = sqn
                            best_strategy = strat

            # 打印最优策略的分析结果
            if best_strategy:
                f.write("已进行参数优化，打印最优策略的分析结果：\n")
                _print_analyzer_results(best_strategy, f)
            else:
                f.write("未找到最优策略\n")


def _print_analyzer_results(strategy, file_handle):
    """
    打印指定策略的分析结果到文件
    :param strategy: 策略对象
    :param file_handle: 文件句柄
    """
    file_handle.write(f"策略参数: 短期均线周期={strategy.params.short_period}, 长期均线周期={strategy.params.long_period}\n")

    # 获取分析结果
    drawdown = strategy.analyzers.DrawDown.get_analysis()
    returns = strategy.analyzers.Returns.get_analysis()
    trade_analyzer = strategy.analyzers.TradeAnalyzer.get_analysis()
    sqn_value = strategy.analyzers.SQN.get_analysis()

    # 在回测完成后提取杠杆率信息
    gross_leverage = strategy.analyzers.GrossLeverage.get_analysis()
    leverage_values = list(gross_leverage.values())

    # 计算最大、最小和平均杠杆率
    if leverage_values:
        max_leverage = max(leverage_values)
        min_leverage = min(leverage_values)
        avg_leverage = sum(leverage_values) / len(leverage_values)

        file_handle.write(f"最大杠杆率: {max_leverage:.6f}\n")
        file_handle.write(f"最小杠杆率: {min_leverage:.6f}\n")
        file_handle.write(f"平均杠杆率: {avg_leverage:.6f}\n")
    else:
        file_handle.write("没有杠杆率数据可用\n")

    # 年化收益和最大回撤
    annual_return = returns.get('rnorm100', 0)
    max_drawdown = drawdown.max.drawdown
    risk_return_ratio = annual_return / max_drawdown if max_drawdown != 0 else float('inf')

    # 打印结果
    file_handle.write(f'年化收益: {annual_return:.2f}%\n')
    file_handle.write(f'最大回撤: {max_drawdown:.2f}%\n')
    file_handle.write(f'年化收益/回撤比: {risk_return_ratio:.2f}\n')
    file_handle.write(f'SQN: {sqn_value["sqn"]}\n')

    # 交易分析结果
    file_handle.write(f'总交易次数: {trade_analyzer.total.total}\n')
    file_handle.write(f'盈利交易次数: {trade_analyzer.won.total}\n')
    file_handle.write(f'亏损交易次数: {trade_analyzer.lost.total}\n')
    file_handle.write(f'总净利润: {trade_analyzer.pnl.net.total}\n')
    file_handle.write(f'盈利交易平均净利润: {trade_analyzer.won.pnl.average}\n')
    file_handle.write(f'亏损交易平均净利润: {trade_analyzer.lost.pnl.average}\n')
    file_handle.write('----------------------------\n')