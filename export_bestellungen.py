import pandas as pd
from sqlalchemy import create_engine

# Verbindet sich mit der SQLite-Datenbank
db_path = "data/bestellungen.db"
engine = create_engine(f"sqlite:///{db_path}")

# ---------------------------
# Funktion: Daten aus der Tabelle "bestellungen" laden
# ---------------------------
def load_orders():
    query = "SELECT * FROM bestellungen"
    df = pd.read_sql_query(query, engine)
    return df

# ---------------------------
# Funktion: Export als Excel und CSV
# ---------------------------
def export_orders():
    orders_df = load_orders()

    if orders_df.empty:
        print("Keine Bestellungen in der Datenbank.")
    else:
        # Export als Excel
        excel_file = "export_bestellungen.xlsx"
        orders_df.to_excel(excel_file, index=False)
        print(f"Excel-Datei gespeichert: {excel_file}")

        # Export als CSV
        csv_file = "export_bestellungen.csv"
        orders_df.to_csv(csv_file, index=False)
        print(f"CSV-Datei gespeichert: {csv_file}")

# ---------------------------
# Skript ausführen
# ---------------------------
if __name__ == "__main__":
    export_orders()
