import backtrader as bt

class FixedPercentSizer(bt.Sizer):
    params = (
        ('percent', 0.1),  # 使用账户总权益的10%
        ('min_stake', 0.001),  # 最小仓位单位 0.001BTC
        ('min_leverage', 1),   # 最小杠杆
        ('max_leverage', 125), # 最大杠杆（币安的最大杠杆为125倍）
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        # 检查百分比参数的合法性
        if self.p.percent <= 0 or self.p.percent > 1:
            raise ValueError("Percent must be between 0 and 1.")
        if self.p.min_stake <= 0:
            raise ValueError("min_stake must be positive.")

        # 获取账户总权益
        total_value = self.broker.getvalue()

        # 获取杠杆并进行上下限控制
        leverage = comminfo.get_leverage()
        leverage = max(self.p.min_leverage, min(self.p.max_leverage, leverage))

        # 动态获取维持保证金率
        margin_rate = comminfo.leverage_margin_map.get(leverage, 0.5)  # 默认1倍杠杆对应50%

        # 计算账户可以用来交易的总资金，并考虑维持保证金率
        stake_value = total_value * self.p.percent * leverage
        price = data.close[0]

        # 计算交易量
        stake = stake_value / price
        stake = max(self.p.min_stake, round(stake / self.p.min_stake) * self.p.min_stake)

        # 计算维持保证金所需的资金，确保账户有足够的资金支持维持保证金
        margin_needed = stake * price * margin_rate

        if margin_needed > cash:
            # 如果资金不足以支持维持保证金，不开仓
            return 0

        # 买入交易时直接返回计算的stake
        if isbuy:
            return stake
        else:
            # 卖出交易时根据现有仓位决定交易量
            position = self.broker.getposition(data)
            return min(stake, position.size)



class FixedSizeSizer(bt.Sizer):
    params = (
        ('fixed_size', 0.01),  # 每次交易固定为 0.01 BTC
        ('max_percent', 0.1),   # 最大持仓量不超过账户总权益的 10%
        ('min_stake', 0.001),  # 最小仓位单位 0.001 BTC
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        price = data.close[0]
        total_value = self.broker.getvalue()

        # 获取杠杆，并根据杠杆计算维持保证金率
        leverage = comminfo.get_leverage()
        margin_rate = comminfo.leverage_margin_map.get(leverage, 0.5)

        # 计算账户允许的最大持仓量
        max_btc_allowed = (total_value * self.p.max_percent) / price
        current_position = self.broker.getposition(data).size
        available_to_add = max_btc_allowed - abs(current_position)

        # 根据现有持仓量和最大允许持仓量计算实际交易量
        trade_size = min(self.p.fixed_size, available_to_add)

        # 确保交易量不低于最小仓位单位
        trade_size = max(self.p.min_stake, round(trade_size / self.p.min_stake) * self.p.min_stake)

        # 计算维持保证金所需的资金，确保账户有足够的资金支持维持保证金
        margin_needed = trade_size * price * margin_rate

        if margin_needed > cash:
            # 如果资金不足以支持维持保证金，不下单
            return 0

        return trade_size


# 配置 Sizer
def configure_sizer(cerebro):
    # 使用自定义的 Sizer
    cerebro.addsizer(FixedPercentSizer)
    # cerebro.addsizer(FixedSizeSizer)