"""
Data fetching module for the quantitative trading system.
Supports fetching historical stock data via yfinance.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List


def fetch_stock_data(
    symbol: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', '600519.SS' for A-shares).
        start: Start date string 'YYYY-MM-DD'. Overrides *period* when provided.
        end: End date string 'YYYY-MM-DD'. Defaults to today when *start* is given.
        period: yfinance period string used when *start* is None (default '1y').
        interval: Data interval, e.g. '1d', '1h', '5m'.

    Returns:
        DataFrame with columns Open, High, Low, Close, Volume (DatetimeIndex).
    """
    ticker = yf.Ticker(symbol)
    if start:
        end = end or datetime.today().strftime("%Y-%m-%d")
        df = ticker.history(start=start, end=end, interval=interval)
    else:
        df = ticker.history(period=period, interval=interval)

    if df.empty:
        raise ValueError(f"No data returned for symbol '{symbol}'")

    df.index = pd.to_datetime(df.index)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)
    return df


def fetch_multiple(
    symbols: List[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: str = "1y",
    interval: str = "1d",
) -> dict:
    """
    Fetch data for multiple symbols.

    Returns:
        Dict mapping symbol -> DataFrame.
    """
    result = {}
    for sym in symbols:
        try:
            result[sym] = fetch_stock_data(sym, start=start, end=end, period=period, interval=interval)
        except Exception as exc:
            print(f"[WARN] Could not fetch {sym}: {exc}")
    return result
