# backend/app/service/analysis_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date, timedelta
import collections 

import pandas as pd
import numpy as np
import joblib 
import os 
from sklearn.linear_model import LinearRegression 
from sklearn.ensemble import IsolationForest 

# --- Perbaikan Import Path ---
from backend.app.database import models 
from backend.app.model.transaction_model import TransactionResponse 
from backend.app.model.category_model import CategoryResponse 
from backend.app.model.analysis_model import FinancialAnalysisResponse, SummaryMetrics, Insight, Conclusion 
# --- Akhir Perbaikan Import Path ---

# --- Variabel Global untuk Model ML ---
ML_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'machine', 'ml_models')
PROJECTION_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'projection_model.pkl')
ANOMALY_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'anomaly_detection_model.pkl')

projection_model = None
anomaly_model = None

try:
    projection_model = joblib.load(PROJECTION_MODEL_PATH)
    print(f"Model proyeksi berhasil dimuat dari: {PROJECTION_MODEL_PATH}")
except FileNotFoundError:
    print(f"WARNING: Model proyeksi tidak ditemukan di {PROJECTION_MODEL_PATH}. Proyeksi akan menggunakan logika fallback atau tidak tersedia.")
except Exception as e:
    print(f"ERROR: Gagal memuat model proyeksi: {e}")

try:
    anomaly_model = joblib.load(ANOMALY_MODEL_PATH)
    print(f"Model deteksi anomali berhasil dimuat dari: {ANOMALY_MODEL_PATH}")
except FileNotFoundError:
    print(f"WARNING: Model deteksi anomali tidak ditemukan di {ANOMALY_MODEL_PATH}. Deteksi anomali tidak akan tersedia.")
except Exception as e:
    print(f"ERROR: Gagal memuat model deteksi anomali: {e}")


def get_monthly_expense_average(transactions: List[Dict]) -> float:
    monthly_expenses = collections.defaultdict(float)
    for trans in transactions:
        if trans['type'] == 'expense': 
            trans_date = trans['date']
            month_year = f"{trans_date.year}-{trans_date.month}"
            monthly_expenses[month_year] += trans['amount']
    
    months_count = len(monthly_expenses)
    total_past_expense = sum(monthly_expenses.values())
    return total_past_expense / months_count if months_count > 0 else 0

def filter_transactions_by_period_py(
    transactions: List[Dict], 
    period: str
) -> List[Dict]:
    now = date.today()
    start_date = None
    end_date = now 

    if period == 'last_month':
        first_day_of_current_month = now.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        start_date = last_day_of_last_month.replace(day=1)
        end_date = last_day_of_last_month
    elif period == 'last_3_months':
        start_date = (now.replace(day=1) - pd.DateOffset(months=2)).date() 
        end_date = now 
    elif period == 'last_6_months':
        start_date = (now.replace(day=1) - pd.DateOffset(months=5)).date() 
        end_date = now 
    elif period == 'this_year':
        start_date = now.replace(month=1, day=1)
    elif period == 'all_time':
        if transactions:
            earliest_date = min(t['date'] for t in transactions)
            start_date = earliest_date.replace(day=1)
        else:
            return [] 
    
    if start_date:
        if period != 'last_month':
             end_of_current_month = (date(now.year, now.month, 1) + pd.DateOffset(months=1) - timedelta(days=1)).date()
             end_date = end_of_current_month


        return [
            t for t in transactions 
            if start_date <= t['date'] <= end_date
        ]
    return transactions 


