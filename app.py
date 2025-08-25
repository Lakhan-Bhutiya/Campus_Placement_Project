import streamlit as st
import pandas as pd
import pickle
import math
import altair as alt

# ---
# Why my code based on 3 - 5 kpis


# The original dataset contains over 470 different KPIs.  
# For a real dealership, that much complexity makes it hard to build an **actionable planning tool**.

# So in this project I focused on a core set of financial and operational KPIs:

# Financial KPIs: Revenue, Expense, Payroll, Profit  
# Operational KPIs: Outlander Units, RVR Units, Eclipse Cross Units, Mirage Units  

# These are the drivers that truly impact profitability  
# By keeping the tool simple, a manager can quickly set profit targets and see what actions (like selling more vehicles) are required.

#  The other KPIs are not lost — they are still categorized in the data,  
# but showing all 470+ in the planner would make it **confusing and unusable**.



# --- 1. LOAD PRE-TRAINED MODELS ---
@st.cache_resource
def load_models(model_filepath='trained_models.pkl'):
    """Loads the dictionary of trained models from a file."""
    try:
        with open(model_filepath, 'rb') as f:
            models = pickle.load(f)
        return models
    except FileNotFoundError:
        st.error(f"Error: The model file '{model_filepath}' was not found. Please run 'model_training.py' first.")
        return None

# --- 2. DEFINE BUSINESS LOGIC (ASSUMPTIONS) ---
BUSINESS_LOGIC = {
    'Outlander': {'revenue': 30000, 'cost_of_sales': 25000},
    'RVR': {'revenue': 24000, 'cost_of_sales': 20000},
    'Eclipse Cross': {'revenue': 28000, 'cost_of_sales': 24000},
    'Mirage': {'revenue': 18000, 'cost_of_sales': 15000}
}
COMMISSION_RATE = 0.05

for model, data in BUSINESS_LOGIC.items():
    revenue = data['revenue']
    cost = data['cost_of_sales']
    commission = revenue * COMMISSION_RATE
    data['profit_per_unit'] = revenue - cost - commission
PROFITABLE_MODELS = sorted(BUSINESS_LOGIC.items(), key=lambda item: item[1]['profit_per_unit'], reverse=True)

