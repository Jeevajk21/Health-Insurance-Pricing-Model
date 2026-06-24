import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import json

df = pd.read_csv("../data/insurance.csv")
df["smoker_yes"] = (df["smoker"] == "yes").astype(int)
df["sex_male"] = (df["sex"] == "male").astype(int)

# Gamma GLM with log link - the standard actuarial approach for cost/severity modeling
formula = "charges ~ age + bmi + children + smoker_yes + sex_male + C(region, Treatment(reference='northeast'))"
model = smf.glm(formula=formula, data=df, family=sm.families.Gamma(link=sm.families.links.Log()))
result = model.fit()

print(result.summary())

params = result.params.to_dict()
print("\nPARAMS:", params)

# Model fit stats
pred = result.predict(df)
actual = df["charges"]
resid = actual - pred
mae = float(np.mean(np.abs(resid)))
rmse = float(np.sqrt(np.mean(resid**2)))
ss_res = float(np.sum(resid**2))
ss_tot = float(np.sum((actual - actual.mean())**2))
r2 = 1 - ss_res / ss_tot
print(f"\nMAE={mae:.2f} RMSE={rmse:.2f} pseudo-R2={r2:.4f}")

# Decile validation (lift chart) - sort by predicted, bucket into 10 deciles, compare actual vs predicted means
df["pred"] = pred
df["decile"] = pd.qcut(df["pred"], 10, labels=False) + 1
lift = df.groupby("decile").agg(
    actual_mean=("charges", "mean"),
    predicted_mean=("pred", "mean"),
    n=("charges", "count")
).reset_index()
print("\nLIFT CHART:\n", lift)

# Clean param names for export
clean_params = {}
for k, v in params.items():
    if k == "Intercept":
        clean_params["intercept"] = v
    elif k == "age":
        clean_params["age"] = v
    elif k == "bmi":
        clean_params["bmi"] = v
    elif k == "children":
        clean_params["children"] = v
    elif k == "smoker_yes":
        clean_params["smoker_yes"] = v
    elif k == "sex_male":
        clean_params["sex_male"] = v
    elif "northwest" in k:
        clean_params["region_northwest"] = v
    elif "southeast" in k:
        clean_params["region_southeast"] = v
    elif "southwest" in k:
        clean_params["region_southwest"] = v

export = {
    "coefficients": clean_params,
    "fit_stats": {"mae": mae, "rmse": rmse, "pseudo_r2": r2, "n": int(len(df))},
    "lift_chart": lift.to_dict(orient="records"),
    "data_summary": {
        "n_policies": int(len(df)),
        "avg_charge": float(df["charges"].mean()),
        "smoker_avg": float(df[df.smoker_yes==1]["charges"].mean()),
        "nonsmoker_avg": float(df[df.smoker_yes==0]["charges"].mean()),
    }
}

with open("model_export.json", "w") as f:
    json.dump(export, f, indent=2)

print("\nExported to model_export.json")
print(json.dumps(export, indent=2))
