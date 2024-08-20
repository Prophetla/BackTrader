import backtrader as bt


def add_analyzers(cerebro):
    """
    向 cerebro 添加所有的分析器。
    """
    analyzers = [
        ('SharpeRatio', bt.analyzers.SharpeRatio),
        ('DrawDown', bt.analyzers.DrawDown),
        ('TradeAnalyzer', bt.analyzers.TradeAnalyzer),
        ('Returns', bt.analyzers.Returns),
        ('AnnualReturn', bt.analyzers.AnnualReturn),
        ('GrossLeverage', bt.analyzers.GrossLeverage),
        ('SQN', bt.analyzers.SQN)
    ]

    for name, analyzer in analyzers:
        cerebro.addanalyzer(analyzer, _name=name)


def print_analyzer_results(strategy):
    """
    打印回测完成后的分析器结果。
    """
    try:
        drawdown = strategy.analyzers.DrawDown.get_analysis()
        returns = strategy.analyzers.Returns.get_analysis()
        trade_analyzer = strategy.analyzers.TradeAnalyzer.get_analysis()
        sqn_value = strategy.analyzers.SQN.get_analysis()

        # 杠杆率分析
        leverage_values = list(strategy.analyzers.GrossLeverage.get_analysis().values())
        if leverage_values:
            max_leverage = max(leverage_values)
            min_leverage = min(leverage_values)
            avg_leverage = sum(leverage_values) / len(leverage_values)
            print(f"最大杠杆率: {max_leverage:.2f}")
            print(f"最小杠杆率: {min_leverage:.2f}")
            print(f"平均杠杆率: {avg_leverage:.2f}")
        else:
            print("没有杠杆率数据可用")

        # 年化收益和最大回撤
        annual_return = returns.get('rnorm100', 0)
        max_drawdown = drawdown.max.drawdown
        risk_return_ratio = annual_return / max_drawdown if max_drawdown != 0 else float('inf')

        print(f'年化收益: {annual_return:.2f}%')
        print(f'最大回撤: {max_drawdown:.2f}%')
        print(f'年化收益/回撤比: {risk_return_ratio:.2f}')
        print(f'SQN: {sqn_value.get("sqn", "N/A")}')

        # 交易分析
        trade_stats = [
            ('总交易次数', trade_analyzer.total.total),
            ('盈利交易次数', trade_analyzer.won.total),
            ('亏损交易次数', trade_analyzer.lost.total),
            ('总净利润', trade_analyzer.pnl.net.total),
            ('盈利交易平均净利润', trade_analyzer.won.pnl.average),
            ('亏损交易平均净利润', trade_analyzer.lost.pnl.average)
        ]

        for stat_name, stat_value in trade_stats:
            print(f'{stat_name}: {stat_value}')

    except KeyError as e:
        print(f"无法提取分析器数据: {e}")
