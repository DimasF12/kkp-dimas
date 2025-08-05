from pydantic import BaseModel
from typing import List, Optional, Dict

class InvestmentRequest(BaseModel):
    uangSaatIni: float
    targetInvestasi: float
    returnInvestasi: float
    waktu: int
    uangCapai: float

class Recommendation(BaseModel):
    investment_type: str
    return_rate: float
    risk_level: str

class CalculatorResponse(BaseModel):
    uangSaatIni: float
    targetInvestasi: float
    returnInvestasi: float
    waktu: int
    uangCapai: float

    hasilInvestasi: float
    totalUangDibutuhkan: float
    message: str
    rekomendasi: Optional[List[Recommendation]] = None
