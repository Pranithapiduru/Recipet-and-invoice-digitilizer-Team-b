import pandas as pd


def search_receipts(df: pd.DataFrame, keyword: str):
    if df.empty or not keyword:
        return df

    keyword = keyword.lower()
    return df[
        (df["vendor"].str.lower().str.contains(keyword, na=False)) |
        (df["category"].str.lower().str.contains(keyword, na=False))
    ]