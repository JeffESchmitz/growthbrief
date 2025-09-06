#!/usr/bin/env python3
"""Run signals end-to-end for the tickers in tickers.csv.
This is a starter script; it will work once data.get_prices and signals.compute are implemented.
"""
import os
import sys
import csv
from datetime import date, timedelta
from pathlib import Path

from rich import print
from rich.table import Table
import pandas as pd

try:
    from growthbrief import data as gb_data
    from growthbrief import signals as gb_signals
except Exception as e:
    print(f"[red]Import error:[/red] {e}")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
TICKERS_PATH = ROOT / "tickers.csv"
OUT_DIR = ROOT / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def read_tickers(path: Path):
    symbols = []
    with open(path) as f:
        reader = csv.reader(f)
        rows = list(reader)
        # Support header or no header
        if rows and rows[0] and rows[0][0].strip().upper() in {"SYMBOL","TICKER"}:
            rows = rows[1:]
        for r in rows:
            if not r: 
                continue
            sym = r[0].strip().upper()
            if sym:
                symbols.append(sym)
    return symbols

def main():
    symbols = read_tickers(TICKERS_PATH)
    if not symbols:
        print("[yellow]No symbols found in tickers.csv[/yellow]")
        sys.exit(0)

    try:
        prices = gb_data.get_prices(symbols)
    except Exception as e:
        print(f"[red]Failed to load prices:[/red] {e}")
        sys.exit(1)

    try:
        metrics = gb_signals.compute(prices)
    except Exception as e:
        print(f"[red]Failed to compute signals:[/red] {e}")
        sys.exit(1)

    # Render table
    table = Table(title="GrowthBrief — Signals")
    table.add_column("Symbol")
    table.add_column("Price", justify="right")
    table.add_column("6m %", justify="right")
    table.add_column("SMA50", justify="right")
    table.add_column("SMA100", justify="right")
    table.add_column("SMA200", justify="right")
    table.add_column("Vol20d", justify="right")
    table.add_column("Uptrend", justify="center")

    latest_metrics = metrics.iloc[-1] # Get the last row of the DataFrame

    for sym in symbols:
        table.add_row(
            sym,
            f"{latest_metrics[(sym, 'Price')]:.2f}", # Last price for the symbol
            f"{latest_metrics[(sym, 'six_month_momentum_pct')]:.2f}",
            f"{latest_metrics[(sym, 'SMA50')]:.2f}",
            f"{latest_metrics[(sym, 'SMA100')]:.2f}",
            f"{latest_metrics[(sym, 'SMA200')]:.2f}",
            f"{latest_metrics[(sym, '20d_volatility')]:.4f}",
            "✅" if latest_metrics[(sym, 'is_uptrend')] else "—",
        )

    print(table)

    # Save CSV
    out_csv = OUT_DIR / f"signals_{date.today().isoformat()}.csv"
    try:
        # Create a DataFrame for saving with single-level columns
        data_for_csv = []
        for sym in symbols:
            row_data = {
                "Symbol": sym,
                "Price": latest_metrics[(sym, 'Price')],
                "six_month_momentum_pct": latest_metrics[(sym, 'six_month_momentum_pct')],
                "SMA50": latest_metrics[(sym, 'SMA50')],
                "SMA100": latest_metrics[(sym, 'SMA100')],
                "SMA200": latest_metrics[(sym, 'SMA200')],
                "20d_volatility": latest_metrics[(sym, '20d_volatility')],
                "is_uptrend": int(bool(latest_metrics[(sym, 'is_uptrend')]))
            }
            data_for_csv.append(row_data)
        
        df_to_save = pd.DataFrame(data_for_csv)
        df_to_save.to_csv(out_csv, index=False)
        print(f"[green]Saved:[/green] {out_csv}")
    except Exception as e:
        print(f"[red]Failed to save CSV:[/red] {e}")

if __name__ == "__main__":
    main()
