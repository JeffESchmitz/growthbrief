import pandas as pd
from growthbrief.scoring import score_grs

def test_score_grs_smoke():
    # Create a dummy DataFrame for smoke test
    data = {
        'col1': [1, 2, 3],
        'col2': [4, 5, 6]
    }
    df = pd.DataFrame(data)

    # Call the function
    result_df = score_grs(df)

    # Assert that the result is a DataFrame and has the expected columns (for now, just the original ones)
    assert isinstance(result_df, pd.DataFrame)
    assert list(result_df.columns) == list(df.columns)
