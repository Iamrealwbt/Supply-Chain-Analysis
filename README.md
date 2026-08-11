# Supply-Chain-Analysis ( the project is still developing with additional models/documenting) 
Demand–Supply Planning Analytics with Power BI and Python

Demand–Supply Planning Analytics

A short-horizon demand planning pipeline built on the SupplyGraph benchmark dataset. It consolidates four operational flows into a single daily panel, measures where demand, production and delivery diverge, and produces a hierarchical top-down forecast — forecast at the stable Sub-Group level, then allocate back to SKUs — feeding a Power BI risk table for planners.

The central question the project answers is not "what is next week's demand" but "at what grain should we forecast at all?" Section 05 is the answer, and it is backed by a controlled comparison rather than an assertion.

Data

Source: SupplyGraph: A Benchmark Dataset for Supply Chain Planning using Graph Neural Networks — real operational data from an FMCG manufacturer, released as an academic benchmark.

License: LGPL-2.1. This repository does not redistribute the raw data. Download it from the link above and place it under data/raw/.

bibtex
@misc{wasi2024supplygraph,
      title={SupplyGraph: A Benchmark Dataset for Supply Chain Planning using Graph Neural Networks},
      author={Azmine Toushik Wasi and MD Shafikul Islam and Adipto Raihan Akib},
      year={2024},
      eprint={2401.15299},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}

Scope after consolidation: 40 SKUs · 221 days (2023-01-01 → 2023-08-09) · 8,840 product-day rows · zero duplicate keys, zero missing values.

Flows used: sales orders (distributor demand), production volume, factory issue quantity, delivery to distributor — plus the product Group / Sub-Group node attributes.

What the data does not contain, which constrains everything downstream: beginning inventory, true production capacity, and order-level backlog. Every "risk" number in this project is therefore a planning proxy, not a stockout probability. This is stated again wherever it matters.

**Pipeline**
**01_data_audit.ipynb — consolidation and audit**

The four temporal files arrive in wide format (one column per SKU). Each is melted to long, joined on Date × product_id, and merged against the node table to attach Group and Sub-Group. Includes a duplicate-SKU-column fix and an explicit check that every product resolves to a group.

Audit output: row count, product count, date span, duplicate keys, null counts. → data/processed/daily_flow.csv

**02_weekly_KPI.ipynb — weekly KPIs and demand profiling**

Rolls the daily panel to product-weeks and computes the gaps that matter operationally:

Metric	                  Definition
demand_production_gap	      orders − production
demand_delivery_gap	      orders − delivery
factory_delivery_gap	      factory issue − delivery
production_to_demand_ratio	production ÷ orders
delivery_to_demand_ratio	delivery ÷ orders

Splitting delivery shortfall into a production problem and a factory-issue-to-delivery problem is the point — they have different owners and different fixes.

Also profiles each SKU on total demand, mean, standard deviation, coefficient of variation, and zero-demand rate. That profile is what motivates the forecasting decision two notebooks later: SKU-level daily demand here is intermittent and high-CV, exactly the regime where direct SKU forecasting underperforms.

→ weekly_product_flow.csv, product_risk_current.csv

**03_demand_forecasting.ipynb — daily SKU baseline**

A first pass: 28-day holdout, three naive models (seasonal_naive_7, moving_average_7, moving_average_28), per-SKU model selection on WAPE, 14-day forward forecast.

This notebook is retained as the baseline, not as the final method. Two problems it exposed:

Selecting a model per SKU on a single 28-day window, across 40 SKUs and 3 models, fits the holdout rather than the demand.
Forecasting intermittent daily SKU demand directly is fighting the noise rather than the signal.

Both are addressed in 04.

**04_hierarchical_forecasting.ipynb — the adopted method**

Forecast at the Sub-Group level, where demand aggregates into something stable, then allocate back down to SKUs.

Weeks defined as ending Wednesday so the final observed week (2023-08-03 → 08-09) is complete; partial weeks are dropped rather than silently under-counted.
Four-week holdout. Candidates: previous_week, moving_average_4, moving_average_8.
Model selected once, pooled across Sub-Groups on pooled WAPE — not per series. This is the deliberate fix for problem (1) above.
SKU allocation shares = 80% recent-8-week mix + 20% long-run mix, falling back to long-run share when recent demand is zero, and to equal shares when the Sub-Group has no history at all.
Shares are built strictly from the training period. No test-window information enters the allocation; forward-looking shares are rebuilt separately on full history.
Asserts that allocated SKU forecasts sum back to their Sub-Group forecast within 1e-6.

Reported: Sub-Group WAPE and bias, reconciled SKU-level WAPE and bias. Bias convention: positive = over-forecasting.

