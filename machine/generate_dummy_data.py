import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

# Simulasi kategori dari database (id, tipe, nama)
categories = [
    (1, 'income', 'Gaji'),
    (2, 'income', 'Freelance'),
    (3, 'income', 'Bonus'),
    (4, 'income', 'Investasi'),
    (5, 'income', 'Sewa Properti'),
    (6, 'income', 'Dividen'),
    (7, 'income', 'Hadiah Uang'),
    (8, 'income', 'Penjualan Aset'),
    (9, 'expense', 'Makanan'),
    (10, 'expense', 'Transportasi'),
    (11, 'expense', 'Hiburan'),
    (12, 'expense', 'Belanja'),
    (13, 'expense', 'Tagihan'),
    (14, 'expense', 'Kesehatan'),
    (15, 'expense', 'Edukasi'),
    (16, 'expense', 'Rumah Tangga'),
    (17, 'expense', 'Pakaian'),
    (18, 'expense', 'Utilitas'),
    (19, 'expense', 'Asuransi'),
    (20, 'expense', 'Donasi/Amal'),
    (21, 'expense', 'Olahraga/Fitness'),
    (22, 'expense', 'Perawatan Diri'),
    (23, 'expense', 'Pulsa/Paket Data'),
    (24, 'expense', 'Perjalanan'),
    (25, 'both', 'Lain-lain'),
]

# Deskripsi per kategori sederhana, bisa dikembangkan
descriptions = {
    'Gaji': ["Gaji bulanan", "Gaji kantor", "Gaji lembur"],
    'Freelance': ["Proyek freelance", "Pendapatan freelance", "Honor freelance"],
    'Bonus': ["Bonus tahunan", "Bonus proyek", "Bonus kinerja"],
    'Investasi': ["Penjualan saham", "Dividen saham", "Keuntungan investasi"],
    'Sewa Properti': ["Sewa apartemen", "Sewa rumah", "Pendapatan sewa"],
    'Dividen': ["Dividen perusahaan", "Pembagian dividen", "Pendapatan dividen"],
    'Hadiah Uang': ["Hadiah lomba", "Hadiah acara", "Uang hadiah"],
    'Penjualan Aset': ["Jual mobil", "Jual elektronik", "Jual aset lainnya"],
    
    'Makanan': ["Belanja bahan makanan", "Makan di restoran", "Snack dan minuman"],
    'Transportasi': ["Bensin", "Tiket kereta", "Ojek online"],
    'Hiburan': ["Bioskop", "Konser musik", "Langganan Netflix"],
    'Belanja': ["Belanja pakaian", "Belanja kebutuhan rumah", "Belanja online"],
    'Tagihan': ["Tagihan listrik", "Tagihan air", "Tagihan internet"],
    'Kesehatan': ["Obat-obatan", "Konsultasi dokter", "Pemeriksaan kesehatan"],
    'Edukasi': ["Buku pelajaran", "Kursus online", "Seminar edukasi"],
    'Rumah Tangga': ["Peralatan rumah", "Perbaikan rumah", "Perlengkapan rumah"],
    'Pakaian': ["Baju baru", "Sepatu", "Aksesoris"],
    'Utilitas': ["Listrik", "Air", "Gas"],
    'Asuransi': ["Asuransi kesehatan", "Asuransi kendaraan", "Asuransi jiwa"],
    'Donasi/Amal': ["Donasi ke panti asuhan", "Sedekah", "Amal jariyah"],
    'Olahraga/Fitness': ["Gym", "Peralatan olahraga", "Kelas fitness"],
    'Perawatan Diri': ["Salon", "Kosmetik", "Perawatan kulit"],
    'Pulsa/Paket Data': ["Pulsa telepon", "Paket internet", "Langganan data"],
    'Perjalanan': ["Tiket pesawat", "Hotel", "Transportasi lokal"],
    'Lain-lain': ["Pengeluaran tak terduga", "Lainnya", "Miscellaneous"],
}

def random_date(start, end):
    delta = end - start
    int_delta = delta.days
    random_day = random.randint(0, int_delta)
    return start + timedelta(days=random_day)

def generate_dummy_transactions(num=3000, max_user_id=5):
    data = []
    start_date = datetime.now() - timedelta(days=365*2)
    end_date = datetime.now()

    # Pisahkan kategori berdasarkan tipe
    income_categories = [c for c in categories if c[1] == 'income']
    expense_categories = [c for c in categories if c[1] == 'expense']

    for i in range(1, num+1):
        user_id = random.randint(1, max_user_id)
        transaction_type = random.choices([True, False], weights=[0.4, 0.6])[0]

        if transaction_type:
            cat = random.choice(income_categories)
            category_id = cat[0]
            category_name = cat[2]
            amount = round(random.uniform(1_000_000, 10_000_000), 2)
        else:
            cat = random.choice(expense_categories)
            category_id = cat[0]
            category_name = cat[2]
            amount = round(random.uniform(10_000, 5_000_000), 2)

        desc_list = descriptions.get(category_name, ["Transaksi"])
        description = random.choice(desc_list)
        transaction_date = random_date(start_date, end_date).date()

        data.append({
            "id": i,
            "user_id": user_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "transaction_date": transaction_date,
            "description": description,
            "category_id": category_id
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    dummy_df = generate_dummy_transactions(5000, max_user_id=5)
    print(dummy_df.head())
    dummy_df.to_csv("dummy_transactions_v2.csv", index=False)
