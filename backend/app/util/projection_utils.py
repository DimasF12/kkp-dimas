from datetime import datetime, timedelta
from typing import List
import pandas as pd
import numpy as np

from backend.app.model.transaction_model import TransactionBase
from backend.app.service.ml_service import projection_model

def prepare_cumulative_balance_df(df: pd.DataFrame) -> pd.DataFrame:
    if "transaction_date" not in df.columns or "amount" not in df.columns:
        raise ValueError("DataFrame must contain 'transaction_date' and 'amount' columns.")

    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df = df.sort_values(by="transaction_date")
    df["balance"] = df["amount"].cumsum()
    return df[["transaction_date", "balance"]]

def prepare_projection_dataframe(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Siapkan DataFrame saldo kumulatif berdasarkan transaksi, 
    menghasilkan kolom ['transaction_date', 'balance'].
    """
    df = transactions_df.copy()

    # Gunakan 'transaction_date' atau fallback ke 'date'
    if 'transaction_date' not in df.columns:
        if 'date' in df.columns:
            df['transaction_date'] = df['date']
        else:
            raise ValueError("Kolom 'transaction_date' atau 'date' tidak ditemukan.")

    # Validasi kolom
    required = ['amount', 'transaction_type', 'transaction_date']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    # Tipe tanggal dan net_amount
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df.dropna(subset=['transaction_date'], inplace=True)
    df['net_amount'] = df.apply(lambda r: r['amount'] if r['transaction_type'] else -r['amount'], axis=1)

    # Urut & hitung saldo kumulatif
    df.sort_values('transaction_date', inplace=True)
    df['balance'] = df['net_amount'].cumsum()

    return df[['transaction_date', 'balance']]

def predict_future_balance(balance_df: pd.DataFrame, days_ahead: int = 30) -> List[dict]:
    """
    Prediksi saldo masa depan berdasarkan rata-rata kenaikan saldo harian,
    bukan berdasarkan tren linear absolut.
    """
    if balance_df.empty:
        raise ValueError("DataFrame kosong, tidak bisa lakukan prediksi.")

    required = ['transaction_date', 'balance']
    for col in required:
        if col not in balance_df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Urutkan data
    balance_df = balance_df.sort_values('transaction_date')
    balance_df['transaction_date'] = pd.to_datetime(balance_df['transaction_date'])

    # Hitung selisih hari dari tanggal pertama
    balance_df['day_index'] = (balance_df['transaction_date'] - balance_df['transaction_date'].min()).dt.days
    X = balance_df[['day_index']]
    y = balance_df['balance']

    # Latih model linear
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)

    # Prediksi untuk hari ke depan
    last_day_index = balance_df['day_index'].max()
    future_day_indices = np.array([last_day_index + i for i in range(1, days_ahead + 1)]).reshape(-1, 1)

    # Tanggal masa depan
    last_date = balance_df['transaction_date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]

    future_predictions = model.predict(future_day_indices)

    # Format hasil
    results = []
    for date, pred in zip(future_dates, future_predictions):
        results.append({
            "date": date.strftime("%Y-%m-%d"),
            "predicted_balance": round(float(pred), 2)
        })

    return results


def filter_transactions_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Filter transaksi berdasarkan periode pilihan user.
    """
    if 'transaction_date' not in df.columns:
        raise ValueError("DataFrame harus memiliki kolom 'transaction_date'.")

    df = df.copy()
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df.dropna(subset=['transaction_date'], inplace=True)

    today = pd.Timestamp.today()

    if period == "last_month":
        start_date = today - pd.DateOffset(days=30)
    elif period == "3_months":
        start_date = today - pd.DateOffset(months=3)
    elif period == "6_months":
        start_date = today - pd.DateOffset(months=6)
    elif period == "year_to_date":
        start_date = pd.Timestamp(year=today.year, month=1, day=1)
    elif period == "all_time":
        return df
    else:
        raise ValueError(f"Periode tidak dikenali: {period}")

    return df[df['transaction_date'] >= start_date]
