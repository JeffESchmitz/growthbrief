#!/usr/bin/env python3
"""Run signals end-to-end for the tickers in tickers.csv.
This is a starter script; it will work once data.get_prices and signals.compute are implemented.
"""
import os
import sys
import csv
from datetime import date
from pathlib import Path

from rich import print
from rich.table import Table

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
        prices = gb_data.get_prices(symbols, lookback_days=400)
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

    for sym, m in metrics.items():
        table.add_row(
            sym,
            f"{m.get('price', float('nan')):.2f}",
            f"{m.get('six_month_momentum_pct', float('nan')):.2f}",
            f"{m.get('sma_50', float('nan')):.2f}",
            f"{m.get('sma_100', float('nan')):.2f}",
            f"{m.get('sma_200', float('nan')):.2f}",
            f"{m.get('volatility_20d', float('nan')):.4f}",
            "✅" if m.get("is_uptrend") else "—",
        )

    print(table)

    # Save CSV
    out_csv = OUT_DIR / f"signals_{date.today().isoformat()}.csv"
    try:
        import csv as _csv
        with open(out_csv, "w", newline="") as f:
            w = _csv.writer(f)
            w.writerow(["Symbol","Price","six_month_momentum_pct","sma_50","sma_100","sma_200","volatility_20d","is_uptrend"])
            for sym, m in metrics.items():
                w.writerow([
                    sym,
                    f"{m.get('price', float('nan'))}",
                    f"{m.get('six_month_momentum_pct', float('nan'))}",
                    f"{m.get('sma_50', float('nan'))}",
                    f"{m.get('sma_100', float('nan'))}",
                    f"{m.get('sma_200', float('nan'))}",
                    f"{m.get('volatility_20d', float('nan'))}",
                    int(bool(m.get('is_uptrend'))),
                ])
        print(f"[green]Saved:[/green] {out_csv}")
    except Exception as e:
        print(f"[red]Failed to save CSV:[/red] {e}")

if __name__ == "__main__":
    main()
