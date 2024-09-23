"""
基于SOLID原则
尽量在引入新变量时，添加类型提示和默认值（Type Hinting with Default Values），避免空值检查
"""
import numpy as np
import backtrader as bt
from datetime import timedelta
from collections import deque


class BaseStrategy(bt.Strategy):
    def __init__(self):
        self.last_cash: float
        self.last_value: float
        self.order: str
        self.openprice: float
        self.opencomm: float

    def start(self):
        """
        回测开始时的操作
        """
        self.last_cash = self.broker.get_cash()
        self.last_value = self.broker.get_value()
        self.log(f'回测开始，初始资金: {self.last_cash:.2f} USDT | 初始总值: {self.last_value:.2f} USDT', level='START',
                 doprint=True)

    def stop(self):
        """
        回测结束时的操作
        """
        final_cash = self.broker.get_cash()
        final_value = self.broker.get_value()
        overall_return = (final_value - self.last_value) / self.last_value * 100
        current_position_size = self.broker.getposition(self.data).size

        self.log(
            f'策略执行结束 | 最终现金: {final_cash:.4f} USDT | 最终账户总值: {final_value:.4f} | 当前持仓: {current_position_size:.4f} BTC | 总收益率: {overall_return:.2f}%',
            level='INFO')

    def log(self, message, level='INFO', doprint=True):
        """
        日志记录，支持不同级别的日志和时间戳
        """
        dt = self.datas[0].datetime.datetime(0) if len(self.data) else None
        formatted_message = f'[{level}] - {dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""} - {message}'
        if doprint:
            print(formatted_message)

    def log_order(self, order):
        """
        记录订单状态（可以进一步扩展记录更多信息）
        """
        pass

    def notify_order(self, order):
        """
        订单状态更新通知
        """
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'开仓，价格: {order.executed.price:.2f} USDT，成本: {order.executed.value:.3f} USDT，佣金费用: {order.executed.comm:.4f} USDT，成交量: {order.executed.size:.4f} BTC')
                self.buyprice = order.executed.price
                self.commprice = order.executed.comm

            elif order.issell():
                self.log(
                    f'平仓，价格: {order.executed.price:.2f} USDT，成本: {order.executed.value:.3f} USDT，佣金费用: {order.executed.comm:.4f} USDT，成交量: {order.executed.size:.4f} BTC')

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单被取消/保证金不足/拒绝，原因: {order.getstatusname()}', level='WARNING')

        # 清空订单
        self.order = None

    def notify_trade(self, trade):
        """
        交易完成通知
        """
        if not trade.isclosed:
            return
        self.log(f'交易平仓 | 盈亏: {trade.pnl:.2f} USDT | 净盈亏（含佣金）: {trade.pnlcomm:.2f} USDT')


def fibonacci_extension_custom(low, mid, multiple):
    """斐波那契倍数计算方法"""
    diff = mid - low
    fib_custom = mid + diff * multiple
    return fib_custom


