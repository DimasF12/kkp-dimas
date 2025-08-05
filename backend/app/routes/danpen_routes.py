from fastapi import APIRouter
from backend.app.model.danpen_model import PensionInput
from backend.app.service.danpen_services import hitung_dana_pensiun

router = APIRouter()

@router.post("/calculate")
def calculate_pension(data: PensionInput):
    return hitung_dana_pensiun(data)
