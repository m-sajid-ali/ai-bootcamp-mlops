"""
Simulate a *silent* data change: the file keeps the same name, but its contents change.

    python change_data.py           # drop the price-capped rows (data "cleaning")

Run train.py before and after this — same code, same params, same git commit,
but a different result... and only the data_md5 in MLflow reveals why.
"""
import pandas as pd

path = "data/house_prices.csv"
df = pd.read_csv(path)
before = len(df)

# A realistic "someone cleaned the data" change: drop the price-capped rows.
df = df[df["price"] < 500_000]

df.to_csv(path, index=False)     # same filename — the change is invisible from outside
print(f"Changed {path}: {before} -> {len(df)} rows (dropped price-capped rows).")
print("The filename is unchanged. Nothing outside this file knows it moved.")
