# this is a strategy class

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Strategy_func as stdfunc


class Indexdata:

    # 构造函数
    def __init__(self, data=pd.DataFrame()):
        self.data = data.copy()
        self.date = self.data.index

    # 计算收益率
    # 注：该收益率的计算要求data列数大于2,
    # 不能是pd.Series, 否则会报IndexError

    def returns(self):
        # 为了避免发生IndexError错误，分两种情况讨论
        try:
            return_list = self.data.iloc[:, 0:] / self.data.shift(1).iloc[:, 0:] - 1  # 变成收益率
            return_list = return_list.iloc[1:, :]  # 把第一行去掉，这样序列长度-1，很重要
            return_list = return_list.fillna(-1)   # 空白的填成-1
        except:
            return_list = self.data.iloc[:] / self.data.shift(1).iloc[:] - 1
            return_list = return_list.iloc[1:]
            return_list = return_list.fillna(-1)

        return return_list

    # values将指数序列转化为净值序列，适用于单列数据
    def values(self):
        # 转化成pd.DataFrame对象
        value = pd.DataFrame([1])
        returns = pd.DataFrame(self.returns())
        for i in range(1, returns.shape[0]):
            value = value.append([value.iloc[i-1, 0] * (1 + returns.iloc[i,0])])

        # 输出为pd.DataFrame
        # index对象可以直接用索引
        value.index = self.date[1:]
        return value

    # 展示时间戳
    def time_interval(self):
        print("----Start Time:----")
        print(self.data.index[0])
        print("----End Time:----")
        print(self.data.index[-1])
        return [self.data.index[0], self.data.index[-1], self.data.shape[0]]

    # 绘图
    def draw(self):
        plt.plot(self.date, self.data)
        plt.xlabel("Time")
        plt.ylabel("Values")

    # 保存
    def save(self, name):
        stdfunc.save_results(self.data, name)
        return 0

    # 提取其中的一列数据
    def get_element(self, column):
        return self.data.iloc[:, column]

    # 改变其中的一列数据
    def set_element(self, column, new_data):
        self.data.iloc[:, column] = new_data
        return 0


# 建立momentum类，和Indexdata之间存在包含关系
# std_momentum 方法标准输出：[returns, values]，pd。DataFrame格式
class Momentum:

    # 默认构造函数
    def __init__(self, data=Indexdata(), industry_numbers=1, freq="month"):
        # 属性包括：一个Indexdata对象，要买前几个指数，策略频率
        self.data = data
        self.returns = self.data.returns()
        self.num = industry_numbers
        self.freq = freq
        # 月份和年份，用iterator写出来
        self.month = self.data.returns().index
        self.season = pd.DataFrame([self.returns.index[time] for time in range(2, self.returns.shape[0], 3)])

    # 执行动量策略
    def std_momentum(self):
        returns = stdfunc.SMBmomentum(self.returns, self.num, self.freq)[0]
        values = stdfunc.SMBmomentum(self.returns, self.num, self.freq)[1]

        # 加上列标签
        if self.freq == "month":
            returns.index = self.data.returns().index
            values.index = self.data.returns().index
        else:
            returns.index = self.season.iloc[:, 0]
            values.index = self.season.iloc[:, 0]

        return [returns, values]

    # 获得频率
    def get_freq(self):
        return self.freq

    # 获得回测时间点
    def get_length(self):
        if self.freq == "month":
            return self.month
        else:
            return self.season


# 按照信号来处理
class SignalMomentum(Momentum):

    def __init__(self, data=Indexdata(), industry_numbers=1, freq="month",
                 signal=pd.DataFrame(), signal_type="0"):
        # 调用momentum类构造函数
        super(SignalMomentum, self).__init__(data, industry_numbers, freq)
        # 加入新的属性
        self.type = signal_type
        self.signal = signal
        # 加入低风险指数
        raw = pd.read_excel("data/空仓.xlsx", index_col=0)
        self.signal_returns = Indexdata(raw).returns()
        # 以及策略收益净值
        self.strategy_returns = self.std_momentum()[0]
        self.strategy_value = self.std_momentum()[1]

    # 覆盖父类的momentum
    def sig_momentum(self, signal_num=1, x=0, y=0):
        if self.type == "single":
            return stdfunc.single_momentum(self.strategy_returns, self.signal, self.signal_returns)
        elif self.type == "multiple":
            return stdfunc.multiple_momentum(self.strategy_returns, self.signal, self.signal_returns, signal_num)
        elif self.type == "proportional":
            return stdfunc.proportional_momentum(self.strategy_returns, self.signal, self.signal_returns, x)
        else:
            return stdfunc.stop_momentum(self.strategy_returns, self.signal_returns, y)


# evaluation 包括所有指标的输出,包含Indexdata
# 标准输入，value, returns
class Evaluation:

    # 默认构造函数
    def __init__(self, value=pd.DataFrame(), returns=pd.DataFrame(), freq="month"):
        # data 是一个pd.dataframe对象，但输入时是Indexdata对象
        self.value = value
        # returns也是
        self.returns = returns

    # 输出各项指标
    def performance(self, riskless_rate=0.0):
        perform = pd.DataFrame([stdfunc.performance_eval(self.returns, self.value, riskless_rate)])
        perform.columns = ["最大回撤", "年化收益", "年化波动率", "夏普比率", "Calmar比率"]
        print((self.returns.mean() - riskless_rate)/self.returns.std())
        return perform

    # 计算胜率和盈亏比
    def earnings_lost(self, target_returns):
        returns = pd.DataFrame(self.returns)
        target_returns = pd.DataFrame(target_returns)
        results = stdfunc.earnings_lost(returns.iloc[:, 0], target_returns.iloc[:, 0])
        print("----- 盈亏比为 -----")
        print(results[0])
        print("----- 胜率为 -----")
        print(results[1])
        return 0

    # 保存结果
    def save(self, save_type, name, riskless_rate=0.0, target=pd.DataFrame()):
        if save_type == "perform":
            perform = self.performance(riskless_rate)
            stdfunc.save_results(perform, name)
        else:
            perform = self.earnings_lost(target)
            stdfunc.save_results(perform, name)

        return 0












