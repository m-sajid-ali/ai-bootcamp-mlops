"""
Train a house-price model and track the run with MLflow.

The values we EXPERIMENT with are command-line arguments (not code edits):
    python train.py --n-estimators 300 --max-depth 15

The LOGIC we occasionally change (features, preprocessing) lives in the code below,
in build_features(). Changing that is a real code change -> commit it before running.
"""
import argparse
import time
import os
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def build_features(df):
    # --- LOGIC (change this = a code change = commit before running) ---
    # Start simple. Later in the demo we add a feature here, commit, and re-run.
    # df["rooms_per_person"] = df["AveRooms"] / df["AveOccup"]
    return df


def main(args):
    df = pd.read_csv(args.data)          
    df = build_features(df)

    X = df.drop("price", axis=1)
    y = df["price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000"))
    mlflow.set_experiment("house-prices")

    with mlflow.start_run(run_name=args.run_name):
        # PARAMETERS — what we varied (logged, not committed)
        mlflow.log_params({
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,
            "test_size": args.test_size,
            "seed": args.seed,
            "features": list(X.columns),
        })

        model = RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.seed,
        )
        model.fit(X_train, y_train)

        start = time.perf_counter()
        
        preds = model.predict(X_test)
        predict_time = time.perf_counter() - start

        rmse = mean_squared_error(y_test, preds) ** 0.5

        # OUTPUTS — the result and the model itself
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("predict_time_sec", predict_time)          # batch predict time
        mlflow.log_metric("predict_ms_per_row", predict_time / len(X_test) * 1000)  # per-row

        mlflow.sklearn.log_model(model, name="model", input_example=X_test.iloc[:2])

        # MLflow auto-records the git commit as a tag (mlflow.source.git.commit)
        # IF this folder is a git repo and the code is committed.
        print(f"[{args.run_name}] RMSE ${rmse:,.0f}  ({len(X.columns)} features)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/house_prices.csv")
    p.add_argument("--run-name", default="run")
    p.add_argument("--n-estimators", type=int, default=100)
    p.add_argument("--max-depth", type=int, default=None)
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    main(p.parse_args())
