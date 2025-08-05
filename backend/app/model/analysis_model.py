# backend/app/model/analysis_model.py
from pydantic import BaseModel
from typing import List
from datetime import date

class Insight(BaseModel):
    title: str
    description: str

class Conclusion(BaseModel):
    text: str
    reason: str

class SummaryMetrics(BaseModel):
    income_total_filtered: float
    expense_total_filtered: float
    net_balance_filtered: float
    cumulative_balance: float
    average_monthly_expense: float
    emergency_fund_ratio: float
    savings_rate_filtered: float

class ProjectionPoint(BaseModel):
    date: date
    predicted_balance: float

class FinancialAnalysisResponse(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    insights: List[Insight]
    summary_metrics: SummaryMetrics
    conclusion: Conclusion
    projection_data: List[ProjectionPoint]
    

