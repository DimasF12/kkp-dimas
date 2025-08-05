import math
from backend.app.util.investment_loader import load_investment_data

def calculate_future_value(initial_amount, monthly_investment, annual_return_rate, years):
    """
    Menghitung nilai akhir investasi dengan setoran bulanan dan bunga majemuk.
    """
    try:
        current_amount = initial_amount
        monthly_return_rate = annual_return_rate / 12 / 100
        total_months = years * 12

        for _ in range(total_months):
            current_amount += monthly_investment
            current_amount *= (1 + monthly_return_rate)

        return math.ceil(current_amount)
    except Exception as e:
        raise ValueError(f"Error calculating future value: {e}")

def calculate_required_monthly_investment(initial_amount, target_amount, annual_return_rate, years):
    """
    Menghitung investasi bulanan yang dibutuhkan untuk mencapai target.
    """
    try:
        monthly_return_rate = annual_return_rate / 12 / 100
        total_months = years * 12

        fv_without_investment = initial_amount * (1 + monthly_return_rate) ** total_months
        future_value_needed = target_amount - fv_without_investment

        if future_value_needed <= 0:
            return 0

        required_monthly_investment = future_value_needed * monthly_return_rate / ((1 + monthly_return_rate) ** total_months - 1)
        return math.ceil(required_monthly_investment)
    except Exception as e:
        raise ValueError(f"Error calculating required monthly investment: {e}")

def calculate_required_duration(initial_amount, monthly_investment, annual_return_rate, target_amount):
    """
    Menghitung berapa tahun yang dibutuhkan untuk mencapai target investasi.
    """
    try:
        current_amount = initial_amount
        monthly_return_rate = annual_return_rate / 12 / 100
        months = 0

        while current_amount < target_amount:
            current_amount += monthly_investment
            current_amount *= (1 + monthly_return_rate)
            months += 1

        return math.ceil(months / 12)
    except Exception as e:
        raise ValueError(f"Error calculating required duration: {e}")

def recommend_investments(current_return_rate):
    """
    Merekomendasikan 3 jenis investasi dengan return lebih tinggi.
    """
    data = load_investment_data()
    recommended = data[data['return_rate'] > current_return_rate] \
                    .sort_values(by='return_rate', ascending=False).head(3)

    return [
        {
            'investment_type': row['investment_type'],
            'return_rate': row['return_rate'],
            'risk_level': row['risk_level']
        }
        for _, row in recommended.iterrows()
    ]

def get_investment_risk_profile(return_investasi: float) -> str:
    if return_investasi > 15:
        resiko = "Tinggi"
        keterangan = "Dengan profil agresif, kamu cocok untuk investasi saham, crypto, atau reksa dana saham jangka panjang."
        return resiko,keterangan
    
    elif 7 <= return_investasi <= 15:
        resiko = "Menengah"
        keterangan = "Sebagai investor moderat, kamu bisa memilih reksa dana campuran, obligasi korporat, atau kombinasi saham dan pendapatan tetap."
        return resiko,keterangan
    
    else:
        resiko = "Rendah"
        keterangan = "Karena kamu termasuk investor konservatif, pilih instrumen seperti deposito, obligasi negara, atau reksa dana pasar uang."
        return resiko,keterangan