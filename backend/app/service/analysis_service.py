from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.model.analysis_model import (
    FinancialAnalysisResponse, Insight, SummaryMetrics, Conclusion, ProjectionPoint
)
from backend.app.database.models import Transaction
from backend.app.util.period_utils import get_period_range
from backend.app.util.dataframe_utils import prepare_dataframe
from backend.app.util.metrics_utils import calculate_summary_metrics
from backend.app.util.projection_utils import predict_future_balance, prepare_cumulative_balance_df
from backend.app.util.conclusion_utils import generate_conclusion
from backend.app.service.ml_service import detect_anomalies

def simple_investment_recommendation(savings_rate_percent: float) -> str:
    if savings_rate_percent < 10:
        return "Kami sarankan memulai investasi dengan produk risiko rendah seperti Reksa Dana Pasar Uang."
    elif 10 <= savings_rate_percent < 20:
        return "Rekomendasi investasi Anda adalah Reksa Dana Campuran dengan risiko sedang."
    else:
        return "Anda cocok untuk investasi dengan risiko lebih tinggi seperti Reksa Dana Saham atau Saham langsung."

def generate_financial_analysis(user_id: int, db: Session, period: str = "all_time") -> FinancialAnalysisResponse:
    now = datetime.now()
    start_date, end_date = get_period_range(period, now)

    # 🔍 Ambil dan filter transaksi sesuai periode
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if period != "all_time":
        query = query.filter(Transaction.transaction_date <= end_date)

    transactions = query.all()
    if not transactions:
        return FinancialAnalysisResponse(
            total_income=0,
            total_expense=0,
            balance=0,
            insights=[],
            summary_metrics=SummaryMetrics(
                income_total_filtered=0,
                expense_total_filtered=0,
                net_balance_filtered=0,
                cumulative_balance=0,
                average_monthly_expense=0,
                emergency_fund_ratio=0,
                savings_rate_filtered=0
            ),
            conclusion=Conclusion(
                text="Tidak ada data",
                reason="Tidak ditemukan transaksi pada periode yang dipilih."
            ),
            projection_data=[]
        )

    # 📊 Siapkan DataFrame dari transaksi
    df = prepare_dataframe(transactions)

    # 💸 Hitung income/expense/balance dari data terfilter
    income_total = df[df["type"] == True]["amount"].sum()
    expense_total = df[df["type"] == False]["amount"].sum()
    balance = income_total - expense_total
    cumulative_balance = df["net_amount"].sum()

    # 📈 Metode analisis rasio
    avg_monthly_expense, emergency_fund_ratio, savings_rate = calculate_summary_metrics(
        df, income_total, expense_total, balance
    )

    # 🔍 Deteksi anomali
    anomalies_flags = detect_anomalies(transactions)
    anomalous_transactions = [txn for txn, flag in zip(transactions, anomalies_flags) if flag]
    num_anomalies = len(anomalous_transactions)

    if num_anomalies > 0:
        description = (
            f"Kami menemukan {num_anomalies} transaksi yang berbeda dari pola biasanya. "
            "Silakan periksa detail transaksi berikut untuk memastikan semuanya benar dan aman:\n"
            + "\n".join([
                f"- {txn.description or 'Transaksi tanpa deskripsi'} pada {txn.transaction_date.strftime('%d %b %Y')} sebesar Rp{txn.amount:,.0f}"
                for txn in anomalous_transactions
            ])
            + "\nJika ada yang tidak kamu kenali, segera tindak lanjuti untuk menjaga keamanan keuanganmu."
        )
        title = "Perhatian: Transaksi Tidak Biasa Ditemukan"
    else:
        title = "Semua Transaksi Normal"
        description = "Tidak ditemukan transaksi yang mencurigakan. Keuangan kamu aman dan terkendali."

    insights = [Insight(title=title, description=description)]

    # 💡 Insight rekomendasi investasi
    recommendation_text = simple_investment_recommendation(savings_rate * 100)
    insights.append(Insight(title="Rekomendasi Investasi", description=recommendation_text))

    # 🧮 Siapkan saldo kumulatif untuk prediksi saldo ke depan
    balance_df = prepare_cumulative_balance_df(df)

    # 📊 Prediksi saldo masa depan berdasarkan periode terfilter
    projection_data_dicts = predict_future_balance(balance_df)

    projection_data = [ProjectionPoint(**item) for item in projection_data_dicts]

    # 🧠 Buat kesimpulan akhir
    conclusion = generate_conclusion(balance, savings_rate, emergency_fund_ratio)

    return FinancialAnalysisResponse(
        total_income=income_total,
        total_expense=expense_total,
        balance=balance,
        insights=insights,
        summary_metrics=SummaryMetrics(
            income_total_filtered=income_total,
            expense_total_filtered=expense_total,
            net_balance_filtered=balance,
            cumulative_balance=cumulative_balance,
            average_monthly_expense=avg_monthly_expense,
            emergency_fund_ratio=emergency_fund_ratio,
            savings_rate_filtered=savings_rate
        ),
        conclusion=conclusion,
        projection_data=projection_data
    )







# from datetime import datetime, timedelta, date
# from sqlalchemy.orm import Session
# from backend.app.model.analysis_model import (
#     FinancialAnalysisResponse, Insight, SummaryMetrics,
#     Conclusion, ProjectionPoint
# )
# from backend.app.database.models import Transaction
# from backend.app.service.ml_service import analyze_finance


