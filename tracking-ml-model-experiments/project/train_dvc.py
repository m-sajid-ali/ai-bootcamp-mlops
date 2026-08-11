"""
Same training as train.py — but now the DATA is versioned too.

This version logs, for each run:
  - data_version : the DVC hash of house_prices.csv (a RESTORABLE pointer)
  - the dataset   : via MLflow's dataset feature (fills the UI "Dataset" column)

The point to make: MLflow can now *record* the data (Dataset column), but it's the
DVC version that lets us *restore* the exact data. MLflow points; DVC rebuilds.

    python train_dvc.py --run-name dvc_baseline --n-estimators 300
"""
import argparse
import os
import re
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def build_features(df):
    # --- LOGIC (change this = a code change = commit before running) ---
    # df["rooms_per_person"] = df["AveRooms"] / df["AveOccup"]
    return df


def dvc_data_version(dvc_file):
    """Read the DVC md5 from the .dvc pointer file — the restorable data version."""
    if not os.path.exists(dvc_file):
        return None
    m = re.search(r"md5:\s*([0-9a-f]+)", open(dvc_file).read())
    return m.group(1) if m else None


def main(args):
    df = pd.read_csv(args.data)
    df = build_features(df)

    X = df.drop("price", axis=1)
    y = df["price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000"))
    mlflow.set_experiment("house-prices")     # same experiment -> compare with earlier runs

    with mlflow.start_run(run_name=args.run_name):
        data_version = dvc_data_version(args.data + ".dvc")   # the DVC hash (restorable)

        mlflow.log_params({
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,
            "test_size": args.test_size,
            "seed": args.seed,
            "features": list(X.columns),
            "data_version": data_version,        # <-- the DVC version of the data
        })

        # MLflow's own dataset record — fills the "Dataset" column in the UI.
        # (Records WHICH data; DVC is what RESTORES it.)
        dataset = mlflow.data.from_pandas(df, source=args.data, name="house_prices")
        mlflow.log_input(dataset, context="training")

        model = RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.seed,
        )
        model.fit(X_train, y_train)

        rmse = mean_squared_error(y_test, model.predict(X_test)) ** 0.5
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, name="model", input_example=X_test.iloc[:2])

        v = data_version[:8] if data_version else "NONE (run `dvc add` first)"
        print(f"[{args.run_name}] RMSE ${rmse:,.0f}   data_version={v}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/house_prices.csv")
    p.add_argument("--run-name", default="dvc_run")
    p.add_argument("--n-estimators", type=int, default=100)
    p.add_argument("--max-depth", type=int, default=None)
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    main(p.parse_args())