# Health insurance risk-based pricing model

An actuarial-style risk-based pricing engine for health insurance: a Gamma GLM severity model fit on
real policy data, an interactive pricing dashboard, and a full validation writeup.

**[Live demo](docs/index.html)** · built to practice the same frequency-severity rating methodology used by pricing and actuarial teams in insurance.

## What this is

Insurers don't charge every policyholder the same premium. Risk-based pricing means estimating the
expected cost of each individual risk, then building a premium up from that estimate plus loadings for
expenses and profit. This project does exactly that for health insurance:

1. Fits a **Gamma GLM with a log link** (the standard actuarial technique for cost/severity modeling)
   on 1,338 real US health insurance policies
2. Converts the model into a **rating table** of relativities, the way a real filed rate manual works
3. Wraps it in an **interactive dashboard** where you can build an underwriting profile and watch the
   premium reconstruct itself, rating factor by rating factor
4. Validates the model the way actuaries do: a **lift chart** (actual vs predicted cost by decile) and
   a coefficient significance table

## Key findings

| Rating factor | Relativity | p-value | Significant |
|---|---|---|---|
| Tobacco use | **4.48x** | < 0.001 | Yes |
| Age (per year) | 1.029x | < 0.001 | Yes |
| BMI (per unit) | 1.014x | < 0.001 | Yes |
| Dependents (per child) | 1.088x | < 0.001 | Yes |
| Region: southeast vs northeast | 0.868x | 0.009 | Yes |
| Region: southwest vs northeast | 0.865x | 0.007 | Yes |
| Region: northwest vs northeast | 0.944x | 0.281 | No |
| Sex (male vs female) | 0.945x | 0.128 | No |

Smoking status is by far the dominant rating factor. Sex comes out statistically insignificant in this
fit, which lines up with why several regulators (the EU Gender Directive, the US ACA for individual and
small-group plans) exclude sex as a rating factor outright.

Model fit: **pseudo R² = 0.588, MAE = $4,389, RMSE = $7,771** (n = 1,338, in-sample).

## Project structure

```
health-insurance-risk-pricing/
├── data/
│   └── insurance.csv          # 1,338 policies: age, sex, bmi, children, smoker, region, charges
├── src/
│   ├── fit_model.py            # Fits the Gamma GLM, exports coefficients + validation data
│   └── model_export.json       # Model output consumed by the dashboard
├── notebooks/
│   └── analysis.ipynb          # Full EDA + model fit + validation, with plots
├── docs/
│   └── index.html              # Interactive pricing dashboard (GitHub Pages-ready)
├── requirements.txt
└── README.md
```

## Methodology

**Why Gamma, why log link.** Healthcare costs are strictly positive and right-skewed: most people cost
little, a small number cost a lot. A Gamma distribution fits that shape far better than assuming normal
errors. The log link makes every rating factor multiplicative, exactly how a real rate manual is built:
a base rate multiplied by a relativity per factor.

**Frequency and severity are combined here.** This dataset has one total annual cost per person, not
individual claim records, so this is a single severity-style cost model rather than a true frequency x
severity split. A production pricing team with claims-level data would model utilization (visits or
admissions per member) and cost-per-service separately, then multiply them, since the same total cost
can come from many small claims or a few large ones, and that distinction drives deductible design and
reinsurance.

**Premium build-up.** Gross premium = pure premium (expected claims cost) ÷ (1 − expense ratio − profit
margin), the standard actuarial "grossing-up" formula, where expenses and profit are expressed as a
percentage of premium rather than of losses.

## Limitations

- Single cross-sectional snapshot, not multi-year claims experience, so there's no out-of-sample
  holdout test, the fit statistics above are in-sample
- No credibility weighting for thin segments (a real model blends small/new segments toward the class
  average using Bühlmann credibility)
- No claims-level data, so no true frequency x severity split

## Running it

```bash
git clone <this-repo-url>
cd health-insurance-risk-pricing
pip install -r requirements.txt

# Refit the model and regenerate the validation data
cd src && python fit_model.py

# Explore the full analysis with plots
jupyter notebook notebooks/analysis.ipynb
```

The dashboard at `docs/index.html` is fully self-contained (the GLM coefficients are embedded as
constants, so it runs entirely client-side) and can be opened directly in a browser, or served via
GitHub Pages by pointing Pages at the `/docs` folder in this repo's settings.

## Data source

[Medical Cost Personal Datasets](https://github.com/stedy/Machine-Learning-with-R-datasets) — 1,338 US
health insurance policies, originally referenced in Brett Lantz's *Machine Learning with R*.

## Tech stack

Python (pandas, statsmodels), Gamma GLM with log link, vanilla HTML/CSS/JS dashboard, Chart.js.

## License

MIT, see [LICENSE](LICENSE).