def get_savings_projection_from_model(
    all_user_transactions: List[Dict], 
    current_cumulative_balance: float, 
    projection_months: int = 12
) -> List[Dict[str, Any]]:
    global projection_model 
    
    df = pd.DataFrame(all_user_transactions)
    if df.empty:
        return []

    df['date'] = pd.to_datetime(df['date'])
    df['net_balance'] = df.apply(lambda row: row['amount'] if row['type'] == 'income' else -row['amount'], axis=1)
    
    monthly_data = df.set_index('date').resample('M')['net_balance'].sum().reset_index()
    monthly_data.columns = ['month_end_date', 'monthly_net_balance']

    if len(monthly_data) < 2 or projection_model is None:
        print("Model proyeksi tidak tersedia atau data tidak cukup untuk ML. Menggunakan proyeksi rata-rata sederhana.")
        
        monthly_net_balances_avg_fallback = monthly_data['monthly_net_balance'].mean() if len(monthly_data) > 0 else 0
        
        if monthly_net_balances_avg_fallback == 0 and sum(t['amount'] for t in all_user_transactions if t['type']=='income') > 0:
             income_only_df = df[df['type'] == 'income']
             if not income_only_df.empty:
                 monthly_income_avg_fallback = income_only_df.set_index('date').resample('M')['amount'].sum().mean()
                 monthly_net_balances_avg_fallback = monthly_income_avg_fallback 

        if monthly_net_balances_avg_fallback == 0 and current_cumulative_balance == 0:
             return []


        projected_data = []
        current_projected_balance_fallback = current_cumulative_balance
        today = date.today()

        for i in range(projection_months + 1): 
            future_date_obj = date.today().replace(day=1) + pd.DateOffset(months=i)
            future_date = future_date_obj.date()

            projected_data.append({
                "date": future_date,
                "projected_balance": float(current_projected_balance_fallback) 
            })
            current_projected_balance_fallback += monthly_net_balances_avg_fallback
        return projected_data

    min_year = monthly_data['month_end_date'].dt.year.min()
    min_month = monthly_data['month_end_date'].dt.month.min()
    monthly_data['month_index'] = (
        (monthly_data['month_end_date'].dt.year - min_year) * 12 +
        (monthly_data['month_end_date'].dt.month - min_month)
    )

    last_month_index = monthly_data['month_index'].max()
    future_month_indices = np.array([[last_month_index + i] for i in range(1, projection_months + 1)])
    
    predicted_balances_raw = projection_model.predict(future_month_indices)

    monthly_data['cumulative_balance_at_month_end'] = monthly_data['monthly_net_balance'].cumsum()

    predicted_last_month_balance_model = projection_model.predict(np.array([[last_month_index]]))[0]
    
    offset = current_cumulative_balance - predicted_last_month_balance_model

    projected_data = []
    projected_data.append({
        "date": date.today(), 
        "projected_balance": float(current_cumulative_balance)
    })

    for i in range(projection_months):
        future_date_obj = monthly_data['month_end_date'].max() + pd.DateOffset(months=i+1)
        projected_balance = predicted_balances_raw[i] + offset
        
        projected_data.append({
            "date": future_date_obj.date(), 
            "projected_balance": float(projected_balance)
        })

    return projected_data


def detect_transaction_anomalies_ml(transactions: List[Dict]) -> List[Dict[str, Any]]:
    global anomaly_model 
    
    if anomaly_model is None:
        print("Model deteksi anomali belum dimuat atau ada error. Deteksi anomali tidak tersedia.")
        return []

    if len(transactions) < 2: 
        return []

    df = pd.DataFrame(transactions)
    df['amount_log'] = np.log1p(df['amount'])

    features = ['amount_log']
    df_features = df[features].dropna()

    if df_features.empty:
        print("Tidak ada fitur valid untuk deteksi anomali.")
        return []

    if not hasattr(anomaly_model, '_gamma'): 
        print("WARNING: Model deteksi anomali belum di-fit. Mengembalikan hasil kosong.")
        return []

    df['anomaly_score'] = anomaly_model.decision_function(df_features)
    df['is_anomaly'] = anomaly_model.predict(df_features) 

    anomalies = []
    for index, row in df[df['is_anomaly'] == -1].iterrows():
        original_trans = next((t for t in transactions if t['id'] == row['id']), None)
        if original_trans:
            anomalies.append({
                "id": original_trans['id'],
                "amount": original_trans['amount'],
                "category": original_trans['category'],
                "date": original_trans['date'],
                "description": original_trans['description'],
                "score": float(row['anomaly_score'])
            })
    return anomalies


