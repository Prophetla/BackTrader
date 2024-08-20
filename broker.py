import backtrader as bt

class CustomFuturesCommissionInfo(bt.CommInfoBase):
    params = (
        ('commission', 0.0), ('mult', 1.0), ('margin', None),
        ('commtype', bt.CommInfoBase.COMM_PERC),  # 佣金类型：百分比
        ('stocklike', False),  # 期货操作行为，不是股票
        ('percabs', True),  # 将 0.0005 理解为 0.05%
        ('interest', 0.0),
        ('interest_long', False),
        ('leverage', 1.0),
        ('automargin', False),
    )
    params = (
        ('commission', 0.0005),  # 佣金 0.05%
        ('mult', 1.0),  # 合约乘数
        ('margin', 0.1),  # 保证金比例
        ('commtype', bt.CommInfoBase.COMM_PERC),
        ('stocklike', False),  # 期货操作行为，不是股票
        ('percabs', True),  # 将 0.0005 理解为 0.05%
    )

    def _getcommission(self, size, price, pseudoexec):
        """
        计算每笔交易的佣金
        """
        # 使用绝对百分比来计算佣金
        return abs(size) * price * self.p.commission


def configure_broker(cerebro, leverage=1):
    """
    配置 Broker 模块，并根据所选杠杆倍率调整保证金比例
    """
    comm_info = CustomFuturesCommissionInfo(commission=0.0005)  # 设置佣金为 0.05%
    cerebro.broker.addcommissioninfo(comm_info)
    cerebro.broker.set_slippage_fixed(0.1)  # 固定滑点为 0.1
    cerebro.broker.setcash(100000.0)  # 初始资金设置