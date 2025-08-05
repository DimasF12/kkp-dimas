import pandas as pd

def calculate_summary_metrics(df: pd.DataFrame, income_total: float, expense_total: float, balance: float):
    df["month"] = df["transaction_date"].dt.to_period("M")
    unique_months = df["month"].nunique()
    avg_month_count = max(1, unique_months)

    average_monthly_expense = expense_total / avg_month_count
    emergency_fund_ratio = balance / max(1, average_monthly_expense)
    savings_rate = (income_total - expense_total) / income_total if income_total > 0 else 0

    return average_monthly_expense, emergency_fund_ratio, savings_rate
