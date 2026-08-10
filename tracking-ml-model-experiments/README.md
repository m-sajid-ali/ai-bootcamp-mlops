# MLOps — Reproducibility & Tracking (all local, terminal + Docker)

One container, one project, two parts — **same interface throughout** (a terminal + the
MLflow UI). No notebooks.

- **Part A — Meet MLflow.** Run experiments with `train.py` and *watch tracking work* in the
  MLflow UI. Goal: get comfortable with experiment tracking.
- **Part B — Track the code too.** Notice MLflow didn't capture the *code* you changed. Add git,
  and see code and experiments line up.

Part B is the *same work* as Part A — the only thing that changes is that we add git.

```
tracking-ml-model-experiments/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── project/                # mounted in: live code + data + persistent mlflow.db
    ├── house_prices.csv     # real California data (price in $)
    ├── train.py             # params as inputs; MLflow logs params/metric/model + git commit
    └── README.md
```

## One-time setup
```
cd tracking-ml-model-experiments
docker compose build         
```

## Start it
```
docker compose up -d        
docker compose exec lab bash  # your working shell, inside /workspace
```
---

# Part A — Meet MLflow (terminal + UI)

**Goal:** run experiments and watch MLflow track every one.

1. Open **http://localhost:5000** in your browser. Leave it open.
2. **Run a few experiments** (in your first shell). Same code, different inputs:
   ```
   python train.py --run-name baseline    --n-estimators 100
   python train.py --run-name more_trees  --n-estimators 300
   python train.py --run-name depth15     --n-estimators 300 --max-depth 15
   python train.py --run-name smaller_test --n-estimators 300 --test-size 0.1
   ```
   After each run, **switch to the UI** and watch the row appear.

3. **Observe tracking in the UI** — the part to make you *feel*:
   - sort by `rmse` -> the **best** run, instantly
   - tick two runs -> **Compare** -> exactly which params differ
   - click a run -> its **params, metric, and the saved model** are all there

*"This is the record we could never keep by hand — automatic, comparable, permanent.
And because the database lives in our mounted folder, it survives restarts."*

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
*"Three experiments, zero code edits, zero commits. MLflow logged the params.
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
*"This changed what the code does — so we commit once, then run.
Now MLflow's commit pointer actually means something."*

### 3) The payoff — the two records line up
```
git log --oneline
```
Refresh the **MLflow UI** and see the **Git Version Commit** column value, or print it:

**The lesson:** the param-only runs share **one** commit (code never changed);
`version` carries a **new** commit. To rebuild any run: read its commit, `git checkout`,
and you have the exact code that produced it.

---

## The three-way mental model
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

---

# Part C — Version the data too (DVC)
 
**Goal:** version the *data*, so a run can be rebuilt with the exact data that produced it.
Git versions code, MLflow tracks runs — but nothing has been versioning the **data**.
 
## The problem — the data isn't recorded at all
 
Look at any run in the MLflow UI: there's **no record of which data it used** — the Dataset
column is empty, and no parameter captures it. Now watch that become dangerous.
```
python train.py --run-name before_change --n-estimators 200
python change_data.py          # edits house_prices.csv IN PLACE (same filename)
python train.py --run-name after_change  --n-estimators 200
```
Compare the two runs using UI

same params, **same git commit**, but a different RMSE — and *nothing
in the record explains why*. The data changed underneath us, and the original data is now
overwritten. **Which data made `before_change`? You can't get it back.** Git tracked the code,
MLflow tracked the run, and the data fell through the gap between them.
 
## The fix — DVC versions the data
 
**1. Initialise DVC and hand the data over from git to DVC.**
(The CSV was tracked by git in Parts A/B; DVC takes it over.)
```
dvc init
git rm -r --cached house_prices.csv        # stop git tracking the big file
dvc add house_prices.csv                    # DVC now tracks it
git add house_prices.csv.dvc .gitignore
git commit -m "track data with DVC (v1)"
```
Show the tiny **`house_prices.csv.dvc`** pointer — it holds the data's md5 hash and *is* tracked
by git. The CSV itself is now in `.gitignore` (git no longer stores the big file).
 
**2. Add a local remote (a folder — persists via the mounted volume) and push.**
```
dvc remote add -d localremote /dvc-remote
git add .dvc/config && git commit -m "add local DVC remote"
dvc push                                     # data now stored in /dvc-remote
```
 
**3. Now train with data tracking — use `train_dvc.py`.**
Same training code, but it logs the **DVC data version** as a param and registers the
**dataset** in MLflow (filling the UI's Dataset column):
```
python train_dvc.py --run-name dvc_baseline   --n-estimators 300
python train_dvc.py --run-name dvc_more_trees --n-estimators 500
```
In the runs table, the **old `train.py` runs show no data** (empty Dataset / `data_version`),
while the new `dvc_*` runs show the DVC hash and a dataset entry. Same experiment, one table,
before-and-after at a glance.
 
> **The key point:** MLflow now *records* which data was used — but it's the `data_version`
> (the DVC hash) that lets us *restore* it. **MLflow points; DVC rebuilds.**
 
**4. Make a new data version and prove you can go back.**
```
python change_data.py                        # data -> v2
dvc add house_prices.csv
git add house_prices.csv.dvc && git commit -m "data v2 (cleaned)"
dvc push
 
git checkout HEAD~1 -- house_prices.csv.dvc  # go back to the v1 pointer
dvc checkout house_prices.csv                # DVC restores the exact v1 file
md5sum house_prices.csv                        # matches v1 again
```
**The v1 data is back, byte for byte.** Re-run `train_dvc.py` and the original result returns.
Reproducibility restored.
 
---
 
## The complete mental model
| What you version | Tool |
|---|---|
| experiments — params, metrics, the model | **MLflow** |
| code | **Git** |
| data | **DVC** |
 
Together they reproduce any past run — the exact **experiment**, the exact **code**, and the
exact **data** that produced it. That is the reproducibility gap, fully closed.

