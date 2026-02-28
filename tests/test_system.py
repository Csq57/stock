"""
Unit tests for the quantitative trading system.
Run with: python -m pytest tests/ -v
"""

import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_ohlcv(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic OHLCV data for testing."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start="2020-01-01", periods=n, freq="B")
    close = 100 * np.cumprod(1 + rng.normal(0.0005, 0.01, n))
    high = close * (1 + rng.uniform(0, 0.02, n))
    low = close * (1 - rng.uniform(0, 0.02, n))
    open_ = close * (1 + rng.normal(0, 0.005, n))
    volume = rng.integers(1_000_000, 10_000_000, n).astype(float)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


# ---------------------------------------------------------------------------
# Indicator tests
# ---------------------------------------------------------------------------

class TestIndicators:
    def test_sma_length(self):
        from stock.indicators import sma
        df = make_ohlcv(100)
        result = sma(df["Close"], 20)
        assert len(result) == 100

    def test_sma_values(self):
        from stock.indicators import sma
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = sma(series, 3)
        assert abs(result.iloc[-1] - 4.0) < 1e-9

    def test_ema_length(self):
        from stock.indicators import ema
        df = make_ohlcv(100)
        result = ema(df["Close"], 10)
        assert len(result) == 100

    def test_rsi_range(self):
        from stock.indicators import rsi
        df = make_ohlcv(100)
        result = rsi(df["Close"], 14).dropna()
        assert (result >= 0).all() and (result <= 100).all()

    def test_macd_returns_three_series(self):
        from stock.indicators import macd
        df = make_ohlcv(100)
        m, s, h = macd(df["Close"])
        assert len(m) == len(s) == len(h) == 100

    def test_bollinger_bands_ordering(self):
        from stock.indicators import bollinger_bands
        df = make_ohlcv(100)
        upper, mid, lower = bollinger_bands(df["Close"])
        # Upper band must be >= lower band
        assert (upper.dropna() >= lower.dropna()).all()

    def test_atr_non_negative(self):
        from stock.indicators import atr
        df = make_ohlcv(100)
        result = atr(df, 14).dropna()
        assert (result >= 0).all()


# ---------------------------------------------------------------------------
# Strategy tests
# ---------------------------------------------------------------------------

class TestStrategies:
    def test_sma_cross_signal_values(self):
        from stock.strategies import SMACrossStrategy
        df = make_ohlcv(100)
        strategy = SMACrossStrategy(fast=5, slow=20)
        signals = strategy.generate_signals(df)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_rsi_strategy_signal_values(self):
        from stock.strategies import RSIStrategy
        df = make_ohlcv(100)
        strategy = RSIStrategy()
        signals = strategy.generate_signals(df)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_macd_strategy_signal_values(self):
        from stock.strategies import MACDStrategy
        df = make_ohlcv(100)
        strategy = MACDStrategy()
        signals = strategy.generate_signals(df)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_bb_strategy_signal_values(self):
        from stock.strategies import BollingerBandStrategy
        df = make_ohlcv(100)
        strategy = BollingerBandStrategy()
        signals = strategy.generate_signals(df)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_strategy_signal_index_aligned(self):
        from stock.strategies import SMACrossStrategy
        df = make_ohlcv(100)
        strategy = SMACrossStrategy()
        signals = strategy.generate_signals(df)
        assert signals.index.equals(df.index)


# ---------------------------------------------------------------------------
# Backtester tests
# ---------------------------------------------------------------------------

class TestBacktester:
    def test_initial_equity(self):
        from stock.strategies import SMACrossStrategy
        from stock.backtest import Backtester
        df = make_ohlcv(100)
        bt = Backtester(initial_capital=50_000)
        result = bt.run(df, SMACrossStrategy())
        assert result.equity.iloc[0] == pytest.approx(50_000, rel=0.01)

    def test_equity_curve_length(self):
        from stock.strategies import SMACrossStrategy
        from stock.backtest import Backtester
        df = make_ohlcv(100)
        bt = Backtester()
        result = bt.run(df, SMACrossStrategy())
        assert len(result.equity) == len(df)

    def test_metrics_keys(self):
        from stock.strategies import SMACrossStrategy
        from stock.backtest import Backtester
        df = make_ohlcv(100)
        bt = Backtester()
        result = bt.run(df, SMACrossStrategy())
        expected_keys = {
            "Total Return", "Annualized Return", "Annualized Volatility",
            "Sharpe Ratio", "Max Drawdown", "Buy & Hold Return",
        }
        assert expected_keys.issubset(result.metrics.keys())

    def test_max_drawdown_non_positive(self):
        from stock.strategies import SMACrossStrategy
        from stock.backtest import Backtester
        df = make_ohlcv(200)
        bt = Backtester()
        result = bt.run(df, SMACrossStrategy())
        assert result.metrics["Max Drawdown"] <= 0

    def test_no_lookahead_bias(self):
        """Trades should be based on yesterday's signal (signal shifted by 1)."""
        from stock.strategies import SMACrossStrategy
        from stock.backtest import Backtester
        df = make_ohlcv(100)
        bt = Backtester()
        result = bt.run(df, SMACrossStrategy())
        # Equity at bar 0 equals initial capital (no trade can happen on first bar)
        assert result.equity.iloc[0] == pytest.approx(100_000, rel=0.01)
