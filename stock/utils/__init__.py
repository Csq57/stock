"""
Utility helpers: plotting equity curves and printing performance tables.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for environments without a display
import matplotlib.pyplot as plt
from typing import Optional


def plot_equity(equity: pd.Series, title: str = "Equity Curve", save_path: Optional[str] = None):
    """Plot an equity curve and optionally save it to *save_path*."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(equity.index, equity.values, label="Strategy", linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"[INFO] Equity curve saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)


def compare_strategies(results: dict, save_path: Optional[str] = None):
    """
    Plot equity curves for multiple strategies on a single chart.

    Args:
        results: Dict mapping strategy name -> BacktestResult.
        save_path: Optional file path to save the figure.
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    for name, result in results.items():
        norm = result.equity / result.equity.iloc[0]
        ax.plot(norm.index, norm.values, label=name, linewidth=1.5)
    ax.set_title("Strategy Comparison (Normalised)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalised Value")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"[INFO] Comparison chart saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)
