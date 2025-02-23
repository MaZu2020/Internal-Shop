from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

# Verbindet sich mit der SQLite-Datenbank (oder erstellt sie, wenn sie nicht existiert)
db_path = "data/bestellungen.db"
engine = create_engine(f"sqlite:///{db_path}")

# Datenbankstruktur definieren
meta = MetaData()

# Tabelle "bestellungen" definieren
orders_table = Table(
    'bestellungen', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('Datum', String),
    Column('Storenummer', String),
    Column('Produktname', String),
    Column('SAP_Nummer', String),
    Column('Anzahl', Integer)
)

# Tabelle erstellen (nur wenn sie nicht existiert)
meta.create_all(engine)

print("Tabelle 'bestellungen' wurde erfolgreich erstellt (falls sie noch nicht existierte).")
