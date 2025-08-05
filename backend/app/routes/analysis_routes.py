from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.database_conn import get_db
from backend.app.service.analysis_service import generate_financial_analysis
from backend.app.model.analysis_model import FinancialAnalysisResponse
from backend.app.auth.auth import get_current_user
from backend.app.database.models import User

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

# Allowed period values
ALLOWED_PERIODS = {"all_time", "last_month", "last_3_months", "last_6_months", "last_year"}

@router.get(
    "/insights",
    response_model=FinancialAnalysisResponse,
    summary="Get Financial Analysis Insights",
    description="Returns a financial health summary and projections based on user transactions."
)
def get_analysis_data(
    period: str = Query(
        default="all_time",
        description="Select the time period for the analysis. Options: all_time, last_month, last_3_months, last_6_months, last_year."
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if period not in ALLOWED_PERIODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period '{period}'. Allowed values are: {', '.join(ALLOWED_PERIODS)}."
        )
    
    try:
        return generate_financial_analysis(current_user.id, db, period)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial analysis: {str(e)}"
        )
