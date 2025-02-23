import streamlit as st
import pandas as pd
import os
import base64
import webbrowser
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select, insert

# ---------------------------
# Debugging-Hilfe: Überprüfe das Verzeichnis und die Dateien darin
st.write("Verzeichnisinhalt:", os.listdir("data"))

# ---------------------------
# Datenbank-Verbindung und Tabellen-Definition
# ---------------------------
# Verbindet sich mit der Datenbank (oder erstellt sie, wenn sie nicht existiert)
db_path = "data/bestellungen.db"
engine = create_engine(f"sqlite:///{db_path}")

# Datenbankstruktur definieren
meta = MetaData()

orders_table = Table(
    'bestellungen', meta,
    Column('id', Integer, primary_key=True),
    Column('Datum', String),
    Column('Storenummer', String),
    Column('Produktname', String),
    Column('SAP_Nummer', String),
    Column('Anzahl', Integer)
)

# Tabelle erstellen (nur einmalig nötig)
meta.create_all(engine)

# ---------------------------
# Funktion zum Laden von Daten mit Fehlerbehandlung
# ---------------------------
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        st.success(f"Datei erfolgreich geladen: {file_path}")
        return df
    except FileNotFoundError:
        st.error(f"Datei nicht gefunden: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Fehler beim Laden der Datei: {file_path}")
        st.error(str(e))
        return pd.DataFrame()

# ---------------------------
# Excel-Dateipfade und Überprüfung
# ---------------------------
storelist_path = "data/storelist_new.xlsx"
products_path = "data/produkte.xlsx"
special_products_path = "data/produkte_special.xlsx"

# Überprüfe, ob die Dateien im Verzeichnis vorhanden sind
st.write("Prüfe Pfad:", storelist_path)
st.write("Dateien im Verzeichnis:", os.listdir("data"))

# ---------------------------
# Lade die Daten
# ---------------------------
storelist = load_data(storelist_path)
products = load_data(products_path)
special_products = load_data(special_products_path)

# Überprüfe, ob DataFrames geladen wurden
if storelist.empty:
    st.warning("Storelist konnte nicht geladen werden.")
if products.empty:
    st.warning("Produkte konnten nicht geladen werden.")
if special_products.empty:
    st.warning("Spezialprodukte konnten nicht geladen werden.")

# Erstelle Mappings für Store-Auswahl:
store_mapping = dict(zip(storelist["Storenummer"], storelist["Storename"]))

# ---------------------------
# Sidebar: Store-Auswahl
# ---------------------------
st.sidebar.title("Store Auswahl")
selected_store_number = st.sidebar.selectbox(
    "Wähle deine Store-Nummer:",
    options=list(store_mapping.keys()),
    format_func=lambda x: f"{x} - {store_mapping[x]}",
    key="selected_store_number"
)

# ---------------------------
# Funktion: Bestellung speichern
# ---------------------------
def save_order(store_number, sap_number, product_name, quantity):
    with engine.connect() as conn:
        stmt = insert(orders_table).values(
            Datum=datetime.now().strftime("%Y-%m-%d"),
            Storenummer=store_number,
            Produktname=product_name,
            SAP_Nummer=sap_number,
            Anzahl=quantity
        )
        conn.execute(stmt)
        conn.commit()
    st.success("Bestellung wurde in der Datenbank gespeichert!")

# ---------------------------
# Funktion: Alle Bestellungen anzeigen
# ---------------------------
def get_orders():
    with engine.connect() as conn:
        stmt = select([orders_table])
        result = conn.execute(stmt)
        orders = result.fetchall()
    return orders

# ---------------------------
# Funktion: Bestellungen als DataFrame herunterladen
# ---------------------------
def download_orders():
    df = pd.read_sql_table('bestellungen', engine)
    return df

# ---------------------------
# Produkte anzeigen und Bestellungen aufnehmen
# ---------------------------
def display_products(product_data):
    cols = st.columns(3)
    for index, row in product_data.iterrows():
        col = cols[index % 3]
        with col:
            st.markdown(f"### {row['Name']}")
            st.write(f"**SAP Nummer:** {row['SAP Number']}")
            st.write(f"**Stock:** {row['actual Stock']}")

            qty_options = [qty for qty in [row.get("Qty 1"), row.get("Qty 2"), row.get("Qty 3")] if not pd.isna(qty)]

            if qty_options:
                qty_selected = st.selectbox(
                    "Bestellmenge",
                    options=qty_options,
                    key=f"qty_{index}",
                    disabled=(row['actual Stock'] == 0)
                )

                if st.button(f"Bestellen: {row['Name']}", key=f"save_{index}", disabled=(row['actual Stock'] == 0)):
                    save_order(selected_store_number, row["SAP Number"], row["Name"], qty_selected)
                    st.session_state[f"order_saved_{index}"] = True
                    st.rerun()

# ---------------------------
# Navigation und Seiteninhalt
# ---------------------------
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio("Seiten", ["Produkte", "Spezialprodukte", "Bestellungen"])

if selected_tab == "Produkte":
    st.header("Produkte")
    display_products(products)
elif selected_tab == "Spezialprodukte":
    st.header("Spezialprodukte")
    display_products(special_products)
elif selected_tab == "Bestellungen":
    st.header("Alle Bestellungen")
    orders = get_orders()
    orders_df = pd.DataFrame(orders, columns=['ID', 'Datum', 'Storenummer', 'Produktname', 'SAP Nummer', 'Anzahl'])
    st.dataframe(orders_df)

    st.subheader("Bestellungen herunterladen")
    orders_df = download_orders()

    # Download als Excel
    st.download_button(
        label="Bestellungen als Excel herunterladen",
        data=orders_df.to_excel(index=False),
        file_name="bestellungen.xlsx"
    )

    # Download als CSV
    st.download_button(
        label="Bestellungen als CSV herunterladen",
        data=orders_df.to_csv(index=False),
        file_name="bestellungen.csv"
    )
