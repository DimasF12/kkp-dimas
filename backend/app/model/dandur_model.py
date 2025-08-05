from pydantic import BaseModel
from typing import Optional

class EmergencyFundRequest(BaseModel):
    pengeluaran_wajib: float
    sudah_menikah: bool
    jumlah_tanggungan: int
    waktu_pengumpulan_bulan: int
    dana_darurat_saat_ini: float
    target_investasi_bulanan: float
    return_investasi: float  # dalam persen

class EmergencyFundResponse(BaseModel):
    target_dana_darurat: float
    kekurangan_dana: float
    estimasi_dana_terkumpul: float
    status: str
    bulan_tanggungan: int
    instrumen_rekomendasi: str
    saran: Optional[str] = None
    strategi_rekomendasi: Optional[str]
