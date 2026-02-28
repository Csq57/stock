"""
Technical indicators module.
Wraps the *ta* library for common indicators used in quantitative strategies.
"""

import pandas as pd
import ta


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add a comprehensive set of technical indicators to *df* (in-place copy)."""
    df = df.copy()
    df = ta.add_all_ta_features(
        df,
        open="Open",
        high="High",
        low="Low",
        close="Close",
        volume="Volume",
        fillna=True,
    )
    return df


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=window, adjust=False).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index."""
    indicator = ta.momentum.RSIIndicator(close=series, window=window)
    return indicator.rsi()


def macd(series: pd.Series, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9):
    """
    MACD line, signal line and histogram.

    Returns:
        Tuple(macd_line, signal_line, histogram) as pd.Series.
    """
    indicator = ta.trend.MACD(
        close=series,
        window_slow=window_slow,
        window_fast=window_fast,
        window_sign=window_sign,
    )
    return indicator.macd(), indicator.macd_signal(), indicator.macd_diff()


def bollinger_bands(series: pd.Series, window: int = 20, window_dev: int = 2):
    """
    Bollinger Bands.

    Returns:
        Tuple(upper_band, middle_band, lower_band) as pd.Series.
    """
    indicator = ta.volatility.BollingerBands(close=series, window=window, window_dev=window_dev)
    return indicator.bollinger_hband(), indicator.bollinger_mavg(), indicator.bollinger_lband()


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range."""
    indicator = ta.volatility.AverageTrueRange(
        high=df["High"], low=df["Low"], close=df["Close"], window=window
    )
    return indicator.average_true_range()
