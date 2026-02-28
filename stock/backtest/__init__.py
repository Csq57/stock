"""
Backtesting engine.
Simulates a long-only strategy on historical data and reports performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Optional

from ..strategies import Strategy


class BacktestResult:
    """Container for backtesting results."""

    def __init__(self, trades: pd.DataFrame, equity: pd.Series, metrics: dict):
        self.trades = trades
        self.equity = equity
        self.metrics = metrics

    def summary(self) -> str:
        lines = ["=== Backtest Summary ==="]
        for k, v in self.metrics.items():
            if isinstance(v, float):
                lines.append(f"  {k}: {v:.4f}")
            else:
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    def __repr__(self):
        return self.summary()


class Backtester:
    """
    Simple event-driven backtester.

    Assumptions:
    - Long-only.
    - Executes trades at the *next* bar's open price (no look-ahead bias).
    - Position sizing: invest full capital per signal (100% of equity).
    - Transaction cost applied as a fraction of trade value (both sides).
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission: float = 0.001,
    ):
        self.initial_capital = initial_capital
        self.commission = commission

    def run(self, df: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        """
        Run the backtest.

        Args:
            df: OHLCV DataFrame.
            strategy: A Strategy instance.

        Returns:
            BacktestResult with trades, equity curve and metrics.
        """
        signals = strategy.generate_signals(df)

        # Shift signals by 1 to execute at next open (avoid lookahead bias)
        exec_signals = signals.shift(1).fillna(0)
        prices = df["Open"].copy()

        cash = self.initial_capital
        shares = 0.0
        position = 0  # 0 = flat, 1 = long

        equity_values = []
        trades = []

        for i, (date, price) in enumerate(prices.items()):
            sig = exec_signals.iloc[i]

            if sig == 1 and position == 0 and cash > 0:
                # Buy
                cost = cash
                shares = (cost * (1 - self.commission)) / price
                cash = 0.0
                position = 1
                trades.append({"date": date, "action": "BUY", "price": price, "shares": shares})

            elif sig == -1 and position == 1:
                # Sell
                proceeds = shares * price * (1 - self.commission)
                cash = proceeds
                shares = 0.0
                position = 0
                trades.append({"date": date, "action": "SELL", "price": price, "shares": shares})

            equity_values.append(cash + shares * price)

        equity = pd.Series(equity_values, index=prices.index)
        trades_df = pd.DataFrame(trades)

        metrics = self._compute_metrics(equity, df["Close"])
        return BacktestResult(trades=trades_df, equity=equity, metrics=metrics)

    def _compute_metrics(self, equity: pd.Series, close: pd.Series) -> dict:
        returns = equity.pct_change().dropna()
        total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(equity)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe = annualized_return / volatility if volatility != 0 else 0.0

        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        bh_return = (close.iloc[-1] / close.iloc[0]) - 1

        return {
            "Total Return": total_return,
            "Annualized Return": annualized_return,
            "Annualized Volatility": volatility,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": max_drawdown,
            "Buy & Hold Return": bh_return,
        }
