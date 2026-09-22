# Developing an algorithm/programme to measure increase in income of FPOs on account of project interventions

## Project
This project provides a simple dashboard for measuring the increase in income of Farmer Producer Organizations (FPOs) attributable to entered project intervention activities.

## Main calculation

Intervention Income =
Demand-based Services Income + CHC Income + Produce Marketing Income + Other Intervention Income

Income After Intervention =
Baseline Income + Intervention Income

Income Increase =
Income After Intervention - Baseline Income

Percentage Increase =
(Income Increase / Baseline Income) × 100

## Features
- FPO-wise data entry
- Baseline income measurement
- Intervention-wise income entry
- Automatic income increase calculation
- Percentage increase calculation
- FPO comparison dashboard
- Intervention contribution chart
- CSV results download
- SQLite local database

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit address shown in the terminal.

## Folder structure

```text
FPO_Income_Project/
├── app.py
├── requirements.txt
├── README.md
├── fpo_income.db       # created automatically when the app runs
└── data/
    └── sample_fpo_data.csv
```
