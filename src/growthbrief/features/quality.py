import yfinance as yf
import pandas as pd
import numpy as np

def quality_snapshot(ticker: str) -> dict:
    """
    Fetches key quality metrics for a given ticker using yfinance.

    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing quality metrics, or NaN for missing data.
    """
    try:
        stock = yf.Ticker(ticker)

        income_stmt = stock.financials
        cash_flow = stock.cashflow
        balance_sheet = stock.balance_sheet

        if income_stmt.empty or cash_flow.empty or balance_sheet.empty:
            return {
                'roa_proxy': np.nan,
                'cash_conversion': np.nan,
            }

        income_stmt = income_stmt.T.sort_index(ascending=False)
        cash_flow = cash_flow.T.sort_index(ascending=False)
        balance_sheet = balance_sheet.T.sort_index(ascending=False)

        # --- ROA Proxy: Net Income / Total Assets ---
        net_income = income_stmt.get('Net Income')
        total_assets = balance_sheet.get('Total Assets')

        roa_proxy = np.nan
        if net_income is not None and total_assets is not None and not total_assets.empty and total_assets.iloc[0] != 0:
            roa_proxy = net_income.iloc[0] / total_assets.iloc[0]

        # --- Cash Conversion: FCF / Net Income ---
        cfo = cash_flow.get('Cash Flow From Operations')
        capex = cash_flow.get('Capital Expenditures')

        fcf = np.nan
        if cfo is not None and capex is not None:
            fcf = cfo.iloc[0] + capex.iloc[0] # CapEx is usually negative in yfinance

        cash_conversion = np.nan
        if fcf is not None and net_income is not None and net_income.iloc[0] != 0:
            cash_conversion = fcf / net_income.iloc[0]

        return {
            'roa_proxy': roa_proxy,
            'cash_conversion': cash_conversion,
        }

    except Exception as e:
        print(f"Error fetching quality metrics for {ticker}: {e}")
        return {
            'roa_proxy': np.nan,
            'cash_conversion': np.nan,
        }
