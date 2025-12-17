"""
Download stock data via yfinance for the last 1000 trading days
and prepare a tidy table including Open, Close, VWAP estimate, and Volume.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


def compute_daily_vwap(data: pd.DataFrame) -> pd.Series:
    """Compute an approximate daily VWAP using High, Low, and Close prices.

    yfinance provides daily bars without intraday trades, so this uses the
    typical price (High + Low + Close) / 3 as an estimate of the daily
    volume-weighted average price. The Volume column must be present.
    """

    if not {"High", "Low", "Close", "Volume"}.issubset(data.columns):
        missing = {"High", "Low", "Close", "Volume"} - set(data.columns)
        raise KeyError(f"Missing required columns for VWAP calculation: {missing}")

    typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
    return typical_price


def fetch_stock_history(ticker: str, days: int = 1000) -> pd.DataFrame:
    """Download the last ``days`` trading days of OHLCV data for ``ticker``."""
    ticker = ticker.strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    history = yf.download(ticker, period=f"{days}d", progress=False)
    if history.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'. Please verify the symbol.")

    history = history.reset_index().rename(columns={"Date": "date"})
    history["vwap"] = compute_daily_vwap(history)

    return history[["date", "Open", "Close", "vwap", "Volume"]]


def save_history(history: pd.DataFrame, ticker: str, output_dir: Path) -> Path:
    """Save history to a CSV file in ``output_dir`` and return the file path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{ticker}_last_1000_trading_days.csv"
    history.to_csv(file_path, index=False)
    return file_path


def main() -> None:
    ticker = input("请输入股票代码（例如 AAPL 或 000001.SZ）：").strip()
    try:
        history = fetch_stock_history(ticker)
    except Exception as exc:  # noqa: BLE001 - surface clear message to user
        print(f"下载数据时出错：{exc}")
        return

    output_dir = Path("data")
    csv_path = save_history(history, ticker, output_dir)

    print("数据整理完成！前5行示例：")
    print(history.head())
    print(f"完整数据已保存到: {csv_path.resolve()}")


if __name__ == "__main__":
    main()
