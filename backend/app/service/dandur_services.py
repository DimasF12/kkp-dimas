from math import pow

def rekomendasi_instrumen(return_investasi: float) -> str:
    """
    Memberikan rekomendasi instrumen investasi berdasarkan return yang diharapkan.
    """
    if return_investasi <= 2:
        return (
            "Tabungan Bank*: Cocok untuk kamu yang menginginkan keamanan dan fleksibilitas. "
            "Risiko rendah, mudah dicairkan, namun imbal hasil terbatas."
        )
    elif return_investasi <= 4:
        return (
            "Deposito Berjangka: Aman dan stabil, cocok untuk kamu yang ingin sedikit return lebih tinggi "
            "tanpa mengambil banyak risiko."
        )
    elif return_investasi <= 8:
        return (
            "Reksa Dana Pasar Uang: Ideal untuk tujuan jangka pendek-menengah, dengan likuiditas tinggi dan risiko rendah."
        )
    elif return_investasi <= 12:
        return (
            "Obligasi / Sukuk: Memberikan pendapatan tetap, cocok untuk kamu yang siap dengan komitmen jangka menengah "
            "dengan risiko moderat."
        )
    else:
        return (
            "Saham / Reksa Dana Saham: Potensi imbal hasil tinggi untuk jangka panjang, namun disertai risiko yang besar."
        )

def hitung_bulan_tanggungan(sudah_menikah: bool, jumlah_tanggungan: int) -> int:
    """
    Menentukan berapa bulan tanggungan dana darurat berdasarkan status pernikahan dan jumlah tanggungan.
    """
    if sudah_menikah and jumlah_tanggungan > 0:
        return 12
    elif sudah_menikah:
        return 6
    else:
        return 3

def hitung_emergency_fund(
    pengeluaran_wajib: float,
    sudah_menikah: bool,
    jumlah_tanggungan: int,
    waktu_pengumpulan_bulan: int,
    dana_darurat_saat_ini: float,
    target_investasi_bulanan: float,
    return_investasi: float
) -> dict:
    """
    Menghitung kebutuhan dan progres pengumpulan dana darurat.
    """
    if pengeluaran_wajib < 0 or waktu_pengumpulan_bulan <= 0 or target_investasi_bulanan < 0 or dana_darurat_saat_ini < 0:
        raise ValueError("Input tidak valid. Semua nilai harus positif dan waktu harus lebih dari 0.")

    bulan_tanggungan = hitung_bulan_tanggungan(sudah_menikah, jumlah_tanggungan)
    target_dana = pengeluaran_wajib * bulan_tanggungan

    r = return_investasi / 100 / 12  # konversi ke bulanan
    n = waktu_pengumpulan_bulan

    # Hitung estimasi dana yang bisa dikumpulkan
    if r == 0:
        estimasi_dana = target_investasi_bulanan * n
    else:
        estimasi_dana = target_investasi_bulanan * ((pow(1 + r, n) - 1) / r)

    # 🔁 Perhitungan ulang kekurangan dana yang logis
    total_potensi_dana = dana_darurat_saat_ini + estimasi_dana
    kekurangan_dana = max(0, target_dana - total_potensi_dana)

    status = "✅ Tercapai, Pertahankan ritme investasimu!" if estimasi_dana >= kekurangan_dana else "❌ Belum Tercapai"
    saran = "Pertahankan ritme investasimu!" if status == "✅ Tercapai" else "Tingkatkan investasi bulanan atau perpanjang waktu."

    strategi_rekomendasi = ""
    if status == "❌ Belum Tercapai" and kekurangan_dana > 0:
        required_bulanan = kekurangan_dana / waktu_pengumpulan_bulan
        strategi_rekomendasi = (
            f"🎯 Anda perlu menambah investasi bulanan sekitar Rp {required_bulanan:,.2f}"
            f"selama {waktu_pengumpulan_bulan} bulan ke depan agar dana darurat tercapai."
            f"Alternatif lain, perpanjang waktu pengumpulan atau kurangi target tanggungan."
        )

    return {
        "target_dana_darurat": round(target_dana, 2),
        "dana_darurat_saat_ini": round(dana_darurat_saat_ini, 2),
        "kekurangan_dana": round(kekurangan_dana, 2),
        "estimasi_dana_terkumpul": round(estimasi_dana, 2),
        "bulan_tanggungan": bulan_tanggungan,
        "status": status,
        "saran_tindakan": saran,
        "instrumen_rekomendasi": rekomendasi_instrumen(return_investasi),
        "strategi_rekomendasi": strategi_rekomendasi
    }
