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


def print_result(results, output_file='/Users/prophetl/PycharmProjects/BackTrader/results.txt'):
    """
    打印单一策略的分析结果到txt文件，并备注策略参数。
    :param results: 单一策略运行结果
    :param output_file: 输出结果的文件路径
    """
    try:
        with open(output_file, 'w') as f:
            for strat in results:
                if isinstance(strat, bt.Strategy):
                    f.write("=" * 40 + "\n")
                    f.write("策略参数:\n")
                    for param_name in strat.params._getkeys():
                        param_value = getattr(strat.params, param_name)
                        f.write(f"{param_name}: {param_value}\n")

                    f.write("Sharpe Ratio: {}\n".format(strat.analyzers.SharpeRatio.get_analysis().get('sharperatio', 'N/A')))
                    f.write("最大回撤: {}\n".format(strat.analyzers.DrawDown.get_analysis().get('max', {}).get('drawdown', 'N/A')))
                    f.write("年化收益: {}\n".format(strat.analyzers.Returns.get_analysis().get('rnorm100', 'N/A')))
                    f.write("SQN: {}\n".format(strat.analyzers.SQN.get_analysis().get('sqn', 'N/A')))
                    f.write("=" * 40 + "\n")
            print("Single strategy results successfully written.")
    except Exception as e:
        print(f"Error writing to file: {e}")
