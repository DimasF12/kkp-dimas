from pydantic import BaseModel

class BarangImpianRequest(BaseModel):
    waktu_target_bulan: int
    harga_barang: float
    dp_persen: float  # Tetap disimpan kalau dibutuhkan nanti
    inflasi: float = 4.0
    investasi_bulanan: float
    return_investasi: float

class BarangImpianResponse(BaseModel):
    harga_setelah_inflasi: float
    dana_yang_perlu_dikumpulkan: float
    total_dana_terkumpul: float
    status: str
    kekurangan_dana: float
    saran_investasi: str | None = None
    saran_tindakan: str | None = None
    dp_persen_disarankan: float | None = None 
    dp_nilai: float | None = None  # nilai DP dalam rupiah


