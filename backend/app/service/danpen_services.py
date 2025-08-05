from math import pow
from backend.app.model.danpen_model import PensionInput

def rekomendasi_investasi(tahun_persiapan: int, kekurangan_dana: float):
    if kekurangan_dana == 0:
        return ["Rencana investasi sudah cukup. Tetap disiplin investasi bulanan."]
    
    if tahun_persiapan >= 15:
        return [
            "Saham atau Reksa Dana Saham",
            "ETF berbasis indeks",
            "Properti jangka panjang"
        ]
    elif tahun_persiapan >= 10:
        return [
            "Reksa Dana Campuran",
            "SBN Ritel (Sukuk/ORI) jangka menengah",
            "Deposito atau emas untuk diversifikasi"
        ]
    elif tahun_persiapan >= 5:
        return [
            "Reksa Dana Pendapatan Tetap",
            "Obligasi Negara",
            "Deposito berjangka"
        ]
    else:
        return [
            "Instrumen konservatif seperti: Reksa Dana Pasar Uang, Deposito, atau Tabungan Berjangka",
            "Pertimbangkan untuk menambah jumlah investasi bulanan"
        ]

def hitung_dana_pensiun(data: PensionInput):
    tahun_menuju_pensiun = data.target_usia_pensiun - data.usia_saat_ini
    tahun_hidup_setelah_pensiun = 20  # asumsi default

    if tahun_menuju_pensiun <= 0:
        raise ValueError("Target usia pensiun harus lebih besar dari usia saat ini.")

    # Estimasi pengeluaran bulanan saat pensiun akibat inflasi
    pengeluaran_pensiun = data.pengeluaran_bulanan * pow(1 + data.inflasi / 100, tahun_menuju_pensiun)
    
    # Total kebutuhan dana pensiun
    target_dana_pensiun = pengeluaran_pensiun * 12 * tahun_hidup_setelah_pensiun

    # Perhitungan estimasi investasi yang bisa dikumpulkan
    r = data.return_investasi / 100 / 12  # return bulanan
    n = tahun_menuju_pensiun * 12  # durasi bulan menuju pensiun

    if r == 0:
        estimasi_terkumpul = data.target_investasi_bulanan * n
    else:
        estimasi_terkumpul = data.target_investasi_bulanan * ((pow(1 + r, n) - 1) / r)

    total_estimasi_dana = data.dana_pensiun_saat_ini + estimasi_terkumpul
    kekurangan_dana = max(0, target_dana_pensiun - total_estimasi_dana)

    status = "✅ Tercapai" if total_estimasi_dana >= target_dana_pensiun else "❌ Belum Tercapai"
    saran_tindakan = (
        "Pertahankan ritme investasimu!" if status == "✅ Tercapai"
        else "Tingkatkan investasi bulanan atau pertimbangkan perpanjangan waktu pensiun."
    )

    # Strategi rekomendasi jika belum tercapai
    strategi_rekomendasi = ""
    if status == "❌ Belum Tercapai" and kekurangan_dana > 0 and n > 0:
        tambahan_bulanan = kekurangan_dana / n
        strategi_rekomendasi = (
            f"🎯 Tambahkan investasi bulanan sekitar Rp {tambahan_bulanan:,.2f} "
            f"selama {tahun_menuju_pensiun} tahun ke depan untuk mencapai target dana pensiun. "
            f"Atau pertimbangkan untuk memperpanjang usia pensiun."
        )

    return {
        "target_dana_pensiun": round(target_dana_pensiun),
        "total_dana_terkumpul": round(total_estimasi_dana),
        "kekurangan_dana": round(kekurangan_dana),
        "status": status,
        "saran_tindakan": saran_tindakan,
        "instrumen_rekomendasi": rekomendasi_investasi(tahun_menuju_pensiun, kekurangan_dana),
        "strategi_rekomendasi": strategi_rekomendasi,
        "tahun_persiapan": tahun_menuju_pensiun
    }
