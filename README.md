Campus Placement Project — Dealership KPI Forecasting & Planning Tool

This project was developed as part of my campus placement practical task.
It focuses on time series forecasting for a car dealership’s key performance indicators (KPIs), with an interactive Streamlit goal-seeking planner.

🔑 Project Highlights

Data Cleaning & Preparation

470+ raw KPIs cleaned, validated, and categorized into business-friendly groups.

Simplified focus on 3 financial KPIs (Revenue, Expense, Payroll → Profit) and 4 operational KPIs (Outlander, RVR, Eclipse Cross, Mirage unit sales).

Model Training

Built using Exponential Smoothing models from statsmodels.

Robust logic: seasonal models if ≥24 months of data, otherwise simpler non-seasonal.

Interactive Planning App (app.py)

📈 Baseline Forecast: Revenue, Expense, Payroll, Profit for 3 months ahead.

🛠️ What-If Scenario: Adjust vehicle sales manually, see instant impact.

🎯 Target-Based Plan: Enter a profit target → app calculates required unit sales.

Campus_Placement_Project/
│
├── data/
│   ├── FS-data-80475.csv         # Dealership dataset (or sample for demo)
│   ├── categorized_kpis.csv      # KPI category mapping
│
├── trained_models.pkl            # Pre-trained models for Streamlit app
│
├── app.py                        # Streamlit interactive app
├── model_training.ipynb          # Model training steps
├── visualization.ipynb           # Data visualization & EDA
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python version pin (for Streamlit Cloud)
└── README.md                     # Project documentation

Clean UI with Streamlit + Altair charts.

Visualization Notebook (visualization.ipynb)

How to Run Locally

Clone the repo

git clone https://github.com/Lakhan-Bhutiya/Campus_Placement_Project.git
cd Campus_Placement_Project


Create virtual environment (Windows)

python -m venv .venv
.\.venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Run the Streamlit app

streamlit run app.py

Exploratory analysis of KPIs.

Charts comparing baseline vs adjusted plans.

Live Demo (Streamlit Cloud)
# https://campusplacementproject-nkucatm3eonhhdfdt3jy5.streamlit.app/

Notes

This is my first time series project — I’ve worked on ML projects before, but this one was new territory.

The dataset had 470+ KPIs; I focused on a core set to keep the tool simple and actionable.
