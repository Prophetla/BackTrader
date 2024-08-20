import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_equity_curve(strategy):
    """
    绘制资金曲线图
    """
    equity_curve = strategy.equity_curve
    plt.figure(figsize=(10, 6))
    plt.plot(equity_curve, label='Equity Curve')
    plt.title('Equity Curve')
    plt.xlabel('Time')
    plt.ylabel('Account Value')
    plt.legend()
    plt.show()


def plot_drawdown_curve(strategy):
    """
    绘制回撤曲线
    """
    # 使用策略记录的 drawdown_curve 列表
    drawdown_curve = strategy.drawdown_curve

    # 绘制回撤曲线
    plt.figure(figsize=(16, 10))
    plt.plot(drawdown_curve, label='Drawdown Curve', color='red')
    plt.title(f'Drawdown Curve (Max Drawdown: {max(drawdown_curve):.2f}%)')
    plt.xlabel('Time')
    plt.ylabel('Drawdown (%)')
    plt.legend()
    plt.show()


def plot_trade_analysis(strategy):
    """
    绘制交易分析，包括盈利和亏损交易数量的柱状图
    """
    trade_analyzer = strategy.analyzers.TradeAnalyzer.get_analysis()

    # 获取交易数据
    trade_data = {
        'Won Trades': trade_analyzer.won.total,
        'Lost Trades': trade_analyzer.lost.total
    }

    # 构建 DataFrame
    df = pd.DataFrame({
        'Trade Type': list(trade_data.keys()),
        'Count': list(trade_data.values())
    })

    # 使用 hue 参数来控制颜色
    plt.figure(figsize=(16, 10))
    sns.barplot(x='Trade Type', y='Count', hue='Trade Type', data=df, palette={'Won Trades': 'green', 'Lost Trades': 'red'}, legend=False)

    plt.title('Trade Analysis')
    plt.ylabel('Number of Trades')
    plt.show()


def plot_combined_equity_and_drawdown(strategy):
    """
    绘制资金曲线和回撤曲线在同一图像中
    """
    equity_curve = strategy.equity_curve
    drawdown_curve = strategy.drawdown_curve

    # 创建图像和双Y轴
    fig, ax1 = plt.subplots(figsize=(16, 10))

    # 绘制资金曲线 (左Y轴)
    color = 'tab:blue'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Account Value', color=color)
    ax1.plot(equity_curve, label='Equity Curve', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # 创建第二个Y轴 (右Y轴) 并绘制回撤曲线
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Drawdown (%)', color=color)
    ax2.plot(drawdown_curve, label='Drawdown Curve', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # 添加标题和图例
    fig.suptitle('Equity Curve and Drawdown Curve')
    # fig.tight_layout()  # 调整布局以防止重叠
    plt.show()