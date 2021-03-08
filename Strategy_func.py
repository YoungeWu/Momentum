import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# 标准的动量策略
def SMBmomentum(data, index_numbers, freq="month"):
    time_step = data.shape[0]
    hold_list = pd.DataFrame()
    value_list = pd.DataFrame()
    return_list = pd.DataFrame()

    if freq == "month":
        hold = []
        for month in range(time_step):
            # 算持仓
            month_return = data.iloc[month, :]
            sorted_return = month_return.sort_values(ascending=False)
            new_hold = list(sorted_return.index[: index_numbers])
            hold_list = hold_list.append([new_hold])

            # 算收益
            hold_num = len(hold)
            if hold_num == 0:
                value_list = value_list.append([1])
                return_list = return_list.append([0])
            else:
                returns = 0
                value = value_list.iloc[month - 1]
                for index in hold:
                    index_returns = data[index].iloc[month]
                    value = value + value_list.iloc[month - 1] / hold_num * index_returns
                    returns = returns + index_returns / hold_num

                value_list = value_list.append([value])
                return_list = return_list.append([returns])

            # 更新持仓
            hold = new_hold

    # 重载 收益率为季度的算法
    else:
        hold = []
        # seq是value list的长度
        seq = 0
        for month in range(2, time_step, 3):
            # 算持仓
            if month >= 2:
                season_return = data.iloc[month-2, :] + data.iloc[month-1, :] + data.iloc[month, :]
                sorted_return = season_return.sort_values(ascending=False)
                new_hold = list(sorted_return.index[: index_numbers])
                hold_list = hold_list.append([new_hold])
            else:
                new_hold = []

            # 算收益
            hold_num = len(hold)
            if hold_num == 0:
                value_list = value_list.append([1])
                return_list = return_list.append([0])
                seq += 1
            else:
                returns = 0
                value = value_list.iloc[seq - 1]
                for index in hold:
                    index_returns = data[index].iloc[month-2] + data[index].iloc[month-1] + data[index].iloc[month]
                    value = value + value_list.iloc[seq-1] / hold_num * index_returns
                    returns = returns + index_returns/hold_num

                value_list = value_list.append([value])
                return_list = return_list.append([returns])
                seq += 1

            # 更新持仓
            hold = new_hold

    return [return_list, value_list]


# 单一指标策略
def single_momentum(strategy_returns, signal, signal_returns):
    # 获取数据长度
    time_len = strategy_returns.shape[0]
    returns = strategy_returns
    for i in range(1, time_len):
        # 计算几个指标有买入信号
        signals = 0
        for j in range(signal.shape[1]):
            signals += signal.iloc[i, j]
        # 算收益
        if signals >= 1:
            returns.iloc[i, 0] = signal_returns.iloc[i, 0]
        else:
            returns.iloc[i, 0] = strategy_returns.iloc[i, 0]

    # 计算调整后的净值
    values = pd.DataFrame([1])
    for i in range(1, time_len):
        values = values.append([values.iloc[i-1, 0] * (1 + returns.iloc[i, 0])])

    return [values, returns]


# 多个指标
def multiple_momentum(strategy_returns, signal, signal_returns, signal_num=3):  # 参考几个指标，x和y是多少
    # 获取数据长度
    time_len = strategy_returns.shape[0]
    returns = strategy_returns
    for i in range(1, time_len):
        # 计算几个指标有买入信号
        signals = 0
        for j in range(signal.shape[1]):
            signals += signal.iloc[i, j]
        if signals >= signal_num:
            returns.iloc[i, 0] = signal_returns.iloc[i, 0]
        else:
            returns.iloc[i, 0] = strategy_returns.iloc[i, 0]

    # 计算调整后的净值
    values = pd.DataFrame([1])
    for i in range(1, time_len):
        values = values.append([values.iloc[i-1, 0] * (1 + returns.iloc[i, 0])])

    return [values, returns]


# x%个指标
def proportional_momentum(strategy_returns, signal, signal_returns, x):  # 参考几个指标，x和y是多少
    # 获取数据长度
    time_len = strategy_returns.shape[0]
    returns = strategy_returns
    for i in range(1, time_len):
        # 计算几个指标有买入信号
        signals = 0
        for j in range(signal.shape[1]):
            signals += signal.iloc[i, j]
        returns.iloc[i, 0] = (signals/3)*signal_returns.iloc[i, 0]+(1-signals/3)*strategy_returns.iloc[i, 0]

    # 计算调整后的净值
    values = pd.DataFrame([1])
    for i in range(1, time_len):
        values = values.append([values.iloc[i-1, 0] * (1 + returns.iloc[i, 0])])

    return [values, returns]


# 止损策略
def stop_momentum(strategy_returns, signal_returns, y):  # 参考几个指标，x和y是多少
    # 获取数据长度
    time_len = strategy_returns.shape[0]
    returns = strategy_returns
    for i in range(1, time_len):
        if (strategy_returns.iloc[i-1, 0]) < y:
            returns.iloc[i, 0] = signal_returns.iloc[i, 0]
        else:
            returns.iloc[i, 0] = strategy_returns.iloc[i, 0]

    # 计算调整后的净值
    values = pd.DataFrame([1])
    for i in range(1, time_len):
        values = values.append([values.iloc[i-1, 0] * (1 + returns.iloc[i, 0])])

    return [values, returns]


def performance_eval(returns, value, riskfree_rate):
    # 先转化成通用的pd.DataFrame格式
    returns = pd.DataFrame(returns)
    values = pd.DataFrame(value)
    # 再转化成np.array格式（历史遗留）
    returns_seq = np.array(returns.iloc[:, 0])
    values = np.array(values.iloc[:, 0])
    # 算最大回撤
    max_drawdown = 0
    for i in range(1, len(values)):
        sub_values = values[: i]
        drawdown = values[i] / max(sub_values) - 1
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    mean_value = pow(values[-1]/values[0], 12/len(values))-1
    # mean_value = np.mean(returns)*12
    std = returns_seq.std() * pow(12, 0.5)
    sharpe_ratio = (mean_value - riskfree_rate) / std
    calmer_ratio = -1 * mean_value / max_drawdown
    return [max_drawdown, mean_value, std, sharpe_ratio, calmer_ratio]


def earnings_lost(returns, returns_target):
    r1 = np.array(returns)
    r2 = np.array(returns_target)
    earnings = 0
    earnings_time = 0
    lost = 0
    lost_time = 0
    for each_return in range(len(r1)):
        if r1[each_return] > r2[each_return]:
            earnings = earnings + (r1[each_return] - r2[each_return])
            earnings_time = earnings_time + 1
        else:
            lost = lost + (r2[each_return] - r1[each_return])
            lost_time = lost_time + 1

    earnings_ratio = (earnings/earnings_time)/(lost/lost_time)
    earnings_prob = earnings_time / (earnings_time + lost_time)
    return [earnings_ratio, earnings_prob]


def save_results(data, name):
    with pd.ExcelWriter(name) as writer:
        data.to_excel(writer)
        writer.close()


def values(returns):
    value = [1]
    returns = pd.DataFrame(returns)
    for i in range(1, returns.shape[0]):
        value.append(value[i-1] * (1 + returns.iloc[i, 0]))

    value = pd.DataFrame(value)
    value.index = returns.index

    return value


def beta(returns, target):
    returns = np.array(returns)
    target = np.array(target)
    return np.cov(returns, target)[1][0] / np.var(target)

