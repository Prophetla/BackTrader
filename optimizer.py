# optimizer.py

def select_best_strategy(optimized_runs, criterion='return'):
    """
    根据指定的标准选择最优策略。
    当前支持的标准：'return'（年化收益）和 'sqn'（策略质量数值）
    """
    best_strategy = None
    best_value = -float('inf')

    for strat_list in optimized_runs:
        for strat in strat_list:
            if criterion == 'return':
                # 基于年化收益选择最优策略
                returns = strat.analyzers.Returns.get_analysis()
                annual_return = returns.get('rnorm100', 0)
                if annual_return > best_value:
                    best_value = annual_return
                    best_strategy = strat
            elif criterion == 'sqn':
                # 基于策略质量数值（SQN）选择最优策略
                sqn_value = strat.analyzers.SQN.get_analysis()
                sqn = sqn_value['sqn']
                if sqn > best_value:
                    best_value = sqn
                    best_strategy = strat

    return best_strategy, best_value
