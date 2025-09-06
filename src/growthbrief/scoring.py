import pandas as pd
import numpy as np
from scipy.stats import rankdata

# Import feature functions
from growthbrief.features.fundamentals import fundamentals_snapshot
from growthbrief.features.quality import quality_snapshot
from growthbrief.features.valuation import valuation_snapshot
from growthbrief.features.industry import industry_snapshot
from growthbrief.features.technical import technical_snapshot

def pct_rank(series: pd.Series) -> pd.Series:
    """
    Calculates percentile rank of a series, handling NaNs.
    """
    return pd.Series(rankdata(series, method='average') / len(series) * 100, index=series.index)

def winsorize_series(series: pd.Series, lower_bound: float = 1, upper_bound: float = 99) -> pd.Series:
    """
    Winsorizes a series to the specified percentile bounds.
    """
    lower_value = np.nanpercentile(series.dropna(), lower_bound)
    upper_value = np.nanpercentile(series.dropna(), upper_bound)
    return series.clip(lower=lower_value, upper=upper_value)

def score_grs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the Growth Room Score (GRS) for each ticker in the DataFrame.

    Args:
        df: DataFrame containing ticker symbols and relevant feature data.

    Returns:
        DataFrame with an added 'GRS' column.
    """
    # Ensure all necessary feature columns are present. If not, fill with NaN.
    # This assumes the input df will have columns like 'rev_yoy', 'roa_proxy', etc.
    # For a full implementation, you would call the snapshot functions here for each ticker.
    # For now, we assume the df comes pre-populated with these features.

    # Define weights for each component
    WEIGHTS = {
        'FM': 0.30,
        'Q': 0.20,
        'VG': 0.20,
        'IT': 0.15,
        'TC': 0.15,
    }

    # Define features for each component and their desired direction (higher is better = 1, lower is better = -1)
    # This is a simplified mapping. In a real scenario, each feature would be scored individually.
    FEATURE_MAPPING = {
        'FM': {'rev_yoy': 1, 'gm_delta': 1, 'om_delta': 1, 'fcf_delta': 1},
        'Q': {'roa_proxy': 1, 'cash_conversion': 1, 'accruals_proxy': -1}, # Accruals: lower is better
        'VG': {'pe': -1, 'ev_sales': -1, 'ev_sales_zscore': -1, 'peg_proxy': -1}, # Lower is better for valuation
        'IT': {'sector_rs_6m': 1, 'sector_rs_12m': 1, 'sector_above_50dma': 1, 'sector_above_200dma': 1},
        'TC': {'above_50dma': 1, 'above_100dma': 1, 'above_200dma': 1, '6m_momentum': 1, 'max_drawdown_1y': 1}, # Max drawdown: less negative (closer to 0) is better
    }

    # Initialize GRS scores
    df['GRS'] = np.nan

    # Iterate through each row (ticker) to calculate GRS
    # In a real scenario, you would likely process features in a vectorized way if possible
    # or fetch them for each ticker if not already in the DataFrame.
    
    # For this implementation, we assume df contains all necessary raw features.
    # We will calculate sub-scores and then combine them.

    # Calculate sub-scores (0-100 scale)
    for component, features in FEATURE_MAPPING.items():
        component_scores = []
        for feature, direction in features.items():
            if feature in df.columns:
                series = df[feature].copy()
                # Handle direction: if lower is better, invert the series for ranking
                if direction == -1:
                    series = -series # Invert for ranking, so lower original value gets higher rank
                
                # Winsorize before ranking to handle outliers
                series_winsorized = winsorize_series(series)
                
                # Calculate percentile rank
                ranked_series = pct_rank(series_winsorized)
                component_scores.append(ranked_series)
            else:
                # If a feature is missing, treat its contribution as 0 or NaN
                component_scores.append(pd.Series(np.nan, index=df.index))
        
        # Average component scores. Handle cases where all features for a component are NaN.
        if component_scores:
            df[f'{component}_score'] = pd.concat(component_scores, axis=1).mean(axis=1)
        else:
            df[f'{component}_score'] = np.nan

    # Combine sub-scores into GRS
    grs_components = []
    for component, weight in WEIGHTS.items():
        score_col = f'{component}_score'
        if score_col in df.columns:
            grs_components.append(df[score_col] * weight)
        else:
            grs_components.append(pd.Series(np.nan, index=df.index))

    # Sum weighted scores and scale to 0-100, 1 decimal
    df['GRS'] = pd.concat(grs_components, axis=1).sum(axis=1).round(1)

    # Ensure GRS is between 0 and 100
    df['GRS'] = df['GRS'].clip(lower=0, upper=100)

    return df
