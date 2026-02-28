"""
Main entry point: run all built-in strategies against a list of symbols
and print a comparative performance report.

Usage:
    python main.py
    python main.py --symbols AAPL TSLA --period 2y
"""

import argparse
import os

from stock.data import fetch_stock_data
from stock.strategies import SMACrossStrategy, RSIStrategy, MACDStrategy, BollingerBandStrategy
from stock.backtest import Backtester
from stock.utils import compare_strategies


DEFAULT_SYMBOLS = ["AAPL", "MSFT", "600519.SS"]
DEFAULT_PERIOD = "1y"

STRATEGIES = [
    SMACrossStrategy(fast=10, slow=30),
    RSIStrategy(window=14, oversold=30, overbought=70),
    MACDStrategy(),
    BollingerBandStrategy(window=20, window_dev=2),
]


def run(symbol: str, period: str, output_dir: str):
    print(f"\n{'='*60}")
    print(f"  Symbol: {symbol}  |  Period: {period}")
    print(f"{'='*60}")

    try:
        df = fetch_stock_data(symbol, period=period)
    except Exception as exc:
        print(f"[SKIP] Could not fetch data for {symbol}: {exc}")
        return

    backtester = Backtester(initial_capital=100_000, commission=0.001)
    results = {}
    for strategy in STRATEGIES:
        result = backtester.run(df, strategy)
        results[strategy.name] = result
        print(f"\n[Strategy] {strategy.name}")
        print(result.summary())

    # Save comparison chart
    os.makedirs(output_dir, exist_ok=True)
    chart_path = os.path.join(output_dir, f"{symbol.replace('.', '_')}_comparison.png")
    compare_strategies(results, save_path=chart_path)


def main():
    parser = argparse.ArgumentParser(description="Quantitative trading system demo")
    parser.add_argument("--symbols", nargs="+", default=DEFAULT_SYMBOLS)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    for symbol in args.symbols:
        run(symbol, args.period, args.output_dir)


if __name__ == "__main__":
    main()
