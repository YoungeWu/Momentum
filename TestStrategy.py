from Strategy import *
from Strategy_func import save_results

''' 测试代码是否准确'''
'''
raw = pd.read_excel("data/data.xlsx", index_col=0)
indexes = Indexdata(raw)
# print(indexes.returns())

sz800 = Indexdata(raw["中证800"])
# print(sz800.values())

broad_index = Indexdata(raw.iloc[:, :7])
industry_index = Indexdata(raw.iloc[:, -8:])

mm1 = Momentum(broad_index, industry_numbers=1).std_momentum()
mm2 = Momentum(industry_index, industry_numbers=2).std_momentum()

strategy_return = 0.5 * mm1[0] + 0.5 * mm2[0]
strategy_value = stdfunc.values(strategy_return)

perform1 = Evaluation(strategy_value, strategy_return)
perform1.earnings_lost(sz800.returns())
print(perform1.performance(0.0))
'''


''' 南方基金轮动 '''

nanfang_funds = pd.read_excel("data/南方基金宽基.xlsx", index_col=0)

indexes = Indexdata(nanfang_funds)
returns = indexes.returns()
time_steps = indexes.time_interval()

# 分别建立indexdata对象
broad_index = Indexdata(nanfang_funds.iloc[:, :8])
industry_index = Indexdata(nanfang_funds.iloc[:, 9:])

# 计算中证800收益
SZ800 = Indexdata(nanfang_funds["中证800"])
SZ800_netvalue = SZ800.values()

# 图1
'''
b1 = Indexdata(Momentum(broad_index, 1, "month").std_momentum()[1])
b2 = Indexdata(Momentum(broad_index, 2, "month").std_momentum()[1])
b3 = Indexdata(Momentum(broad_index, 3, "month").std_momentum()[1])
target = Indexdata(SZ800_netvalue)
b1.draw()
b2.draw()
b3.draw()
target.draw()
plt.legend(["N=1", "N=2", "N=3", "SZ800"])
plt.show()
'''
'''
# 图2
i1 = Indexdata(Momentum(industry_index, 1, "month").std_momentum()[1])
i2 = Indexdata(Momentum(industry_index, 2, "month").std_momentum()[1])
i3 = Indexdata(Momentum(industry_index, 3, "month").std_momentum()[1])
target = Indexdata(SZ800_netvalue)
i1.draw()
i2.draw()
i3.draw()
target.draw()
plt.legend(["N=1", "N=2", "N=3", "SZ800"])
plt.show()
'''


'''
broad_momentum = Momentum(broad_index, 1, "month")
industry_momentum = Momentum(industry_index, 3, "month")

# 策略收益
momentum_returns = 1/2 * broad_momentum.std_momentum()[0] + 1/2 * industry_momentum.std_momentum()[0]
momentum_value = stdfunc.values(momentum_returns)

# 将策略净值也转换成indexdata对象, 然后画图
values = Indexdata(momentum_value)
target = Indexdata(SZ800_netvalue)
values.draw()
target.draw()
plt.show()
plt.legend(["Strategy", "SZ800"])

# 输出盈亏比和胜率
mm_perform = Evaluation(momentum_value, momentum_returns)
mm_perform.earnings_lost(SZ800.returns())

# 保存数据
sz_perform = Evaluation(SZ800.values(), SZ800.returns())
perform = pd.DataFrame()
perform = perform.append([mm_perform.performance()])
perform = perform.append([sz_perform.performance()])
perform.columns = ["最大回撤", "年化收益", "年化波动率", "夏普比率", "Calmar比率"]
perform.index = ['策略', '中证800']
save_results(perform, "指标评测_南方基金.xlsx")
'''

''' 季度数据'''


broad_momentum = Momentum(broad_index, 1, freq="s")
industry_momentum = Momentum(industry_index, 2, freq="s")

# 策略收益
momentum_returns = 0 * broad_momentum.std_momentum()[0] + 1/2 * industry_momentum.std_momentum()[0]
momentum_value = stdfunc.values(momentum_returns)

# 输出盈亏比和胜率
mm_perform = Evaluation(momentum_value, momentum_returns)
mm_perform.earnings_lost(SZ800.returns())

# 保存数据
sz_perform = Evaluation(SZ800.values(), SZ800.returns())
perform = pd.DataFrame()
perform = perform.append([mm_perform.performance()])
perform = perform.append([sz_perform.performance()])
perform.columns = ["最大回撤", "年化收益", "年化波动率", "夏普比率", "Calmar比率"]
perform.index = ['策略', '中证800']
save_results(perform, "指标评测_南方基金.xlsx")

''' 新策略 '''

'''
signals = pd.read_excel("data/signals.xlsx", index_col=0)

mm2 = SignalMomentum(broad_index, 1, "month", signal=signals, signal_type="single")
values = mm2.sig_momentum()[0]
print(values)

mm3 = SignalMomentum(broad_index, 1, "month", signal=signals, signal_type="multiple")
values = mm3.sig_momentum()[0]
print(values)

mm4 = SignalMomentum(broad_index, 1, "month", signal=signals, signal_type="proportional")
values = mm4.sig_momentum()[0]
print(values)

mm5 = SignalMomentum(broad_index, 1, "month", signal=signals, signal_type="stop")
values = mm5.sig_momentum()[0]
print(values)
'''