# --- 3. MAIN APPLICATION FUNCTION ---
def run_planner_app():
    """
    This function contains the main logic for the interactive planner.
    """
    models = load_models()

    if models:
        # --- 4. GENERATE BASELINE FORECAST ---
        baseline_forecasts = {}
        for name, model in models.items():
            forecast = model.forecast(steps=3)
            if name in BUSINESS_LOGIC:
                forecast = forecast.fillna(0).round(0).astype(int)
            baseline_forecasts[name] = forecast

        df_summary = pd.DataFrame(index=baseline_forecasts['Currency:Revenue/Sales'].index)
        df_summary['Revenue'] = baseline_forecasts['Currency:Revenue/Sales']
        df_summary['Expense'] = baseline_forecasts['Currency:Expense']
        df_summary['Payroll'] = baseline_forecasts['Currency:Payroll/Compensation']
        for model_name in BUSINESS_LOGIC:
            if model_name in baseline_forecasts:
                df_summary[f'{model_name}_Units'] = baseline_forecasts[model_name]
        df_summary['Profit'] = df_summary['Revenue'] - (df_summary['Expense'] + df_summary['Payroll'])

        # --- 5. SIDEBAR FOR NAVIGATION ---
        st.sidebar.title("Navigation")
        planner_mode = st.sidebar.radio("Choose a Planner Mode", ('What-If Scenario', 'Target-Based Plan'))
        
        st.sidebar.header("Select Month")
        target_month_str = st.sidebar.selectbox(
            'Select a month to plan for:',
            options=df_summary.index.strftime('%B %Y')
        )
        target_month_date = pd.to_datetime(target_month_str)

        # --- 6. MAIN APP LOGIC ---
        st.header('Baseline 3-Month Forecast')
        st.dataframe(df_summary.style.format(formatter="{:,.0f}").set_properties(**{'text-align': 'right'}))

        df_updated = df_summary.copy()
        
        if planner_mode == 'What-If Scenario':
            st.header('What-If Scenario Planner')
            st.write("Adjust the sliders to see the impact of selling more vehicles.")

            adjustments = {}
            with st.expander("Adjust Vehicle Sales Units", expanded=True):
                for model_name in BUSINESS_LOGIC:
                    if model_name in models:
                        adjustments[model_name] = st.slider(f"Additional '{model_name}' units:", 0, 50, 0, 1)
            
            total_revenue_change, total_cost_change, total_payroll_change = 0, 0, 0
            for model_name, additional_units in adjustments.items():
                if additional_units > 0:
                    revenue_change = additional_units * BUSINESS_LOGIC[model_name]['revenue']
                    cost_change = additional_units * BUSINESS_LOGIC[model_name]['cost_of_sales']
                    total_revenue_change += revenue_change
                    total_cost_change += cost_change
                    total_payroll_change += revenue_change * COMMISSION_RATE
                    df_updated.loc[target_month_date, f'{model_name}_Units'] += additional_units

            df_updated.loc[target_month_date, 'Revenue'] += total_revenue_change
            df_updated.loc[target_month_date, 'Expense'] += total_cost_change
            df_updated.loc[target_month_date, 'Payroll'] += total_payroll_change

        elif planner_mode == 'Target-Based Plan':
            st.header('Target-Based Planner')
            baseline_profit = df_summary.loc[target_month_date, 'Profit']
            profit_target = st.number_input(f'Enter your profit target for {target_month_str}:',
                                            min_value=int(baseline_profit),
                                            value=int(baseline_profit + 50000),
                                            step=1000, format="%d")
            profit_gap = profit_target - baseline_profit

            if profit_gap > 0:
                units_to_sell = {}
                remaining_gap = profit_gap
                for model_name, data in PROFITABLE_MODELS:
                    if model_name not in models: continue
                    profit_per_unit = data['profit_per_unit']
                    if remaining_gap > 0 and profit_per_unit > 0:
                        additional_units = math.ceil(remaining_gap / profit_per_unit)
                        units_to_sell[model_name] = additional_units
                        revenue_change = additional_units * data['revenue']
                        cost_change = additional_units * data['cost_of_sales']
                        payroll_change = revenue_change * COMMISSION_RATE
                        df_updated.loc[target_month_date, f'{model_name}_Units'] += additional_units
                        df_updated.loc[target_month_date, 'Revenue'] += revenue_change
                        df_updated.loc[target_month_date, 'Expense'] += cost_change
                        df_updated.loc[target_month_date, 'Payroll'] += payroll_change
                        remaining_gap = 0
                
                st.subheader("Action Plan:")
                cols = st.columns(len(units_to_sell))
                for i, (model, units) in enumerate(units_to_sell.items()):
                    cols[i].metric(label=f"Sell more '{model}'", value=f"{units} units")

        # --- 7. FINAL CALCULATIONS AND DISPLAY ---
        df_updated['Profit'] = df_updated['Revenue'] - (df_updated['Expense'] + df_updated['Payroll'])
        
        st.subheader(f'Final Adjusted Forecast for {target_month_str}')
        
        final_plan_display = df_updated.loc[[target_month_date]]
        
        def highlight_row(row):
            return ['background-color: #d1e7dd'] * len(row)

        st.dataframe(final_plan_display.style.format(formatter="{:,.0f}").set_properties(**{'text-align': 'right'}).apply(highlight_row, axis=1))

        # --- 8. VISUALIZATION ---
        st.subheader('Visual Comparison')
        baseline_profit = df_summary.loc[target_month_date, 'Profit']
        adjusted_profit = df_updated.loc[target_month_date, 'Profit']
        
        chart_data = pd.DataFrame({
            'Plan': ['Baseline Forecast', 'Adjusted Plan'],
            'Profit': [baseline_profit, adjusted_profit]
        })
        
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Plan', sort=None),
            y='Profit',
            color=alt.Color('Plan', scale=alt.Scale(range=['#4c78a8', '#54a24b']))
        ).properties(
            title=f'Profit Comparison for {target_month_str}'
        )
        st.altair_chart(chart, use_container_width=True)

# --- INTRODUCTION PAGE ---
def introduction_page():
    """
    Displays the introduction page with a button to launch the main app.
    """
    st.set_page_config(layout="centered")
    st.title("Welcome to the Dealership KPI Forecasting Tool")
    
    st.markdown("""
    Hi 👋, thanks for reviewing my project.

    I want to be very clear that **I am serious about this job opportunity**.  
    I have already worked on **machine learning projects**, but this one is special:  
    it’s my **first time series project**.  

    Because of that, I know this may **not reflect my full potential** —   
    Still, I’ve worked hard to build a working forecasting and planning tool,  
    and I’m eager to learn and grow further.

    ### Please note: there is also a **separate file for data visualization**.  
    Make sure to check that for deeper insights.

    ---

    ### Project Steps
    1.  **Data Cleaning & Preparation**: The raw data was thoroughly cleaned, validated, and categorized.
    2.  **Model Training**: A suite of time-series forecasting models were trained on historical data to predict future performance.
    3.  **Interactive Planning**: The tool below loads these trained models to provide an interactive experience for business planning.

    Click the button below to begin.
    """)

    if st.button("🚀 Launch Planner"):
        st.session_state.app_started = True
        # --- ERROR FIX: Use the modern st.rerun() command ---
        st.rerun()

# --- MAIN SCRIPT EXECUTION ---
if 'app_started' not in st.session_state:
    st.session_state.app_started = False

if st.session_state.app_started:
    run_planner_app()
else:
    introduction_page()
