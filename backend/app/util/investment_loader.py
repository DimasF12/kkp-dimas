import pandas as pd
import os

def load_investment_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "../data/investment_data.csv")

        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        raise FileNotFoundError("File investment_data.csv tidak ditemukan.")
    except Exception as e:
        raise Exception(f"Gagal memuat data investasi: {e}")
