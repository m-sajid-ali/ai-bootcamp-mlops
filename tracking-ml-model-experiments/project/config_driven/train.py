"""
Train a house-price model driven by a CONFIG FILE (not command-line arguments).

Edit config.yaml, then run:
    python train_config.py --config config.yaml

Why a config file (vs. long command lines)?
  - readable and structured (grouped by model / data)
  - real types: ints, floats, null, lists — no string-casting
  - it's a FILE, so its history is versionable:
        * logged to MLflow every run  -> no config is ever lost
        * committed to git at milestones -> keepers are versioned
"""
import argparse
import warnings
warnings.filterwarnings("ignore")

import yaml
import time
import os
import pandas as pd
import mlflow
import mlflow.sklearn
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "mlflow.db"


def build_features(df):
    # --- LOGIC (change this = a code change = commit before running) ---
    # df["rooms_per_person"] = df["AveRooms"] / df["AveOccup"]
    return df


def main(config_path):
    # 1) Read the config file — this is the experiment's input.
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    model_cfg = cfg["model"]
    data_cfg = cfg["data"]

    df = pd.read_csv(data_cfg["path"])
    df = build_features(df)

    X = df.drop("price", axis=1)
    y = df["price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=data_cfg["test_size"], random_state=data_cfg["seed"]
    )

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000"))
    mlflow.set_experiment("house-prices")     # same experiment -> compares with CLI runs

    with mlflow.start_run(run_name=cfg.get("run_name", "config_run")):
        # 2) Log the resolved params (flattened) — shows up in the runs table.
        mlflow.log_params({
            "n_estimators": model_cfg["n_estimators"],
            "max_depth": model_cfg["max_depth"],
            "test_size": data_cfg["test_size"],
            "seed": data_cfg["seed"],
            "features": list(X.columns),
        })

        # 3) Log the CONFIG FILE ITSELF as an artifact — the exact recipe, attached
        #    to this run whether or not it was committed to git.
        mlflow.log_artifact(config_path, artifact_path="config")

        model = RandomForestRegressor(
            n_estimators=model_cfg["n_estimators"],
            max_depth=model_cfg["max_depth"],
            random_state=data_cfg["seed"],
        )
        model.fit(X_train, y_train)

        # predict ONCE, then time and score the same call
        start = time.perf_counter()
        
        preds = model.predict(X_test)
        predict_time = time.perf_counter() - start

        rmse = mean_squared_error(y_test, preds) ** 0.5

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("predict_time_sec", predict_time)                    # batch time
        mlflow.log_metric("predict_ms_per_row", predict_time / len(X_test) * 1000)

        mlflow.sklearn.log_model(model, name="model", input_example=X_test.iloc[:2])

        print(f"[{cfg.get('run_name','config_run')}] RMSE ${rmse:,.0f}  "
              f"(config: {config_path})")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.yaml",
                   help="path to the YAML config file")
    main(p.parse_args().config)