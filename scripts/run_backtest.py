import os
import sys
import csv
from datetime import date, timedelta
from pathlib import Path
import json

import pandas as pd
from rich import print
from rich.table import Table
import yfinance as yf

try:
    from growthbrief.backtest import run_backtest
    from growthbrief.scoring import score_grs
    from growthbrief.features.fundamentals import fundamentals_snapshot
    from growthbrief.features.quality import quality_snapshot
    from growthbrief.features.valuation import valuation_snapshot
    from growthbrief.features.industry import industry_snapshot
    from growthbrief.features.technical import technical_snapshot
except Exception as e:
    print(f"[red]Import error:[/red] {e}")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
TICKERS_PATH = ROOT / "tickers.csv"
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def read_tickers(path: Path):
    symbols = []
    with open(path) as f:
        reader = csv.reader(f)
        rows = list(reader)
        if rows and rows[0] and rows[0][0].strip().upper() in {"SYMBOL","TICKER"}:
            rows = rows[1:]
        for r in rows:
            if not r: 
                continue
            sym = r[0].strip().upper()
            if sym:
                symbols.append(sym)
    return symbols

def get_historical_prices(symbols: list, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical adjusted close prices for a list of symbols.
    """
    data = yf.download(symbols, start=start_date, end=end_date, progress=False)
    if data.empty:
        return pd.DataFrame()
    return data['Adj Close']

def main():
    symbols = read_tickers(TICKERS_PATH)
    if not symbols:
        print("[yellow]No symbols found in tickers.csv[/yellow]")
        sys.exit(0)

    # Define historical period for backtest (e.g., last 2 years)
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * 2) # 2 years

    print(f"[blue]Fetching historical prices from {start_date} to {end_date}...[/blue]")
    prices = get_historical_prices(symbols, start_date.isoformat(), end_date.isoformat())
    if prices.empty:
        print("[red]Failed to fetch historical prices.[/red]")
        sys.exit(1)

    # --- SIMPLIFICATION FOR GRS HISTORICAL DATA ---
    # For a true historical backtest, we would need to calculate GRS for each historical rebalance period.
    # This would involve fetching historical fundamental, quality, valuation, industry, and technical data.
    # This is a significant undertaking and beyond the scope of this single step.
    # For this backtest, we will use a simplified approach:
    # 1. Calculate GRS for the *latest* available data for each ticker.
    # 2. Assume these GRS scores are static throughout the backtest period.
    # This will NOT be a true historical GRS backtest, but demonstrates the backtesting framework.
    # TODO: Implement historical GRS calculation for a more robust backtest.

    print("[blue]Calculating latest GRS scores for backtest...[/blue]")
    all_features = []
    for symbol in symbols:
        try:
            fm_data = fundamentals_snapshot(symbol)
            q_data = quality_snapshot(symbol)
            vg_data = valuation_snapshot(symbol)
            it_data = industry_snapshot(symbol)
            tc_data = technical_snapshot(symbol)

            combined_data = {
                'ticker': symbol,
                **fm_data,
                **q_data,
                **vg_data,
                **it_data,
                **tc_data
            }
            all_features.append(combined_data)
        except Exception as e:
            print(f"[red]Error fetching latest features for {symbol}: {e}[/red]")
            all_features.append({'ticker': symbol})

    if not all_features:
        print("[red]No feature data collected for GRS calculation.[/red]")
        sys.exit(1)

    features_df = pd.DataFrame(all_features).set_index('ticker')
    grs_df = score_grs(features_df.copy())

    if 'GRS' not in grs_df.columns:
        print("[red]GRS column not found after scoring for backtest.[/red]")
        sys.exit(1)

    print("[blue]Running backtest...[/blue]")
    metrics = run_backtest(grs_df, prices, top_n=5) # Top 5 GRS tickers

    # Render table
    table = Table(title="GrowthBrief — Backtest Results")
    table.add_column("Metric")
    table.add_column("Value", justify="right")

    for metric, value in metrics.items():
        if isinstance(value, (float, np.float64)) and not np.isnan(value):
            table.add_row(metric.replace('_', ' ').title(), f"{value:.2%}")
        else:
            table.add_row(metric.replace('_', ' ').title(), str(value))

    print(table)

    # Save metrics to JSON
    out_json = OUT_DIR / f"backtest_{date.today().isoformat()}.json"
    try:
        # Convert numpy types to native Python types for JSON serialization
        serializable_metrics = {
            k: (v.item() if isinstance(v, np.generic) else v) 
            for k, v in metrics.items()
        }
        with open(out_json, 'w') as f:
            json.dump(serializable_metrics, f, indent=4)
        print(f"[green]Saved Backtest Results:[/green] {out_json}")
    except Exception as e:
        print(f"[red]Failed to save backtest results to JSON:[/red] {e}")

if __name__ == "__main__":
    main()
