import backtrader as bt


# class CustomFuturesCommissionInfo(bt.CommInfoBase):
#     """
#     自定义期货佣金信息类，用于配置期货交易的佣金、保证金和杠杆等信息。
#     """
#     params = (
#         ('commission', 0.0005),  # 佣金 0.05%
#         ('mult', 1.0),  # 合约乘数
#         ('margin', 0.5),  # 保证金比例
#         ('commtype', bt.CommInfoBase.COMM_PERC),  # 百分比佣金
#         ('stocklike', False),  # 标的为期货
#         ('percabs', True),  # 将 0.0005 解释为 0.05%
#         ('interest', 0.02),  # 利率
#         ('interest_long', False),  # 不对多头计算利息
#         ('leverage', 1),  # 杠杆倍数
#         ('automargin', True),  # 自动管理保证金
#     )
#
#     def _getcommission(self, size, price, pseudoexec):
#         """
#         计算每笔交易的佣金。
#         """
#         return abs(size) * price * self.p.commission
#
#     def get_margin(self, price, size=0.5):
#         """
#         计算持仓的保证金要求。
#         """
#         return abs(size) * price * self.p.margin * self.p.mult
#
#     def get_leverage(self):
#         """
#         获取杠杆倍数。
#         """
#         return self.p.leverage


# def configure_broker(cerebro):
#     """
#     配置 Cerebro 的 Broker，包括佣金、滑点和初始资金。
#     """
#     comm_info = CustomFuturesCommissionInfo()
#
#     # 配置 Broker
#     cerebro.broker.addcommissioninfo(comm_info)
#     cerebro.broker.set_slippage_fixed(0)  # 固定滑点
#     cerebro.broker.set_cash(10000.0)  # 设置初始资金


import backtrader as bt


class CustomFuturesCommissionInfo(bt.CommInfoBase):
    """
    自定义期货佣金信息类，动态调整杠杆和维持保证金率
    """
    params = (
        ('maker_commission', 0.0002),
        ('taker_commission', 0.0005),
        ('mult', 1.0),
        ('commtype', bt.CommInfoBase.COMM_PERC),
        ('stocklike', False),
        ('percabs', True),
        ('interest', 0.02),
        ('interest_long', False),
        ('leverage', 1),
        ('automargin', True),
    )

    # 杠杆对应的维持保证金率
    leverage_margin_map = {
        1: 0.50,
        2: 0.25,
        3: 0.15,
        4: 0.125,
        5: 0.10,
        10: 0.05,
        20: 0.025,
        25: 0.02,
        50: 0.01,
        75: 0.0065,
        100: 0.005,
        125: 0.004,
    }

    def get_margin(self, price):
        """
        根据杠杆动态调整保证金
        """
        leverage = self.p.leverage
        # 根据杠杆获取对应的维持保证金率
        margin_rate = self.leverage_margin_map.get(leverage, 0.5)  # 默认1倍杠杆对应50%保证金率

        # 根据当前价格和维持保证金率计算单手保证金
        return price * self.p.mult * margin_rate

    def get_leverage(self):
        """
        获取杠杆倍数
        """
        return self.p.leverage

    def _getcommission(self, size, price, pseudoexec):
        """
        根据订单类型动态计算佣金。
        假设市场订单为吃单，限价订单为挂单。
        """
        if pseudoexec:  # 判断是否为限价单
            return abs(size) * price * self.p.maker_commission
        else:  # 市价单默认为吃单
            return abs(size) * price * self.p.taker_commission

    def get_margin(self, price):
        """
        保留默认的get_margin方法，根据源码计算保证金。
        """
        if not self.p.automargin:
            return self.p.margin
        elif self.p.automargin < 0:
            return price * self.p.mult
        return price * self.p.automargin  # int/float expected

    def calculate_total_margin(self, price, size):
        """
        新增一个函数来计算总保证金，基于每单位保证金计算总量。
        """
        return self.get_margin(price) * abs(size)

    def calculate_interest(self, size, price, days_held):
        """
        计算持仓的利息成本，假设按天计算利息。
        :param size: 持仓量
        :param price: 当前价格
        :param days_held: 持仓时间（天）
        :return: 持仓利息
        """
        if self.p.interest_long and size > 0:
            return abs(size) * price * self.p.interest * days_held
        return 0


def configure_broker(cerebro, leverage=10, margin=0.05, cash=10000.0, slippage=0.1):

    comm_info = CustomFuturesCommissionInfo(leverage=leverage, margin=margin)

    # 配置 Broker
    cerebro.broker.addcommissioninfo(comm_info)
    cerebro.broker.set_slippage_fixed(slippage)  # 动态设置滑点
    cerebro.broker.set_cash(cash)  # 设置初始资金