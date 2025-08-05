from fastapi import APIRouter
from backend.app.model.dandur_model import EmergencyFundRequest, EmergencyFundResponse
from backend.app.service.dandur_services import hitung_emergency_fund

router = APIRouter()

@router.post("/calculate", response_model=EmergencyFundResponse)
def calculate_emergency_fund(request: EmergencyFundRequest):
    result = hitung_emergency_fund(
        pengeluaran_wajib=request.pengeluaran_wajib,
        sudah_menikah=request.sudah_menikah,
        jumlah_tanggungan=request.jumlah_tanggungan,
        waktu_pengumpulan_bulan=request.waktu_pengumpulan_bulan,
        dana_darurat_saat_ini=request.dana_darurat_saat_ini,
        target_investasi_bulanan=request.target_investasi_bulanan,
        return_investasi=request.return_investasi
    )
    return result