class SystemOne(BaseStrategy):
    """
    系统一在小级别时间框架下运行，主要目的是：
    1.寻找好的信号K
    2.向系统二发出交易信号
    """
    params = (
        ('deque_length', 15),
    )

    def __init__(self):
        super().__init__()
        self.body = deque(maxlen=self.p.deque_length)  # 实体长度
        self.uppershadow = deque(maxlen=self.p.deque_length)  # 上影线长度
        self.lowershadow = deque(maxlen=self.p.deque_length)  # 下影线长度
        self.direction = deque(maxlen=self.p.deque_length)  # Bar的涨跌方向
        self.bar_type = deque(maxlen=self.p.deque_length)  # 柱体的类型
        self.volume = deque(maxlen=self.p.deque_length)  # 交易量
        self.range = deque(maxlen=self.p.deque_length)  # 价格波动范围
        self.low_price: float = .0  # 底部价格
        self.mid_price: float = .0  # 中部价格

    def next(self):
        # 获取当前的价格数据
        open_ = self.datas[0].open[0]
        close = self.datas[0].close[0]
        high = self.datas[0].high[0]
        low = self.datas[0].low[0]
        vol = self.datas[0].volume[0]
        range = high - low

        # 获取前一个Bar数据
        if len(self) > 1:
            prev_open = self.datas[0].open[-1]
            prev_close = self.datas[0].close[-1]
            prev_high = self.datas[0].high[-1]
            prev_low = self.datas[0].low[-1]
            prev_vol = self.datas[0].volume[-1]
        else:
            return  # 确保有足够的历史数据

        # 计算当前柱体的实体长度、上下影线长度
        body_length = abs(open_ - close)
        upper_shadow = high - max(open_, close)
        lower_shadow = min(open_, close) - low

        # 判断K线方向
        if open_ > close:
            direction = 1
        elif open_ == close:
            direction = 0
        else:
            direction = -1

        # 更新deque数据
        self.body.append(body_length)
        self.uppershadow.append(upper_shadow)
        self.lowershadow.append(lower_shadow)
        self.direction.append(direction)
        self.volume.append(vol)
        self.range.append(range)

        if self.position:
            return

        # 判断是否是两根连续的上涨 Bar，且成交量放大
        if close > open_ and prev_close > prev_open and vol > prev_vol:
            # 在最新Bar的最高价上方一个tick挂buy stop order
            buy_price = high + 0.1

            # 在前一根Bar的最低价出挂止损单
            stop_price = 0.9 * prev_low

            # 根据斐波那契回撤计算盈亏比的止盈价格
            fib_x = fibonacci_extension_custom(prev_low, buy_price, 1.5)

            # 使用Bracket Order一次性创建订单
            self.order = self.buy_bracket(
                price=buy_price,  # 买入触发价格
                exectype=bt.Order.Stop,
                valid=timedelta(minutes=5),
                stopprice=stop_price,  # 止损价格
                stopargs=dict(exectype=bt.Order.Stop,
                              # trailpecent=0.02,
                              valid=None, ),
                limitprice=fib_x,  # 止盈价格
                limitargs=dict(exectype=bt.Order.Limit, valid=None),

            )


class SystemTwo(SystemOne):
    """
    系统二，主要目的是：
    1.识别市场趋势
    2.判断系统一发出的交易信号是否合理
    """
    params = ()

    def __init__(self):
        super().__init__()

    def next(self):
        super().next()


# 定义价格密集区指标
class PriceCluster(bt.Indicator):
    lines = ('cluster', )
    params = dict(
        period=100,  # 统计过去多少根K线的数据
        bins=20      # 将价格划分为多少个区间
    )

    def __init__(self):
        self.addminperiod(self.p.period)

    def next(self):
        # 获取过去period周期内的收盘价
        prices = self.data.close.get(size=self.p.period)
        # 如果数据不足，跳过
        if len(prices) < self.p.period:
            return
        # 计算价格直方图
        hist, bin_edges = np.histogram(prices, bins=self.p.bins)
        # 找到出现频率最高的价格区间
        max_bin_index = np.argmax(hist)
        # 计算密集区的中心价格
        cluster_price = (bin_edges[max_bin_index] + bin_edges[max_bin_index + 1]) / 2
        # 将结果赋值给指标线
        self.lines.cluster[0] = cluster_price

# 定义策略，使用价格密集区指标
class PriceClusterStrategy(bt.Strategy):
    params = dict(
        period=100,
        bins=20
    )

    def __init__(self):
        self.cluster_indicator = PriceCluster(
            period=self.p.period,
            bins=self.p.bins
        )
        self.dataclose = self.data.close

    def next(self):
        cluster_price = self.cluster_indicator.cluster[0]
        # 检查指标是否有有效值
        if self.position:
            return

        if not np.isnan(cluster_price):
            if not self.position:
                if self.dataclose[0] < cluster_price:
                    self.buy(
                        exectype=bt.Order.Stop,
                        valid=timedelta(minutes=5),
                    )

            else:
                if self.dataclose[0] > cluster_price:
                    self.sell(
                        exectype=bt.Order.Stop,
                        valid=timedelta(minutes=5),
                    )


