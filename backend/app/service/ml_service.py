# from backend.app.model.analysis_model import FinancialAnalysisResponse, Insight, SummaryMetrics, Conclusion, ProjectionPoint
# from fastapi.encoders import jsonable_encoder
# from typing import List
# import json

# def analyze_finance(transactions: List[dict]) -> FinancialAnalysisResponse:
#     income_total = sum(txn["amount"] for txn in transactions if txn["type"] is True)
#     expense_total = sum(txn["amount"] for txn in transactions if txn["type"] is False)
#     net_balance = income_total - expense_total

#     # Buat insight
#     if net_balance < 0:
#         insights = [
#             Insight(
#                 title="Pengeluaran Lebih Besar dari Pemasukan",
#                 description="Kamu menghabiskan lebih banyak dari yang kamu hasilkan bulan ini. Pertimbangkan untuk mengurangi pengeluaran yang tidak penting."
#             )
#         ]
#     else:
#         insights = [
#             Insight(
#                 title="Transaksi Terlihat Normal",
#                 description="Tidak ada anomali keuangan yang terdeteksi bulan ini."
#             )
#         ]

#     # Buat summary metrics
#     summary = SummaryMetrics(
#         income=income_total,
#         expense=expense_total,
#         balance=net_balance,
#         savings_ratio=round((net_balance / income_total) * 100, 2) if income_total > 0 else 0.0
#     )

#     # Buat conclusion
#     if summary.savings_ratio >= 20:
#         conclusion = Conclusion(
#             financial_health="Sehat",
#             advice="Kondisi keuanganmu cukup sehat. Pertahankan kebiasaan menabungmu!"
#         )
#     else:
#         conclusion = Conclusion(
#             financial_health="Perlu Ditingkatkan",
#             advice="Usahakan untuk meningkatkan rasio tabunganmu, minimal 20% dari pemasukan."
#         )

#     # Dummy projection data (misal: 6 bulan ke depan)
#     projection_data = [
#         ProjectionPoint(month="2025-08", projected_balance=net_balance * 1.05),
#         ProjectionPoint(month="2025-09", projected_balance=net_balance * 1.1),
#         ProjectionPoint(month="2025-10", projected_balance=net_balance * 1.15),
#         ProjectionPoint(month="2025-11", projected_balance=net_balance * 1.2),
#         ProjectionPoint(month="2025-12", projected_balance=net_balance * 1.25),
#         ProjectionPoint(month="2026-01", projected_balance=net_balance * 1.3),
#     ]

#     # Susun semua ke dalam response model
#     result = FinancialAnalysisResponse(
#         total_income=float(income_total),
#         total_expense=float(expense_total),
#         balance=float(net_balance),
#         insights=insights,
#         summary_metrics=summary,
#         conclusion=conclusion,
#         projection_data=projection_data
#     )

#     # Cetak hasil response ke terminal untuk debugging
#     print("=== HASIL RESPONSE FINANCE ANALYSIS ===")
#     print(json.dumps(jsonable_encoder(result), indent=2))

#     return result



import os
import pickle
from typing import List
from datetime import datetime
import numpy as np
import pandas as pd
from pydantic import BaseModel

from backend.app.model.transaction_model import TransactionBase

# ================= PATH CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "machine"))

PROJECTION_MODEL_PATH = os.path.join(MODEL_DIR, "projection_model.pkl")
ANOMALY_MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_detection_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "category_encoder.pkl")


# ================= LOAD MODELS =================
def load_model(path: str):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load model from {path}: {e}")

projection_model = load_model(PROJECTION_MODEL_PATH)
anomaly_model = load_model(ANOMALY_MODEL_PATH)
category_encoder = load_model(ENCODER_PATH)


# ================= FUNGSI 1: Prediksi Saldo di Masa Depan =================
def predict_future_balance(transactions):
    dates = transactions['date'].tolist()
    balances = transactions['balance'].tolist()

    # Konversi string ke datetime
    dates = [datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date for date in dates]

    date_ordinals = np.array([date.toordinal() for date in dates]).reshape(-1, 1)
    balances = np.array(balances)

    try:
        future_days = 30
        last_date = dates[-1]
        future_dates = [last_date.toordinal() + i for i in range(1, future_days + 1)]
        future_dates_array = np.array(future_dates).reshape(-1, 1)

        future_balances = projection_model.predict(future_dates_array)

        results = [{
            "date": datetime.fromordinal(int(date)).strftime("%Y-%m-%d"),
            "predicted_balance": float(balance)
        } for date, balance in zip(future_dates, future_balances)]

        return results

    except Exception as e:
        raise RuntimeError(f"Failed to predict future balance: {e}")


# ================= FUNGSI 2: Deteksi Anomali =================
def detect_anomalies(data: List) -> List[bool]:
    try:
        if not data:
            return []

        # Pastikan setiap transaksi punya atribut .category berupa string nama kategori
        processed_data = []
        for d in data:
            category_name = None
            # Cek apakah .category ada dan tipe objek Category (atau objek dengan .name)
            if hasattr(d, 'category') and d.category:
                # jika objek, ambil .name-nya
                category_name = getattr(d.category, 'name', None)
            # fallback kalau tidak ada, bisa jadi None atau '__unknown__'
            if not category_name:
                category_name = '__unknown__'
            
            processed_data.append({
                "id": d.id,
                "user_id": d.user_id,
                "transaction_type": d.transaction_type,
                "amount": float(d.amount),
                "transaction_date": d.transaction_date,
                "description": d.description,
                "category": category_name
            })

        df = pd.DataFrame(processed_data)

        if 'category' not in df.columns:
            raise ValueError("Missing 'category' column in transaction data.")

        # Validasi kelas kategori
        known_classes = set(category_encoder.classes_)
        df['category'] = df['category'].apply(lambda x: x if x in known_classes else '__unknown__')

        # Tambahkan '__unknown__' ke encoder jika belum ada
        if '__unknown__' not in category_encoder.classes_:
            category_encoder.classes_ = np.append(category_encoder.classes_, '__unknown__')

        df['category_encoded'] = category_encoder.transform(df['category'])
        df['type'] = df['transaction_type'].apply(lambda x: 1 if x else 0)

        # Prediksi anomali
        X = df[['amount', 'type', 'category_encoded']]
        predictions = anomaly_model.predict(X)

        return [pred == -1 for pred in predictions]

    except Exception as e:
        raise ValueError(f"Failed to detect anomalies: {e}")
