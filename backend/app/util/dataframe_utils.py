import pandas as pd

def prepare_dataframe(transactions):
    data = []
    for t in transactions:
        category_name = None
        # pastikan category berupa string nama, bukan objek
        if hasattr(t, 'category'):
            # cek apakah category objek dan punya atribut 'name'
            if hasattr(t.category, 'name'):
                category_name = t.category.name
            else:
                category_name = t.category
        else:
            category_name = '__unknown__'

        data.append({
            "amount": float(t.amount),
            "type": bool(t.transaction_type),
            "transaction_date": t.transaction_date,  # Ganti key jadi 'transaction_date'
            "category": category_name if category_name else '__unknown__'
        })

    df = pd.DataFrame(data)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")  # Update kolom yang diparse
    df = df.dropna(subset=["transaction_date"])
    df["net_amount"] = df.apply(lambda row: row["amount"] if row["type"] else -row["amount"], axis=1)
    df.sort_values("transaction_date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
