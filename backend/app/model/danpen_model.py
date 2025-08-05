from pydantic import BaseModel
from typing import Optional

class PensionInput(BaseModel):
    pengeluaran_bulanan: float
    usia_saat_ini: int
    target_usia_pensiun: int
    inflasi: int = 4
    dana_pensiun_saat_ini: float
    target_investasi_bulanan: float
    return_investasi: float

class PensionOutput(BaseModel):
    target_dana_pensiun: float
    total_dana_terkumpul: float
    kekurangan_dana: float
    status: str
    saran_tindakan: str
    instrumen_rekomendasi: str
    strategi_rekomendasi: Optional[str] = None

    