→ forecast_2w_topdown.csv, hierarchical_model_performance.csv, hierarchical_sku_backtest.csv, hierarchical_backtest_summary.csv

**05_forecast_granularity_comparison.ipynb — the control group**

This notebook is what makes that claim testable. Three approaches, same four-week window, same SKU-week evaluation grain, same pooled WAPE:

Approach	                                    Model	                             Pooled WAPE	       Bias	            Accuracy
Daily × SKU direct → aggregated to SKU-week	seasonal_naive_7	                  0.331	             +22.1%	      66.9%
**Weekly × SKU direct	                        moving_average_8	                  0.238	             −3.1%	      76.2%**
Weekly × Sub-Group → allocated to SKU	      moving_average_8 + 80/20 shares	0.237	             −3.1%	      76.3%

A metric note is written out alongside the comparison: the earlier daily-SKU median WAPE (~0.66) is not comparable to pooled WAPE and is reported separately so the two are never conflated. Pooled WAPE weights by volume; median WAPE weights every SKU equally, including near-zero ones. Reporting one and calling it the other is the most common way forecast accuracy gets overstated.

06_build_topdown_forecast_risk.ipynb — planner-facing risk table

Joins the two-week SKU forecast to recent eight-week operational performance:

projected_2w_production = recent 8-week average weekly production × 2
forecast_production_gap = forecast demand − projected production
High = positive production gap and recent delivery-to-demand below 90%
Medium = either condition alone
Every row carries a plain-language risk_reason

Ships with a field dictionary CSV defining each column, and validates row count, key uniqueness, and unexpected nulls before writing.

→ forecast_risk_topdown.csv, forecast_risk_field_dictionary.csv

**Dashboard**

Two-page Power BI report:

Executive Overview — weekly demand / production / delivery trend, gap KPIs, risk counts by tier, top chronic-gap SKUs.
Product Detail — per-SKU history, forecast, allocation share, risk tier and reason.

<img width="2714" height="1535" alt="image" src="https://github.com/user-attachments/assets/f655d25b-7176-4f8d-8e2a-5e83acd4f8ac" />
<img width="2762" height="1492" alt="image" src="https://github.com/user-attachments/assets/ade4e055-4067-45b1-9309-b375571a5e8f" />


Design decisions worth stating

Why naive models rather than ML. With 31 weeks of history across 40 SKUs, there is not enough data for a learned model to beat a well-chosen aggregation level. The finding here is that grain mattered more than model class — which is why the effort went into 05 rather than into hyperparameter tuning. That finding is only credible because the comparison was run on a common grain with a common metric.

Why the risk flags are proxies. No inventory, capacity, or backlog fields exist in the source. Calling the output "stockout risk" would be a fabrication. It is labelled a planning proxy in the notebook, in the field dictionary, and here.

What is not yet used. SupplyGraph ships four edge types — plant, product group, product sub-group, and storage location. This pipeline uses the group hierarchy as an aggregation level; it does not use the edges as learned relations. The dataset's authors report GNN approaches outperforming statistical ML by roughly 10–30% on comparable regression tasks. Closing that gap is the main open item below.

Roadmap
Graph-aware forecasting — treat plant and storage-location edges as relations rather than labels, letting sparse SKUs borrow demand signal from neighbours. This is the natural extension of the top-down idea: a hierarchy is a tree, but the dataset is a graph.
Capacity-constrained risk — replace the 8-week production average with an explicit capacity model once a capacity source exists.
Retire the daily track — 03 is superseded by 04; converge on one risk definition rather than two.
Rolling-origin validation — 31 weeks supports a single four-week holdout and little more; rolling origins would give a firmer accuracy estimate.
Repository structure
.
├── data/
│   ├── raw/                 # SupplyGraph files — not tracked, see Data
│   └── processed/
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_weekly_KPI.ipynb
│   ├── 03_demand_forecasting.ipynb
│   ├── 04_hierarchical_forecasting.ipynb
│   ├── 05_forecast_granularity_comparison.ipynb
│   └── 06_build_topdown_forecast_risk.ipynb
├── dashboard/
│   └── demand_supply_planning.pbix
├── fig/
├── config.py
├── requirements.txt
└── README.md

Paths resolve from config.py; set SUPPLY_CHAIN_OUTPUT_DIR to redirect outputs.

Running it
bash
pip install -r requirements.txt
# download SupplyGraph into data/raw/
# then run notebooks 01 → 06 in order

Open dashboard/demand_supply_planning.pbix and point it at data/processed/.

Author

[Your name] — [LinkedIn] · [email]
