# MLOps Day 1 — Reproducibility & Tracking (all local, terminal + Docker)

One container, one project, two parts — **same interface throughout** (a terminal + the
MLflow UI). No notebooks.

- **Part A — Meet MLflow.** Run experiments with `train.py` and *watch tracking work* in the
  MLflow UI. Goal: get comfortable with experiment tracking.
- **Part B — Track the code too.** Notice MLflow didn't capture the *code* you changed. Add git,
  and see code and experiments line up.

Part B is the *same work* as Part A — the only thing that changes is that we add git.

```
mlops-lab/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── project/                # mounted in: live code + data + persistent mlflow.db
    ├── house_prices.csv     # real California data (price in $)
    ├── train.py             # params as inputs; MLflow logs params/metric/model + git commit
    └── README.md
```

## One-time setup (before class)
```
cd mlops-lab
docker compose build          # slow ONCE; layers cache, so it's a one-time fetch
```

## Start it (demo day — instant)
```
docker compose up -d          # container starts in seconds and stays running
docker compose exec lab bash  # your working shell, inside /workspace
```
Open a **second** shell the same way for the MLflow UI (below).

---

# Part A — Meet MLflow (terminal + UI)

**Goal:** run experiments and watch MLflow track every one.

1. **Start the MLflow UI.** In a second shell (`docker compose exec lab bash`):
   ```
   mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0
   ```
   Open **http://localhost:5000** in your browser. Leave it open.

2. **Run a few experiments** (in your first shell). Same code, different inputs:
   ```
   python train.py --run-name baseline    --n-estimators 100
   python train.py --run-name more_trees  --n-estimators 300
   python train.py --run-name depth15     --n-estimators 300 --max-depth 15
   python train.py --run-name smaller_test --n-estimators 300 --test-size 0.1
   ```
   After each run, **switch to the UI** and watch the row appear.

3. **Observe tracking in the UI** — the part to make them *feel*:
   - sort by `rmse` -> the **best** run, instantly
   - tick two runs -> **Compare** -> exactly which params differ
   - click a run -> its **params, metric, and the saved model** are all there

*"This is the record we could never keep by hand — automatic, comparable, permanent."*

4. **The catch.** Open any run in the UI and find the **Git Commit** field — it's empty.
   MLflow tracked the *experiment* beautifully… but nothing tracked the **code**. If we change
   the code next, how would we ever tie a result back to the exact code that made it? -> **Part B.**

---

# Part B — Track the code too (add git)

**Goal:** version the *code*, so any run is fully rebuildable.

**Set up the repo (once):**
```
git init -q && git add -A && git commit -qm "initial: train.py + data"
```

### 1) Experiments = changing INPUTS -> no commit
The values are command-line args, so the code file never changes:
```
python train.py --run-name g_baseline    --n-estimators 100
python train.py --run-name g_more_trees  --n-estimators 300
python train.py --run-name g_depth15     --n-estimators 300 --max-depth 15
```
**Say:** *"Three experiments, zero code edits, zero commits. MLflow logged the params.
There's nothing to version — the code is byte-for-byte the same."*

### 2) Logic change = editing CODE -> commit, then run
Open `train.py`, uncomment the feature line in `build_features()`:
```python
df["rooms_per_person"] = df["AveRooms"] / df["AveOccup"]
```
Then:
```
git add -A && git commit -m "add rooms_per_person feature"
python train.py --run-name g_with_feature --n-estimators 300
```
**Say:** *"This changed what the code does — so we commit once, then run.
Now MLflow's commit pointer actually means something."*

### 3) The payoff — the two records line up
```
git log --oneline
```
Refresh the **MLflow UI** and show the **Git Commit** column, or print it:
```
python -c "import mlflow; mlflow.set_tracking_uri('sqlite:///mlflow.db'); \
r=mlflow.search_runs(experiment_names=['house-prices'], order_by=['start_time ASC']); \
r['commit']=r['tags.mlflow.source.git.commit'].str[:7]; \
print(r[['tags.mlflow.runName','params.n_estimators','params.max_depth','metrics.rmse','commit']].to_string(index=False))"
```
**The lesson, on screen:** the param-only runs share **one** commit (code never changed);
`g_with_feature` carries a **new** commit. To rebuild any run: read its commit, `git checkout`,
and you have the exact code that produced it.

---

## The three-way mental model (your takeaway slide)
| What you change | Code edit? | Tracked by |
|---|---|---|
| a value you vary (n_estimators, seed) — **as an arg** | No | **MLflow** (param) |
| logic (feature, preprocessing, model type) | Yes | **Git** (commit) |
| random_state — added **once** to be deterministic | Yes, once | **Git** (a single commit, then stable) |

**Rule of thumb:** *stop editing code for experiments — change inputs.* Then MLflow tracks the
experiments, Git marks the milestones, and "when do I commit?" answers itself.

## Still open -> next gap
`house_prices.csv` just sits there. MLflow noted *which* prep each run used, but nothing
**versions the data itself**. If the file changes tomorrow, our records point at... what?
-> that's **DVC**, the next gap.
