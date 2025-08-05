from backend.app.model.barangimpian_model import BarangImpianRequest, BarangImpianResponse
from textwrap import dedent

def rekomendasi_investasi(return_investasi: float) -> str:
    if return_investasi <= 4:
        return "Reksa Dana Pasar Uang atau Deposito"
    elif return_investasi <= 8:
        return "Reksa Dana Pendapatan Tetap atau Obligasi"
    elif return_investasi <= 12:
        return "Reksa Dana Campuran atau Saham Blue Chip"
    else:
        return "Saham atau Crypto untuk High Risk Tolerance"

def hitung_total_dana_investasi(investasi_bulanan: float, r: float, n: int) -> float:
    if r == 0:
        return investasi_bulanan * n
    return investasi_bulanan * (((1 + r) ** n - 1) / r)

def hitung_saran_tindakan(harga_setelah_inflasi, r, n, investasi_bulanan):
    target_dana_penuh = harga_setelah_inflasi
    dana_terjangkau = hitung_total_dana_investasi(investasi_bulanan, r, n)

    saran_investasi_bulanan = (
        target_dana_penuh / n if r == 0 else
        target_dana_penuh / (((1 + r) ** n - 1) / r)
    )

    dp_persen_disarankan = 100 * (1 - dana_terjangkau / harga_setelah_inflasi)
    dp_persen_disarankan = max(0.0, min(100.0, dp_persen_disarankan))
    dp_nilai_baru = (dp_persen_disarankan / 100) * harga_setelah_inflasi

    saran_tindakan = dedent(f"""
        Meningkatkan investasi bulanan ke Rp {saran_investasi_bulanan:,.0f}
        Memperpanjang waktu target menjadi {n + 6} bulan
        Membayar DP lebih tinggi sekitar {dp_persen_disarankan:.1f}% (Rp {dp_nilai_baru:,.0f}) dari harga barang
    """).strip()

    return saran_tindakan, dp_persen_disarankan, dp_nilai_baru

def calculate_barang_impian(data: BarangImpianRequest) -> BarangImpianResponse:
    r = data.return_investasi / 100 / 12
    n = data.waktu_target_bulan

    harga_setelah_inflasi = data.harga_barang * ((1 + data.inflasi / 100) ** (n / 12))
    dp_nilai = (data.dp_persen / 100) * harga_setelah_inflasi
    target_dana_investasi = harga_setelah_inflasi - dp_nilai

    dana_dari_investasi = hitung_total_dana_investasi(data.investasi_bulanan, r, n)
    total_dana_terkumpul = dana_dari_investasi + dp_nilai
    kekurangan_dana = max(0, harga_setelah_inflasi - total_dana_terkumpul)

    status = "✅ Tercapai" if total_dana_terkumpul >= harga_setelah_inflasi else "❌ Belum Tercapai"

    if status == "✅ Tercapai":
        saran_tindakan = "🎉 Investasi bulanan Anda sudah cukup untuk mencapai tujuan barang impian."
        dp_persen_disarankan = None
        dp_nilai_baru = None
        saran_investasi = None
    else:
        saran_tindakan, dp_persen_disarankan, dp_nilai_baru = hitung_saran_tindakan(
            harga_setelah_inflasi, r, n, data.investasi_bulanan
        )
        saran_investasi = rekomendasi_investasi(data.return_investasi)

    return BarangImpianResponse(
        harga_setelah_inflasi=round(harga_setelah_inflasi, 2),
        dana_yang_perlu_dikumpulkan=round(harga_setelah_inflasi, 2),
        total_dana_terkumpul=round(total_dana_terkumpul, 2),
        status=status,
        kekurangan_dana=round(kekurangan_dana, 2),
        saran_investasi=saran_investasi,
        saran_tindakan=saran_tindakan,
        dp_persen_disarankan=round(dp_persen_disarankan, 1) if dp_persen_disarankan is not None else None,
        dp_nilai=round(dp_nilai, 2)
    )
