from fastapi import APIRouter
from backend.app.model.barangimpian_model import BarangImpianRequest, BarangImpianResponse
from backend.app.service.barangimpian_services import calculate_barang_impian

router = APIRouter()

@router.post("/calculate", response_model=BarangImpianResponse)
def hitung_barang_impian(data: BarangImpianRequest):
    return calculate_barang_impian(data)
