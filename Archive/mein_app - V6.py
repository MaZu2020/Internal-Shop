import streamlit as st
import pandas as pd
import os
import base64
import webbrowser
from order_functions import save_order, send_email_with_outlook

# Mehrsprachigkeit: Sprachoptionen definieren
LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
    "it": "Italiano"
}

TRANSLATIONS = {
    "title": {"de": "Interner Store Shop", "en": "Internal Store Shop", "fr": "Boutique interne", "it": "Negozio interno"},
    "select_store": {"de": "Wähle deine Store-Nummer:", "en": "Select your store number:", "fr": "Sélectionnez votre numéro de magasin:", "it": "Seleziona il numero del tuo negozio:"},
    "current_store": {"de": "Aktueller Store", "en": "Current store", "fr": "Magasin actuel", "it": "Negozio attuale"},
    "products": {"de": "Produkte", "en": "Products", "fr": "Produits", "it": "Prodotti"},
    "special_products": {"de": "Spezialprodukte", "en": "Special Products", "fr": "Produits spéciaux", "it": "Prodotti speciali"},
    "order": {"de": "Bestellung", "en": "Order", "fr": "Commande", "it": "Ordine"},
    "order_success": {"de": "Bestellung wurde erfolgreich gespeichert!", "en": "Order successfully saved!", "fr": "Commande enregistrée avec succès!", "it": "Ordine salvato con successo!"},
    "not_available": {"de": "Nicht verfügbar", "en": "Not available", "fr": "Non disponible", "it": "Non disponibile"}
}

# Initialisierung der Spracheinstellung
if "language" not in st.session_state:
    st.session_state.language = "de"

# Streamlit-Konfiguration muss als erste Anweisung erfolgen
st.set_page_config(page_title="Interner Store Shop", layout="wide")

# Sprachumschaltung
selected_language = st.sidebar.selectbox("Sprache / Language", options=LANGUAGES.keys(), format_func=lambda x: LANGUAGES[x])
st.session_state.language = selected_language

# Funktion für mehrsprachige Texte
def _(key):
    return TRANSLATIONS[key][st.session_state.language]

# CSS-Stil für die Bilder definieren
image_width = "100px"     # Breite des Bildes einstellen
image_height = "100px"    # Höhe des Bildes einstellen

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

# Excel-Dateipfade
storelist_path = r"C:\Users\mzuerche\Desktop\Merch Shop\storelist.xlsx"
products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\produkte.xlsx"
special_products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\produkte special.xlsx"
orders_path = r"C:\Users\mzuerche\Desktop\Merch Shop\bestellungen.xlsx"
static_folder = r"C:\Users\mzuerche\Desktop\Merch Shop\static"

# Funktion zum Laden von Daten
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

storelist = load_data(storelist_path)
products = load_data(products_path)
special_products = load_data(special_products_path)
orders = load_data(orders_path)

st.sidebar.title("Navigation")

selected_store_number = st.sidebar.selectbox(_("select_store"), storelist["Storenummer"])
selected_store_name = storelist.loc[storelist["Storenummer"] == selected_store_number, "Storename"].values[0]
st.sidebar.write(f"{_("current_store")}: {selected_store_name} ({selected_store_number})")

selected_tab = st.sidebar.radio("Seiten", [_("products"), _("special_products")])

# Funktion zur Kodierung eines Bildes als Base64
@st.cache_data
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Funktion zur Produktanzeige als Grid
def display_products(product_data, email_mode=False):
    cols = st.columns(3)  # Grid mit 3 Spalten

    for index, row in product_data.iterrows():
        col = cols[index % 3]  # Verteilt Produkte auf 3 Spalten
        with col:
            st.markdown("<div class='product-container'>", unsafe_allow_html=True)

            # Titel mit Produktname einfügen
            st.markdown(f"<h6>{row['Name']}</h6>", unsafe_allow_html=True)

            image_path = os.path.join(static_folder, row["Bildname"])
            if os.path.exists(image_path):
                image_base64 = get_image_base64(image_path)
                # Bildgröße direkt im HTML-Tag definieren
                st.markdown(f"""
                    <div>
                        <img src="data:image/png;base64,{image_base64}" 
                             alt="{row['Name']}" 
                             style="width: {image_width}; height: {image_height}; object-fit: cover;">
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.write(f"Bild nicht gefunden: {row['Bildname']}")

            stock_text = f"**Stock:** {row['actual Stock']}"
            if row['actual Stock'] == 0:
                stock_text += f" <span class='not-available-text'>({_("not_available")})</span>"

            st.markdown(stock_text, unsafe_allow_html=True)

            qty_selected = st.selectbox(
                _("order"),
                options=[row["Qty 1"], row["Qty 2"], row["Qty 3"], row["Qty 4"]],
                key=f"qty_{index}",
                disabled=(row['actual Stock'] == 0)
            )
            
            if email_mode:
                if st.button(f"Bestellen: {row['Name']}", key=f"email_{index}", disabled=(row['actual Stock'] == 0)):
                    send_email_with_outlook(row['Mail'], row['Name'], row['SAP Number'], qty_selected, selected_store_name, selected_store_number)
            else:
                if st.button(f"{_("order")}: {row['Name']}", key=f"save_{index}", disabled=(row['actual Stock'] == 0)):
                    save_order(selected_store_number, row["SAP Number"], qty_selected, orders_path)

            st.markdown("</div>", unsafe_allow_html=True)

# Seiteninhalt
if selected_tab == _("products"):
    st.header(_("products"))
    display_products(products)
elif selected_tab == _("special_products"):
    st.header(_("special_products"))
    display_products(special_products, email_mode=True)
