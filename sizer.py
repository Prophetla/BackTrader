import backtrader as bt


class CustomSizer(bt.Sizer):
    params = (('stake', 1),)  # 默认仓位大小

    def _getsizing(self, comminfo, cash, data, isbuy):
        # 仓位管理逻辑
        max_stake = min(cash // data.close[0], self.params.stake)
        return max_stake

def configure_sizer(cerebro):
    """
    配置 Sizer 模块
    """
    cerebro.addsizer(CustomSizer)