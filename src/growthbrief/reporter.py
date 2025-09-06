import pandas as pd
import numpy as np

def generate_grs_insights(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Generates insights (evidence and risks) for top-ranked tickers based on GRS.

    Args:
        df: DataFrame containing ticker symbols, GRS, and all feature data.
        top_n: Number of top tickers to generate insights for.

    Returns:
        DataFrame with added 'Evidence' and 'Risks' columns for top tickers.
    """
    df_sorted = df.sort_values(by='GRS', ascending=False).head(top_n).copy()

    evidence_list = []
    risks_list = []

    for index, row in df_sorted.iterrows():
        evidence = []
        risks = []

        # --- Evidence (simplified for now, based on high values of key positive features) ---
        # Fundamentals Momentum
        if row.get('rev_yoy', -np.inf) > 0.1: # Example threshold
            evidence.append(f"Strong Revenue YoY ({row['rev_yoy']:.1%})")
        if row.get('gm_delta', -np.inf) > 0.01: # Example threshold
            evidence.append(f"Improving Gross Margin ({row['gm_delta']:.1%})")

        # Quality
        if row.get('roa_proxy', -np.inf) > 0.05: # Example threshold
            evidence.append(f"Good Return on Assets ({row['roa_proxy']:.1%})")

        # Valuation vs Growth (lower is better, so negative z-score is good)
        if row.get('ev_sales_zscore', np.inf) < -0.5: # Example threshold
            evidence.append(f"Attractive EV/Sales Z-score ({row['ev_sales_zscore']:.1f})")

        # Industry Tailwinds
        if row.get('sector_rs_6m', -np.inf) > 0.05: # Example threshold
            evidence.append(f"Strong Sector Relative Strength ({row['sector_rs_6m']:.1%})")

        # Technical Confirmation
        if row.get('above_200dma', 0) == 1: # Binary indicator
            evidence.append("Price above 200-day MA")

        # --- Risks (simplified for now, based on low values of key positive features or high negative features) ---
        # Drawdown
        if row.get('max_drawdown_1y', 0) < -0.20: # Example threshold for significant drawdown
            risks.append(f"Significant 1-year Drawdown ({row['max_drawdown_1y']:.1%})")
        
        # Valuation (if PE is very high)
        if row.get('pe', np.inf) > 50: # Example threshold
            risks.append(f"High PE Ratio ({row['pe']:.1f})")

        # Ensure at least 3 evidence and 2 risks (fill with generic if not enough specific ones)
        while len(evidence) < 3:
            evidence.append("General positive trend")
        while len(risks) < 2:
            risks.append("General market risk")

        evidence_list.append("; ".join(evidence[:3])) # Take top 3
        risks_list.append("; ".join(risks[:2])) # Take top 2

    df_sorted['Evidence'] = evidence_list
    df_sorted['Risks'] = risks_list

    return df_sorted
