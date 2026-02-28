# stock

A modular Python quantitative trading system. Built from first principles, inspired by the best open-source quant projects.

## 功能 / Features

| 模块 | 说明 |
|------|------|
| `stock/data` | 历史行情数据获取 (yfinance，支持 A 股 / US stocks) |
| `stock/indicators` | 技术指标：SMA、EMA、RSI、MACD、布林带、ATR |
| `stock/strategies` | 策略基类 + 内置策略：均线交叉、RSI、MACD、布林带 |
| `stock/backtest` | 事件驱动回测引擎（含手续费、无未来函数） |
| `stock/utils` | 净值曲线绘图、多策略对比图 |
| `analysis/analyse_starred.py` | 从 GitHub Stars 中筛选股票/量化项目 |

## 快速开始 / Quick Start

```bash
# 安装依赖
pip install -r requirements.txt

# 对默认标的运行所有内置策略
python main.py

# 指定标的和时间段
python main.py --symbols AAPL 600519.SS --period 2y

# 分析你的 GitHub Stars 中的量化项目
python analysis/analyse_starred.py <your_github_username>
# 若遇到 API 速率限制，加上 Personal Access Token
python analysis/analyse_starred.py <your_github_username> --token <YOUR_PAT>
```

## 项目结构 / Project Structure

```
stock/
├── main.py                       # 主入口：批量回测并输出报告
├── requirements.txt
├── stock/
│   ├── data/__init__.py          # 数据获取
│   ├── indicators/__init__.py    # 技术指标
│   ├── strategies/__init__.py    # 策略
│   ├── backtest/__init__.py      # 回测引擎
│   └── utils/__init__.py         # 工具函数
├── analysis/
│   └── analyse_starred.py        # GitHub Star 项目分析脚本
└── tests/
    └── test_system.py            # 单元测试 (pytest)
```

## 自定义策略 / Writing Your Own Strategy

```python
from stock.strategies import Strategy
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self):
        super().__init__("MyStrategy")

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # +1 = 买入, -1 = 卖出, 0 = 持仓不动
        signal = pd.Series(0, index=df.index)
        # ... 在这里实现你的逻辑 ...
        return signal
```

## 运行测试 / Run Tests

```bash
python -m pytest tests/ -v
```

## 参考项目 / Inspiration

- [microsoft/qlib](https://github.com/microsoft/qlib) — AI 量化投资平台
- [UFund-Me/Qbot](https://github.com/UFund-Me/Qbot) — AI 量化交易机器人
- [bbfamily/abu](https://github.com/bbfamily/abu) — 阿布量化交易系统
- [je-suis-tm/quant-trading](https://github.com/je-suis-tm/quant-trading) — Python 量化策略集合
- [wilsonfreitas/awesome-quant](https://github.com/wilsonfreitas/awesome-quant) — 量化金融资源列表
