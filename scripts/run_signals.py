#!/usr/bin/env python3
"""Run signals end-to-end for the tickers in tickers.csv.
This is a starter script; it will work once data.get_prices and signals.compute are implemented.
"""
import os
import sys
import csv
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from rich import print
from rich.table import Table
import pandas as pd

try:
    from growthbrief import data as gb_data
    from growthbrief import signals as gb_signals
    from growthbrief.features.fundamentals import fundamentals_snapshot
    from growthbrief.features.quality import quality_snapshot
    from growthbrief.features.valuation import valuation_snapshot
    from growthbrief.features.industry import industry_snapshot
    from growthbrief.features.technical import technical_snapshot
    from growthbrief.scoring import score_grs
    from growthbrief.reporter import generate_grs_insights
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

    all_features = []
    print("[blue]Fetching features for tickers...[/blue]")
    for symbol in symbols:
        print(f"[blue]  Fetching data for {symbol}...[/blue]")
        try:
            # Fetch all features
            fm_data = fundamentals_snapshot(symbol)
            q_data = quality_snapshot(symbol)
            vg_data = valuation_snapshot(symbol)
            it_data = industry_snapshot(symbol)
            tc_data = technical_snapshot(symbol)

            # Combine all data for the symbol
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
            print(f"[red]Error fetching data for {symbol}: {e}[/red]")
            # Append with NaNs for missing data
            all_features.append({'ticker': symbol})


    if not all_features:
        print("[red]No feature data collected.[/red]")
        sys.exit(1)

    features_df = pd.DataFrame(all_features).set_index('ticker')

    print("[blue]Calculating GRS...[/blue]")
    grs_df = score_grs(features_df.copy()) # Pass a copy to avoid modifying original features_df

    if 'GRS' not in grs_df.columns:
        print("[red]GRS column not found after scoring.[/red]")
        sys.exit(1)

    # Generate insights for top N tickers
    top_n_grs = grs_df.sort_values(by='GRS', ascending=False).head(5) # Top 5 for insights
    grs_with_insights = generate_grs_insights(grs_df.copy(), top_n=len(grs_df)) # Generate for all, then filter for display

    # Render table for GRS
    table = Table(title="GrowthBrief — GRS Scores")
    table.add_column("Symbol")
    table.add_column("GRS", justify="right")
    table.add_column("Evidence", justify="left")
    table.add_column("Risks", justify="left")

    # Sort for display
    display_df = grs_with_insights.sort_values(by='GRS', ascending=False).head(10) # Display top 10

    for symbol, row in display_df.iterrows():
        table.add_row(
            symbol,
            f"{row['GRS']:.1f}",
            row['Evidence'],
            row['Risks'],
        )
    print(table)

    # Save GRS CSV
    grs_out_csv = OUT_DIR / f"grs_{date.today().isoformat()}.csv"
    grs_df.to_csv(grs_out_csv, index=True)
    print(f"[green]Saved GRS:[/green] {grs_out_csv}")

    # Create symlink or copy for latest
    grs_latest_csv = OUT_DIR / "grs_latest.csv"
    if grs_latest_csv.exists():
        grs_latest_csv.unlink() # Remove existing symlink/file
    
    # Using copy for simplicity, symlink might require admin rights or specific OS handling
    import shutil
    shutil.copy(grs_out_csv, grs_latest_csv)
    print(f"[green]Copied GRS to latest:[/green] {grs_latest_csv}")

if __name__ == "__main__":
    main()