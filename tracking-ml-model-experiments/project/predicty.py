"""Reload the BEST model straight from MLflow (no retraining) and predict."""
import pandas as pd
import mlflow, mlflow.sklearn

mlflow.set_tracking_uri("sqlite:///mlflow.db")

# 1) Find the best run (lowest RMSE)
runs = mlflow.search_runs(experiment_names=["house-prices"], order_by=["metrics.rmse ASC"])
if runs.empty:
    raise SystemExit("No runs found yet — run train.py a few times first.")

best = runs.iloc[0]; run_id = best["run_id"]
print(f"Best run : {best['tags.mlflow.runName']}  (RMSE ${best['metrics.rmse']:,.0f})")
print(f"Run id   : {run_id}")

# 2) Load the saved model from that run — no retraining
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
print("Loaded the saved model straight from MLflow (no retraining).")

# 3) Predict on a few rows
df = pd.read_csv("house_prices.csv")
sample = df.drop("price", axis=1).iloc[:5].copy()
if str(best.get("params.add_feature")) == "True" or "rooms_per_person" in str(best.get("params.features")):
    sample["rooms_per_person"] = sample["AveRooms"] / sample["AveOccup"]

preds = model.predict(sample)
print("\nPredicted prices for the first 5 houses:")
for i, p in enumerate(preds):
    print(f"  house {i+1}:  ${p:,.0f}")