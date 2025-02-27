import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select, insert

# ---------------------------
# Mehrsprachigkeit: Sprachoptionen und Übersetzungen definieren
# ---------------------------
LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
    "it": "Italiano"
}

TRANSLATIONS = {
    "title": {
        "de": "Interner Store Shop",
        "en": "Internal Store Shop",
        "fr": "Boutique interne",
        "it": "Negozio interno"
    },
    "select_store": {
        "de": "Wähle deine Store-Nummer:",
        "en": "Select your store number:",
        "fr": "Sélectionnez votre numéro de magasin:",
        "it": "Seleziona il numero del tuo negozio:"
    },
    "current_store": {
        "de": "Aktueller Store",
        "en": "Current store",
        "fr": "Magasin actuel",
        "it": "Negozio attuale"
    },
    "products": {
        "de": "Merchandise Produkte",
        "en": "Merchandise Products",
        "fr": "Produits de merchandise",
        "it": "Prodotti Merchandise"
    },
    "special_products": {
        "de": "Spezialprodukte",
        "en": "Special Products",
        "fr": "Produits spéciaux",
        "it": "Prodotti speciali"
    },
    "order": {
        "de": "Bestellung",
        "en": "Order",
        "fr": "Commande",
        "it": "Ordine"
    },
    "order_success": {
        "de": "Bestellung wurde erfolgreich gespeichert!",
        "en": "Order successfully saved!",
        "fr": "Commande enregistrée avec succès!",
        "it": "Ordine salvato con successo!"
    },
    "not_available": {
        "de": "Nicht verfügbar",
        "en": "Not available",
        "fr": "Non disponible",
        "it": "Non disponibile"
    }
}

# Funktion für mehrsprachige Texte
def _(key):
    return TRANSLATIONS[key][st.session_state.language]

# ---------------------------
# Streamlit-Konfiguration
# ---------------------------
st.set_page_config(page_title="Interner Store Shop", layout="wide")

# ---------------------------
# Datenbank-Verbindung und Tabellen-Definition
# ---------------------------
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
# Funktion zum Laden von Daten
# ---------------------------
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Datei nicht gefunden: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Fehler beim Laden der Datei: {file_path}")
        st.error(str(e))
        return pd.DataFrame()

# ---------------------------
# Excel-Dateipfade und Static-Folder
# ---------------------------
storelist_path = "data/storelist_new.xlsx"
products_path = "data/produkte.xlsx"
special_products_path = "data/produkte_special.xlsx"
static_folder = "static"

# ---------------------------
# Lade die Daten
# ---------------------------
storelist = load_data(storelist_path)
products = load_data(products_path)
special_products = load_data(special_products_path)

# Erstelle Mappings:
store_mapping = dict(zip(storelist["Storenummer"], storelist["Storename"]))
store_lang_mapping = dict(zip(storelist["Storenummer"], storelist["Lang"]))

# ---------------------------
# Sidebar: Navigation und Store-Auswahl
# ---------------------------
st.sidebar.title("Navigation")

def update_language():
    selected_store = st.session_state.selected_store_number
    store_default = store_lang_mapping[selected_store]
    if store_default == "D":
        st.session_state.language = "de"
    elif store_default == "F":
        st.session_state.language = "fr"
    else:
        st.session_state.language = "en"

selected_store_number = st.sidebar.selectbox(
    TRANSLATIONS["select_store"]["de"],
    options=list(store_mapping.keys()),
    format_func=lambda x: f"{x} - {store_mapping[x]}",
    key="selected_store_number",
    on_change=update_language
)

if "language" not in st.session_state:
    update_language()

selected_language = st.sidebar.selectbox(
    "Sprache / Language",
    options=list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state.language),
    format_func=lambda x: LANGUAGES[x]
)
st.session_state.language = selected_language

selected_store_name = store_mapping[selected_store_number]
st.sidebar.write(f"{_('current_store')}: {selected_store_name} ({selected_store_number})")

selected_tab = st.sidebar.radio("Seiten", [_("products"), _("special_products")])

# ---------------------------
# CSS-Stil für die Bilder
# ---------------------------
image_width = "150px"
image_height = "150px"

st.markdown(f"""
    <style>
        .product-container {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .product-container img {{
            width: {image_width};
            height: {image_height};
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
        }}
        .not-available-text {{
            color: red;
        }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Funktion: Bild als Base64 kodieren
# ---------------------------
@st.cache_data
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ---------------------------
# Funktion: Produkte anzeigen
# ---------------------------
def display_products(product_data, email_mode=False):
    cols = st.columns(3)
    
    for index, row in product_data.iterrows():
        col = cols[index % 3]
        with col:
            st.markdown("<div class='product-container'>", unsafe_allow_html=True)
            st.markdown(f"<h5>{row['Name']}</h5>", unsafe_allow_html=True)

            if not pd.isna(row.get("Bemerkungen", "")) and str(row["Bemerkungen"]).strip():
                st.markdown(f"<p style='font-size: small; color: gray;'>{row['Bemerkungen']}</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size: small;'>&nbsp;</p>", unsafe_allow_html=True)

            image_name = str(row["Bildname"])
            image_path = os.path.join(static_folder, image_name)
            if os.path.exists(image_path):
                image_base64 = get_image_base64(image_path)
                st.markdown(f"""
                    <div>
                        <img src="data:image/png;base64,{image_base64}" 
                             alt="{row['Name']}" 
                             style="width: {image_width}; height: {image_height}; object-fit: cover;">
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"Bild nicht gefunden: {image_name}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #ddd; margin: 20px 0;'>", unsafe_allow_html=True)

# ---------------------------
# Seiteninhalt anzeigen
# ---------------------------
if selected_tab == _("products"):
    st.header(_("products"))
    display_products(products)
elif selected_tab == _("special_products"):
    st.header(_("special_products"))
    display_products(special_products, email_mode=True)
else:
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





