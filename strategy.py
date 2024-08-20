import backtrader as bt


class BaseStrategy(bt.Strategy):
    """
    基础策略类，定义了处理订单、交易、资金变动等通知的方法。
    所有继承此类的策略都可以自动使用这些通知方法。
    """

    def __init__(self):
        self.last_cash = None
        self.last_value = None

    def start(self):
        # 在回测开始时初始化资金和账户总值
        self.last_cash = self.broker.get_cash()
        self.last_value = self.broker.get_value()

    def log_order(self, order, action):
        """处理订单的日志输出，通用化买卖操作日志。"""
        self.log(f'{action}执行。价格: {order.executed.price}, 数量: {order.executed.size}, '
                 f'成本: {order.executed.value}, 手续费: {order.executed.comm}')

    def notify_order(self, order):
        """处理订单状态的变化。"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            if order.isbuy():
                self.log_order(order, '买单')
            elif order.issell():
                self.log_order(order, '卖单')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/被拒绝')

        # 重置订单状态
        self.order = None


    def notify_trade(self, trade):
        """处理交易状态的变化。"""
        if trade.isclosed:
            self.log(f'交易已平仓。毛收益: {trade.pnl}, 净收益: {trade.pnlcomm}')
        elif trade.isopen:
            self.log(f'交易已开仓。仓位数量: {trade.size}')

    def notify_cashvalue(self, cash, value):
        """只在现金或账户总值发生变化时记录日志。"""
        if cash != self.last_cash or value != self.last_value:
            self.log(f'当前现金: {cash}, 当前账户总值: {value}')
            # 更新上次的现金和账户总值
            self.last_cash = cash
            self.last_value = value

    # def notify_fund(self, cash, value, fundvalue, shares):
    #     """处理基金的现金、净值和份额更新。"""
    #     self.log(f'基金现金: {cash}, 基金总值: {value}, 净值: {fundvalue}, 份额: {shares}')

    def notify_timer(self, timer, when, *args, **kwargs):
        """处理定时器触发通知。"""
        self.log(f'定时器触发时间: {when}')

    def notify_store(self, msg, *args, **kwargs):
        """处理来自存储提供者的通知（如经纪商或数据提供者）。"""
        self.log(f'存储通知: {msg}')

    def notify_data(self, data, status, *args, **kwargs):
        """处理数据状态的变化通知。"""
        self.log(f'数据状态通知: {data._getstatusname(status)}')

    def log(self, message):
        """日志输出工具方法，打印带日期和时间（精确到分钟）的日志信息。"""
        dt = self.datas[0].datetime.datetime(0)  # 直接获取包含日期和时间的 datetime 对象
        print(f'{dt.strftime("%Y-%m-%d %H:%M")}: {message}')


class SmaCrossStrategy(BaseStrategy):
    """
    双均线交叉策略。当短期均线（短期SMA）上穿长期均线（长期SMA）时买入，
    当短期均线下穿长期均线时卖出。
    """

    params = (
        ('short_period', 10),  # 短期均线周期
        ('long_period', 30),   # 长期均线周期
    )

    def __init__(self):
        # 初始化短期和长期均线指标
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

        # 记录订单状态
        self.order = None

    def next(self):
        """在每个新的数据点上进行策略判断和调试。"""
        # 继续策略逻辑

        # 检查是否有未完成的订单，避免重复下单
        if self.order:
            return

        # 检查是否持有头寸
        if not self.position:
            # 如果短期均线从下方上穿长期均线，则买入
            if self.sma_short[0] > self.sma_long[0] and self.sma_short[-1] <= self.sma_long[-1]:
                self.log(f'短期均线上穿，买入。价格: {self.data.close[0]}')
                self.order = self.buy()

        else:
            # 如果短期均线从上方下穿长期均线，则卖出
            if self.sma_short[0] < self.sma_long[0] and self.sma_short[-1] >= self.sma_long[-1]:
                self.log(f'短期均线下穿，卖出。价格: {self.data.close[0]}')
                self.order = self.sell()


