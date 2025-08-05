from fastapi import APIRouter, HTTPException
from backend.app.model.calculator_model import InvestmentRequest
from backend.app.service.calculator_services import (
    calculate_future_value,
    calculate_required_monthly_investment,
    calculate_required_duration,
    recommend_investments,
    get_investment_risk_profile
)

router = APIRouter()

@router.post("/calculator")
def calculate(request: InvestmentRequest):
    try:
        future_value = calculate_future_value(
            request.uangSaatIni,
            request.targetInvestasi,
            request.returnInvestasi,
            request.waktu
        )

        risk_profile = get_investment_risk_profile(request.returnInvestasi)

        if future_value >= request.uangCapai:
            return {
                'message': f"Selamat! Anda akan memiliki Rp {future_value:,.2f} setelah {request.waktu} tahun, yang memenuhi target Anda.🥳🥳🤩🤩",
                'inputUser' : {
                'uangSaatIni' : request.uangSaatIni,
                'targetInvestasi' : request.targetInvestasi,
                'returnInvestasi' : request.returnInvestasi,
                'waktuDibutuhkan' : request.waktu,
                'targetUang' :request.uangCapai,
                },
                'hasilInvestasi': future_value,
                'totalUangDibutuhkan': request.uangCapai,
                'risk_profile': {
                    'resiko' : risk_profile
                },
            }
        else:
            required_monthly_investment = calculate_required_monthly_investment(
                request.uangSaatIni,
                request.uangCapai,
                request.returnInvestasi,
                request.waktu
            )
            required_duration = calculate_required_duration(
                request.uangSaatIni,
                request.targetInvestasi,
                request.returnInvestasi,
                request.uangCapai
            )
            recommendations = recommend_investments(request.returnInvestasi)

            return {
                'message': (
                    f"Strategi Anda belum cocok. Anda memerlukan investasi bulanan sebesar "
                    f"Rp {required_monthly_investment:,.2f} setiap bulan selama {request.waktu} tahun, atau perpanjang durasi "
                    f"hingga {required_duration:.2f} tahun untuk mencapai target.😟😟"
                ),
                'inputUser' : {
                'uangSaatIni' : request.uangSaatIni,
                'targetInvestasi' : request.targetInvestasi,
                'returnInvestasi' : request.returnInvestasi,
                'waktuDibutuhkan' : request.waktu,
                'targetUang' :request.uangCapai,
                },
                'hasilInvestasi': future_value,
                'totalUangDibutuhkan': request.uangCapai,
                'risk_profile': {
                    'resiko' : risk_profile
                },
                'rekomendasi': recommendations
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")