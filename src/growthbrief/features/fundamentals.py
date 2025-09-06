import yfinance as yf
import pandas as pd
import numpy as np

def fundamentals_snapshot(ticker: str) -> dict:
    """
    Fetches key fundamental data for a given ticker using yfinance.

    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing fundamental metrics, or NaN for missing data.
    """
    try:
        stock = yf.Ticker(ticker)

        # Fetch financial data
        income_stmt = stock.financials
        cash_flow = stock.cashflow
        balance_sheet = stock.balance_sheet

        # Ensure dataframes are not empty and are in the expected format (columns are dates)
        if income_stmt.empty or cash_flow.empty or balance_sheet.empty:
            return {
                'rev_yoy': np.nan,
                'gm': np.nan, 'gm_delta': np.nan,
                'om': np.nan, 'om_delta': np.nan,
                'fcf_margin': np.nan, 'fcf_delta': np.nan,
                'accruals_proxy': np.nan
            }

        # Align dataframes by date (most recent first)
        income_stmt = income_stmt.T.sort_index(ascending=False)
        cash_flow = cash_flow.T.sort_index(ascending=False)
        balance_sheet = balance_sheet.T.sort_index(ascending=False)

        # --- Revenue YoY ---
        revenue = income_stmt.get('Total Revenue')
        rev_yoy = revenue.pct_change(-1).iloc[0] if revenue is not None and len(revenue) > 1 else np.nan

        # --- Gross Margin ---
        gross_profit = income_stmt.get('Gross Profit')
        gm = (gross_profit / revenue).iloc[0] if gross_profit is not None and revenue is not None and not revenue.empty and revenue.iloc[0] != 0 else np.nan
        gm_delta = (gm - (gross_profit / revenue).iloc[1]) if gross_profit is not None and revenue is not None and len(revenue) > 1 and not revenue.empty and revenue.iloc[1] != 0 else np.nan

        # --- Operating Margin ---
        operating_income = income_stmt.get('Operating Income')
        om = (operating_income / revenue).iloc[0] if operating_income is not None and revenue is not None and not revenue.empty and revenue.iloc[0] != 0 else np.nan
        om_delta = (om - (operating_income / revenue).iloc[1]) if operating_income is not None and revenue is not None and len(revenue) > 1 and not revenue.empty and revenue.iloc[1] != 0 else np.nan

        # --- FCF Margin ---
        cfo = cash_flow.get('Cash Flow From Operations')
        capex = cash_flow.get('Capital Expenditures') # This might be negative in yfinance
        
        # Ensure capex is treated as a positive cost for FCF calculation
        if capex is not None:
            capex = capex.abs()

        fcf = cfo + capex if cfo is not None and capex is not None else None # FCF = CFO - CapEx (CapEx is usually negative in yfinance)
        fcf_margin = (fcf / revenue).iloc[0] if fcf is not None and revenue is not None and not revenue.empty and revenue.iloc[0] != 0 else np.nan
        fcf_delta = (fcf_margin - (fcf / revenue).iloc[1]) if fcf is not None and revenue is not None and len(revenue) > 1 and not revenue.empty and revenue.iloc[1] != 0 else np.nan

        # --- Accruals Proxy: (NetIncome − CFO)/AvgAssets ---
        net_income = income_stmt.get('Net Income')
        total_assets = balance_sheet.get('Total Assets')

        if net_income is not None and cfo is not None and total_assets is not None and len(total_assets) > 1:
            avg_assets = (total_assets.iloc[0] + total_assets.iloc[1]) / 2
            if avg_assets != 0:
                accruals_proxy = (net_income.iloc[0] - cfo.iloc[0]) / avg_assets
            else:
                accruals_proxy = np.nan
        else:
            accruals_proxy = np.nan

        return {
            'rev_yoy': rev_yoy,
            'gm': gm, 'gm_delta': gm_delta,
            'om': om, 'om_delta': om_delta,
            'fcf_margin': fcf_margin, 'fcf_delta': fcf_delta,
            'accruals_proxy': accruals_proxy
        }

    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")
        return {
            'rev_yoy': np.nan,
            'gm': np.nan, 'gm_delta': np.nan,
            'om': np.nan, 'om_delta': np.nan,
            'fcf_margin': np.nan, 'fcf_delta': np.nan,
            'accruals_proxy': np.nan
        }
