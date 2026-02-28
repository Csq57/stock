"""
Strategy base class and built-in example strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd
from ..indicators import sma, ema, rsi, macd, bollinger_bands


class Strategy(ABC):
    """Abstract base class for all trading strategies."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Compute buy/sell signals for each bar.

        Args:
            df: OHLCV DataFrame with DatetimeIndex.

        Returns:
            pd.Series of integer signals aligned to *df*.index:
                +1 = buy,  -1 = sell,  0 = hold.
        """

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


# ---------------------------------------------------------------------------
# Built-in strategies
# ---------------------------------------------------------------------------

class SMACrossStrategy(Strategy):
    """
    Dual SMA crossover strategy.
    Buy when fast SMA crosses above slow SMA; sell on the reverse.
    """

    def __init__(self, fast: int = 10, slow: int = 30):
        super().__init__(f"SMA_Cross({fast},{slow})")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast_ma = sma(df["Close"], self.fast)
        slow_ma = sma(df["Close"], self.slow)
        signal = pd.Series(0, index=df.index)
        signal[fast_ma > slow_ma] = 1
        signal[fast_ma < slow_ma] = -1
        return signal


class RSIStrategy(Strategy):
    """
    RSI mean-reversion strategy.
    Buy when RSI crosses below *oversold*; sell when it crosses above *overbought*.
    """

    def __init__(self, window: int = 14, oversold: float = 30.0, overbought: float = 70.0):
        super().__init__(f"RSI({window},{oversold},{overbought})")
        self.window = window
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        rsi_val = rsi(df["Close"], self.window)
        signal = pd.Series(0, index=df.index)
        signal[rsi_val < self.oversold] = 1
        signal[rsi_val > self.overbought] = -1
        return signal


class MACDStrategy(Strategy):
    """
    MACD crossover strategy.
    Buy when MACD line crosses above signal line; sell on the reverse.
    """

    def __init__(self, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9):
        super().__init__(f"MACD({window_fast},{window_slow},{window_sign})")
        self.window_slow = window_slow
        self.window_fast = window_fast
        self.window_sign = window_sign

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        macd_line, signal_line, _ = macd(
            df["Close"],
            window_slow=self.window_slow,
            window_fast=self.window_fast,
            window_sign=self.window_sign,
        )
        signal = pd.Series(0, index=df.index)
        signal[macd_line > signal_line] = 1
        signal[macd_line < signal_line] = -1
        return signal


class BollingerBandStrategy(Strategy):
    """
    Bollinger Band mean-reversion strategy.
    Buy when price touches lower band; sell when price touches upper band.
    """

    def __init__(self, window: int = 20, window_dev: int = 2):
        super().__init__(f"BB({window},{window_dev})")
        self.window = window
        self.window_dev = window_dev

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        upper, _, lower = bollinger_bands(df["Close"], self.window, self.window_dev)
        signal = pd.Series(0, index=df.index)
        signal[df["Close"] < lower] = 1
        signal[df["Close"] > upper] = -1
        return signal