# def generate_financial_analysis(user_id: int, db: Session, period: str = "all_time") -> FinancialAnalysisResponse:
#     end_date = datetime.now()
#     start_date = None

#     if period == "last_month":
#         first_of_this_month = end_date.replace(day=1)
#         last_month_end = first_of_this_month - timedelta(days=1)
#         start_date = last_month_end.replace(day=1)
#         end_date = last_month_end

#     elif period == "last_3_months":
#         start_date = end_date - timedelta(days=90)

#     elif period == "last_6_months":
#         start_date = end_date - timedelta(days=180)

#     elif period == "this_year":
#         start_date = end_date.replace(month=1, day=1)

#     # If period is "all_time" or unknown, no date filter applied (start_date stays None)

#     query = db.query(Transaction).filter(Transaction.user_id == user_id)
#     if start_date:
#         query = query.filter(Transaction.transaction_date >= start_date)
#     if period != "all_time":
#         query = query.filter(Transaction.transaction_date <= end_date)

#     transactions = query.all()

#     income_total = sum(t.amount for t in transactions if t.transaction_type is True)
#     expense_total = sum(t.amount for t in transactions if t.transaction_type is False)
#     balance = income_total - expense_total
#     cumulative_balance = sum(t.amount if t.transaction_type else -t.amount for t in transactions)

#     unique_months = set((t.transaction_date.year, t.transaction_date.month) for t in transactions)
#     avg_month_count = max(1, len(unique_months))
#     average_monthly_expense = expense_total / avg_month_count

#     emergency_fund_ratio = balance / max(1, average_monthly_expense)
#     savings_rate = (income_total - expense_total) / income_total if income_total > 0 else 0

#     # 📌 Generate conclusion + reason
#     if balance > 0 and savings_rate >= 0.2 and emergency_fund_ratio >= 3:
#         conclusion_text = "Keuanganmu sangat sehat!"
#         reason_text = (
#             f"Kamu memiliki saldo akhir sebesar Rp{balance:,.0f}, "
#             f"rasio tabungan sebesar {savings_rate * 100:.1f}% "
#             f"dan dana darurat yang cukup untuk {emergency_fund_ratio:.1f} bulan pengeluaran. "
#             f"Kondisi ini menunjukkan keuangan yang stabil dan ideal. Pertahankan!"
#         )

#     elif balance < 0:
#         conclusion_text = "Keuanganmu dalam kondisi defisit!"
#         reason_text = (
#             f"Saldo kamu negatif (Rp{balance:,.0f}). Artinya pengeluaranmu melebihi pemasukan. "
#             f"Segera evaluasi pengeluaran dan cari peluang menambah pemasukan."
#         )

#     elif savings_rate < 0.1:
#         conclusion_text = "Tingkat tabunganmu sangat rendah."
#         reason_text = (
#             f"Rasio tabunganmu hanya {savings_rate * 100:.1f}%. Idealnya minimal 10% dari pemasukan "
#             f"disisihkan untuk ditabung. Mulailah alokasikan dana untuk tabungan rutin."
#         )

#     elif emergency_fund_ratio < 1:
#         conclusion_text = "Dana daruratmu sangat kurang!"
#         reason_text = (
#             f"Dana daruratmu hanya mencukupi {emergency_fund_ratio:.1f} bulan pengeluaran. "
#             f"Rekomendasi umum adalah minimal 3 bulan. Sisihkan sebagian dari saldo (Rp{balance:,.0f}) "
#             f"untuk membangun dana darurat."
#         )

#     else:
#         conclusion_text = "Kondisi keuanganmu cukup baik, tapi masih bisa ditingkatkan."
#         reason_text = (
#             f"Saat ini kamu memiliki saldo akhir Rp{balance:,.0f}, "
#             f"rasio tabungan {savings_rate * 100:.1f}%, dan dana darurat {emergency_fund_ratio:.1f} bulan. "
#             f"Pertahankan kebiasaan baik dan tingkatkan aspek yang masih di bawah ideal."
#         )

#     # 🔮 Projection Data (3 bulan ke depan)
#     projection_data = [
#         ProjectionPoint(
#             date=(date.today().replace(day=1) + timedelta(days=30 * i)),
#             projected_balance=balance + i * (income_total - expense_total)
#         )
#         for i in range(1, 4)
#     ]

#     return FinancialAnalysisResponse(
#         total_income=income_total,
#         total_expense=expense_total,
#         balance=balance,
#         insights=[
#             Insight(title="Kontrol Pengeluaran", description="Perhatikan pengeluaranmu di kategori besar."),
#             Insight(title="Tabungan", description="Usahakan menyisihkan tabungan secara konsisten tiap bulan."),
#         ],
#         summary_metrics=SummaryMetrics(
#             income_total_filtered=income_total,
#             expense_total_filtered=expense_total,
#             net_balance_filtered=balance,
#             cumulative_balance=cumulative_balance,
#             average_monthly_expense=average_monthly_expense,
#             emergency_fund_ratio=emergency_fund_ratio,
#             savings_rate_filtered=savings_rate
#         ),
#         conclusion=Conclusion(
#             text=conclusion_text,
#             reason=reason_text
#         ),
#         projection_data=projection_data
#     )
