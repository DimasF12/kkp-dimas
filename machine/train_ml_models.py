import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
import pickle
import numpy as np

# Load data dummy csv yang tadi dibuat
df = pd.read_csv("dummy_transactions_v2.csv")

# Convert transaction_date ke datetime
df['transaction_date'] = pd.to_datetime(df['transaction_date'])

# Tipe transaksi bool ke int (True=1 income, False=0 expense)
df['type'] = df['transaction_type'].astype(int)

# --- Encode kategori untuk fitur ML ---
category_encoder = LabelEncoder()
df['category_encoded'] = category_encoder.fit_transform(df['category_id'].astype(str))

# Buat fitur input untuk model
X = df[['amount', 'type', 'category_encoded']]

# Inisiasi model
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)

# Train model
model.fit(X)

with open("anomaly_detection_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("category_encoder.pkl", "wb") as f:
    pickle.dump(category_encoder, f)
