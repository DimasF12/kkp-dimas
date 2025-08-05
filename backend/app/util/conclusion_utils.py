from backend.app.model.analysis_model import Conclusion

def generate_conclusion(balance, savings_rate, emergency_fund_ratio):
    if balance > 0 and savings_rate >= 0.2 and emergency_fund_ratio >= 3:
        return Conclusion(
            text="Keuanganmu sangat sehat!",
            reason=(
                f"Kamu memiliki saldo akhir Rp{balance:,.0f}, rasio tabungan {savings_rate * 100:.1f}%, "
                f"dana darurat cukup untuk {emergency_fund_ratio:.1f} bulan. Pertahankan kondisi ini!"
            )
        )
    elif balance < 0:
        return Conclusion(
            text="Keuanganmu defisit.",
            reason="Pengeluaran melebihi pemasukan. Segera evaluasi kondisi keuanganmu."
        )
    elif savings_rate < 0.1:
        return Conclusion(
            text="Tingkat tabungan rendah.",
            reason=f"Hanya {savings_rate * 100:.1f}% dari pemasukan ditabung. Usahakan minimal 10%."
        )
    elif emergency_fund_ratio < 1:
        return Conclusion(
            text="Dana darurat tidak mencukupi.",
            reason=f"Dana darurat hanya mencukupi {emergency_fund_ratio:.1f} bulan. Idealnya minimal 3 bulan."
        )
    else:
        return Conclusion(
            text="Keuangan cukup stabil.",
            reason="Kondisi keuangan kamu baik, tapi masih bisa ditingkatkan."
        )
