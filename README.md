# FPO Income Impact Measurement – Presentation Ready

Streamlit prototype for the problem statement: developing an algorithm/programme to measure increase in income of FPOs on account of project interventions.

## User flow

Farmer Registration → Farmer Login → Income Record → Individual Dashboard → FPO Aggregation → Reports

## Modules

- Professional project landing page
- Farmer registration and PIN login
- Farmer dashboard
- Income/intervention records
- Before/after income calculation
- Net benefit
- FPO Admin dashboard
- Farmer management/search
- Intervention-wise analysis
- Methodology page
- CSV reports

## Demo admin

Username: `admin`
Password: `admin123`

## Run

```bash
pip3 install -r requirements.txt
python3 -m streamlit run app.py
```

## Calculation

Income Increase = After Income − Before Income

Increase % = (Income Increase / Before Income) × 100

Net Benefit = Income Increase − Intervention Cost

FPO metrics are aggregated from individual farmer records.

## Academic note

This prototype calculates observed before/after differences from entered data. Formal causal attribution requires verified project records and an appropriate evaluation methodology.
