import backtrader as bt
from datetime import datetime, timedelta

class TradingMetricsAnalyzer(bt.Analyzer):
    def __init__(self):
        self.trade_count = 0
        self.profit_trade_count = 0  # 盈利交易次数
        self.profits = []
        self.losses = []
        self.total_pnl = 0.0  # 累计净利润百分比
        self.max_net_worth = 0.0  # 记录净值新高
        self.max_net_worth_times = []  # 记录净值创新高的时间点
        self.first_trade_time = None  # 记录第一次交易的时间
        self.last_trade_time = None  # 记录最后一次交易的时间

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trade_count += 1
            pnl = trade.pnlcomm  # 获取扣除佣金后的净利润

            # 使用账户总值来计算总盈利百分比
            account_value = self.strategy.broker.getvalue()
            if account_value > 0:
                # 累计总盈利百分比（基于账户总值）
                self.total_pnl += (pnl / account_value) * 100

                # 更新盈利和亏损
                if pnl > 0:
                    self.profit_trade_count += 1
                    self.profits.append(pnl)
                else:
                    self.losses.append(abs(pnl))

                # 记录净值新高及其时间
                current_time = self.strategy.data.datetime.datetime(0)
                if account_value > self.max_net_worth:
                    self.max_net_worth = account_value
                    self.max_net_worth_times.append(current_time)

            # 记录第一次和最后一次交易的时间
            if self.first_trade_time is None:
                self.first_trade_time = self.strategy.data.datetime.datetime(0)
            self.last_trade_time = self.strategy.data.datetime.datetime(0)

    def get_analysis(self):
        total_trades = self.trade_count
        total_profit = sum(self.profits)
        total_loss = sum(self.losses)

        avg_profit = total_profit / len(self.profits) if self.profits else 0
        avg_loss = total_loss / len(self.losses) if self.losses else 0

        profit_loss_ratio = (avg_profit / avg_loss) if avg_loss != 0 else None

        win_rate = (self.profit_trade_count / total_trades) * 100 if total_trades > 0 else 0

        max_profit = max(self.profits, default=0)
        max_loss = max(self.losses, default=0)

        # 计算交易频率（交易次数 / 时间段）
        trade_duration = (self.last_trade_time - self.first_trade_time).days + 1 if self.first_trade_time and self.last_trade_time else 1
        trade_frequency = total_trades / trade_duration if trade_duration > 0 else 0

        # 计算平均净值创新高时间
        if len(self.max_net_worth_times) > 1:
            intervals = [(self.max_net_worth_times[i] - self.max_net_worth_times[i-1]).days for i in range(1, len(self.max_net_worth_times))]
            avg_new_high_time = sum(intervals) / len(intervals)
        else:
            avg_new_high_time = None

        return {
            'total_trades': total_trades,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_loss_ratio': profit_loss_ratio,
            'average_profit': avg_profit,
            'average_loss': avg_loss,
            'total_pnl_percent': self.total_pnl,
            'win_rate': win_rate,
            'max_profit_trade': max_profit,
            'max_loss_trade': max_loss,
            'trade_frequency_per_day': trade_frequency,  # 交易频率
            'average_new_high_time': avg_new_high_time,  # 平均净值创新高时间
        }

def add_analyzers(cerebro):
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='Drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.GrossLeverage, _name='GrossLeverage')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN')
    cerebro.addanalyzer(TradingMetricsAnalyzer, _name='TradingMetrics')

def print_result(results, output_file='results.txt'):
    try:
        with open(output_file, 'w') as f:
            for strat in results:
                if isinstance(strat, bt.Strategy):
                    f.write("=" * 40 + "\n")
                    f.write("策略参数:\n")
                    f.write("=" * 40 + "\n")
                    for param_name in strat.params._getkeys():
                        param_value = getattr(strat.params, param_name)
                        f.write(f"{param_name}: {param_value}\n")
                    f.write("=" * 40 + "\n")

                    trading_metrics = strat.analyzers.TradingMetrics.get_analysis()
                    f.write(f"总盈利: {trading_metrics['total_profit']:.2f} USDT\n")
                    f.write(f"总亏损: {trading_metrics['total_loss']:.2f} USDT\n")
                    f.write(f"最大盈利单笔交易: {trading_metrics['max_profit_trade']:.2f} USDT\n")
                    f.write(f"最大亏损单笔交易: {trading_metrics['max_loss_trade']:.2f} USDT\n")
                    f.write(f"平均盈利: {trading_metrics['average_profit']:.2f} USDT\n")
                    f.write(f"平均亏损: {trading_metrics['average_loss']:.2f} USDT\n")
                    f.write(f"盈亏比: {trading_metrics['profit_loss_ratio']:.2f}\n" if trading_metrics['profit_loss_ratio'] else "盈亏比: N/A\n")
                    f.write("=" * 40 + "\n")
                    f.write(f"总盈利百分比: {trading_metrics['total_pnl_percent']:.2f}%\n")
                    f.write(f"交易频率（每日交易次数）: {trading_metrics['trade_frequency_per_day']:.2f}\n")
                    f.write(f"平均净值创新高时间（天）: {trading_metrics['average_new_high_time']:.2f}\n" if trading_metrics['average_new_high_time'] is not None else "平均净值创新高时间: N/A\n")
                    f.write("=" * 40 + "\n")
                    f.write(f"总交易次数: {trading_metrics['total_trades']}\n")
                    f.write(f"胜率: {trading_metrics['win_rate']:.2f}%\n")
                    f.write("=" * 40 + "\n")
                    f.write("=" * 40 + "\n")

                    drawdown = strat.analyzers.Drawdown.get_analysis()

                    # 使用 drawdown.max.len
                    max_drawdown_days = drawdown.max.len /6

                    f.write(f"最大回撤金额: {drawdown.max.moneydown:.2f} USDT\n")
                    f.write(f"最大回撤百分比: {drawdown.max.drawdown:.2f}%\n")
                    f.write(f"最长回撤天数: {max_drawdown_days:.1f}\n")
                    f.write("=" * 40 + "\n")

            print("结果导出成功")
    except Exception as e:
        print(f"Error writing to file: {e}")