def get_financial_analysis(
    user_id: int, 
    db: Session, 
    period: str,
    user_risk_profile: str = "medium", 
    user_investment_goal: str = "long_term_growth"
) -> FinancialAnalysisResponse: 
    
    all_user_transactions_db = db.query(models.Transaction, models.Category)\
                                 .join(models.Category, models.Transaction.category_id == models.Category.id)\
                                 .filter(models.Transaction.user_id == user_id)\
                                 .order_by(models.Transaction.transaction_date)\
                                 .all()
    
    all_transactions_mapped = []
    for trans_db, cat_db in all_user_transactions_db:
        all_transactions_mapped.append({
            "id": trans_db.id,
            "type": "income" if trans_db.transaction_type else "expense", 
            "amount": float(trans_db.amount), 
            "date": trans_db.transaction_date, 
            "description": trans_db.description,
            "category": cat_db.name, 
            "category_id": cat_db.id
        })
    
    cumulative_balance = 0
    for trans in all_transactions_mapped:
        cumulative_balance += trans['amount'] if trans['type'] == 'income' else -trans['amount']


    filtered_transactions = filter_transactions_by_period_py(all_transactions_mapped, period)

    income_total_filtered = sum(t['amount'] for t in filtered_transactions if t['type'] == 'income')
    expense_total_filtered = sum(t['amount'] for t in filtered_transactions if t['type'] == 'expense')
    net_balance_filtered = income_total_filtered - expense_total_filtered
    savings_rate_filtered = (net_balance_filtered / income_total_filtered * 100) if income_total_filtered > 0 else 0

    category_expenses_filtered = collections.defaultdict(float)
    for t in filtered_transactions:
        if t['type'] == 'expense':
            category_expenses_filtered[t['category']] += t['amount']

    average_monthly_expense = get_monthly_expense_average(all_transactions_mapped)
    emergency_fund_ratio = cumulative_balance / average_monthly_expense if average_monthly_expense > 0 else 0

    insights_list = [] 
    
    # A. Saran Pengeluaran Terbesar
    sorted_categories = sorted(category_expenses_filtered.items(), key=lambda item: item[1], reverse=True)
    if sorted_categories and expense_total_filtered > 0:
        top_category, top_amount = sorted_categories[0]
        percentage_of_total_expense = (top_amount / expense_total_filtered * 100)
        if percentage_of_total_expense >= 25 and top_category not in ['Gaji', 'Investasi']:
            insights_list.append(Insight(
                title=f"Fokus pada Pengeluaran {top_category}",
                text=f"Anda menghabiskan **{percentage_of_total_expense:.0f}%** dari total pengeluaran Anda untuk **{top_category}** ({top_amount:,.0f}). Pertimbangkan cara untuk menguranginya.",
                action="Tips Hemat Kategori"
            ))

    # B. Anomali Pengeluaran Tinggi (menggunakan model Isolation Forest)
    anomalous_transactions = detect_transaction_anomalies_ml(filtered_transactions) 
    for anomaly in anomalous_transactions:
        insights_list.append(Insight(
            title=f"Perhatian: Pengeluaran Besar Tidak Biasa ({anomaly['category']})",
            text=f"Kami mendeteksi pengeluaran tidak biasa sebesar **{anomaly['amount']:,.0f}** untuk **{anomaly['category']}** pada {anomaly['date'].strftime('%d-%m-%Y')}. Ini mungkin anomali.",
            action="Cek Detail Transaksi"
        ))

    # C. Saran Kondisi Keuangan Umum (Defisit/Surplus)
    if net_balance_filtered < 0:
        insights_list.append(Insight(
            title="Perhatian: Pengeluaran Melebihi Pemasukan",
            text=f"Total pengeluaran Anda ({expense_total_filtered:,.0f}) melebihi total pendapatan Anda ({income_total_filtered:,.0f}), menghasilkan defisit **{abs(net_balance_filtered):,.0f}**. Penting untuk segera meninjau dan mengurangi pengeluaran Anda.",
            action="Rencanakan Anggaran"
        ))
    elif savings_rate_filtered < 10 and income_total_filtered > 0:
         insights_list.append(Insight(
            title="Tingkatkan Rasio Tabungan Anda",
            text=f"Rasio tabungan Anda ({savings_rate_filtered:.1f}%) masih di bawah rekomendasi 10-20%. Coba identifikasi area pengeluaran yang bisa dikurangi.",
            action="Strategi Peningkatan Tabungan"
        ))
    elif net_balance_filtered > 0 and income_total_filtered > 0 and 10 <= savings_rate_filtered <= 20:
        insights_list.append(Insight(
            title="Kinerja Tabungan Baik",
            text=f"Selamat! Rasio tabungan Anda ({savings_rate_filtered:.1f}%) sudah baik. Terus pertahankan atau tingkatkan sedikit lagi.",
            action="Langkah Selanjutnya Tabungan"
        ))
    elif savings_rate_filtered > 20:
        insights_list.append(Insight(
            title="Tabungan Sangat Baik!",
            text=f"Luar biasa! Rasio tabungan Anda ({savings_rate_filtered:.1f}%) sangat baik. Anda berada di jalur yang tepat.",
            action="Opsi Investasi Lanjutan"
        ))
    
    # D. Saran untuk pengeluaran diskresioner tinggi
    discretionary_categories = ['Hiburan', 'Belanja', 'Lain-lain']
    discretionary_expense = sum(category_expenses_filtered.get(cat, 0) for cat in discretionary_categories)
    if discretionary_expense > (income_total_filtered * 0.20) and income_total_filtered > 0:
        insights_list.append(Insight(
            title="Tinjau Pengeluaran Diskresioner",
            text=f"Pengeluaran Anda untuk hiburan, belanja, dan kategori 'lain-lain' mencapai **{discretionary_expense:,.0f}** ({discretionary_expense / income_total_filtered * 100:.0f}% dari pendapatan). Mengurangi ini dapat signifikan meningkatkan tabungan.",
            action="Atur Batas Belanja"
        ))

    # E. Rekomendasi Investasi Berbasis Profil Risiko & Tujuan
    if emergency_fund_ratio >= 3 and cumulative_balance > 0 and income_total_filtered > 0:
        investment_rec = ""
        investment_action = "Pelajari Investasi"
        
        if user_risk_profile == 'low':
            if user_investment_goal in ['emergency', 'none', 'down_payment']:
                investment_rec = f"Dengan profil risiko **Rendah** dan tujuan **{user_investment_goal}**, pertimbangkan investasi jangka pendek seperti **Reksa Dana Pasar Uang** atau **Obligasi Pemerintah**."
                investment_action = 'Cari Investasi Stabil'
            else:
                investment_rec = f"Profil risiko **Rendah** cocok untuk stabilitas. Untuk tujuan **{user_investment_goal}**, Anda bisa melihat **Obligasi Pemerintah** atau **Reksa Dana Pendapatan Tetap**."
                investment_action = 'Jelajahi Investasi Aman'
        elif user_risk_profile == 'medium':
            if user_investment_goal in ['education', 'retirement']:
                investment_rec = f"Profil risiko **Sedang** cocok untuk pertumbuhan moderat. Untuk tujuan **{user_investment_goal}**, pertimbangkan **Reksa Dana Campuran** atau **Saham Blue Chip**."
                investment_action = 'Jelajahi Investasi Moderat'
            else:
                investment_rec = f"Dengan profil risiko **Sedang**, cari keseimbangan. **Reksa Dana Campuran** adalah pilihan yang baik."
                investment_action = 'Jelajahi Reksa Dana Campuran'
        elif user_risk_profile == 'high':
            if user_investment_goal in ['long_term_growth', 'retirement']:
                investment_rec = f"Profil risiko **Tinggi** dan tujuan **{user_investment_goal}** memungkinkan pertumbuhan agresif. Pertimbangkan **Reksa Dana Saham** atau **Saham Sektor Teknologi/Inovatif**."
                investment_action = 'Jelajahi Investasi Agresif'
            else:
                investment_rec = f"Dengan profil risiko **Tinggi**, Anda memiliki potensi pertumbuhan besar. Jelajahi **Reksa Dana Saham** atau **Investasi Properti** untuk tujuan jangka panjang."
                investment_action = 'Jelajahi Investasi Berisiko Tinggi'
        
        if investment_rec:
            insights_list.append(Insight( 
                title="Rekomendasi Investasi Personal 🎯",
                text=investment_rec,
                action=investment_action
            ))
    elif cumulative_balance > 0 and emergency_fund_ratio < 3:
        insights_list.append(Insight( 
            title="Prioritaskan Dana Darurat Anda!",
            text=f"Saldo Anda **{cumulative_balance:,.0f}** tapi rasio dana darurat Anda hanya sekitar **{emergency_fund_ratio:.1f} bulan**. Kami sangat menyarankan untuk fokus membangun dana darurat setidaknya 3-6 bulan pengeluaran sebelum berinvestasi.",
            action="Hitung Kebutuhan Dana Darurat"
        ))

    # 5. Generate Kesimpulan Umum
    conclusion_text_content = "" 

    if len(all_user_transactions_db) == 0: 
        conclusion_text_content = 'Anda belum mencatat transaksi apapun. Mulailah mencatat untuk mendapatkan analisa keuangan yang komprehensif!'
    elif net_balance_filtered > (income_total_filtered * 0.20):
        conclusion_text_content = f"Selamat! Anda berhasil mengelola keuangan dengan sangat baik, dengan surplus sebesar **{net_balance_filtered:,.0f}**. Terus pertahankan kebiasaan baik ini dan manfaatkan dana surplus untuk mencapai tujuan finansial jangka panjang."
    elif net_balance_filtered > 0 and net_balance_filtered <= (income_total_filtered * 0.20):
        conclusion_text_content = f"Kondisi keuangan Anda positif dengan surplus **{net_balance_filtered:,.0f}**. Ini adalah awal yang baik! Pertimbangkan untuk mengidentifikasi area kecil di mana Anda bisa berhemat lebih banyak."
    elif net_balance_filtered < 0:
        conclusion_text_content = f"Perlu perhatian lebih! Keuangan Anda menunjukkan defisit sebesar **{abs(net_balance_filtered):,.0f}** untuk periode ini. Sangat disarankan untuk meninjau kembali pengeluaran Anda."
    else:
        conclusion_text_content = 'Secara keseluruhan, kondisi keuangan Anda cukup stabil. Fokus pada pengeluaran diskresioner dapat memberikan dampak signifikan pada tabungan Anda.'
    
    if len(all_user_transactions_db) > 0 and net_balance_filtered < (income_total_filtered * 0.10) and net_balance_filtered >= 0:
        conclusion_text_content += "\n\nKami menyarankan untuk menetapkan target bulanan untuk kategori pengeluaran tertentu agar lebih efisien."

    # 6. Format Output ke Pydantic Response Model
    projected_savings_data = get_savings_projection_from_model(
        all_transactions_mapped, 
        cumulative_balance 
    )

    return FinancialAnalysisResponse(
        summary_metrics=SummaryMetrics(
            income_total_filtered=income_total_filtered,
            expense_total_filtered=expense_total_filtered,
            net_balance_filtered=net_balance_filtered,
            cumulative_balance=cumulative_balance,
            average_monthly_expense=average_monthly_expense,
            emergency_fund_ratio=emergency_fund_ratio,
            savings_rate_filtered=savings_rate_filtered
        ),
        insights=insights_list,
        conclusion=Conclusion(text=conclusion_text_content),
        projection_data=projected_savings_data 
    )