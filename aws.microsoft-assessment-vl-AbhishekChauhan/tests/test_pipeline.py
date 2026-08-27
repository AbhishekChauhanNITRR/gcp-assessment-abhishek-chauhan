import pytest
import pandas as pd
from data_pipeline.loader import inspect_and_clean_sales

def test_data_cleaning():
    df = inspect_and_clean_sales("data/sales.csv")
    assert "revenue" in df.columns
    assert df["revenue"].dtype == float
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])
