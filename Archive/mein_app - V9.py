import streamlit as st
import pandas as pd
import os
import base64
import webbrowser

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
    "products": {"de": "Merchandise Produkte", "en": "Merchandise Products", "fr": "Produits de merchandise", "it": "Prodotti Merchandise"},
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

# Excel-Dateipfade
storelist_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\storelist.xlsx"
products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\produkte.xlsx"
special_products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\produkte special.xlsx"
orders_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\bestellungen.xlsx"
static_folder = r"C:\Users\mzuerche\Desktop\Merch Shop\static"

# Funktion zum Laden von Daten
# Funktion zum Laden von Daten (bleibt unverändert)
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Produkte nur einmal laden und in die Session speichern
if "storelist_data" not in st.session_state:
    st.session_state.storelist_data = load_data(storelist_path)
if "products_data" not in st.session_state:
    st.session_state.products_data = load_data(products_path)
if "special_products_data" not in st.session_state:
    st.session_state.special_products_data = load_data(special_products_path)
if "orders_data" not in st.session_state:
    st.session_state.orders_data = load_data(orders_path)

# Zugriff auf die Produkte aus der Session
storelist = st.session_state.storelist_data
products = st.session_state.products_data
special_products = st.session_state.special_products_data
orders = st.session_state.orders_data


st.sidebar.title("Navigation")

# Kombiniere Storenummer und Storename für die Anzeige im Dropdown-Menü
store_options = storelist.apply(lambda row: f"{row['Storenummer']} - {row['Storename']}", axis=1)
# Speichere eine Zuordnung zwischen der kombinierten Anzeige und der echten Storenummer
store_display_map = dict(zip(store_options, storelist["Storenummer"]))
# Dropdown-Menü für die Storeauswahl
selected_store_display = st.sidebar.selectbox(_("select_store"), options=store_options)
# Extrahiere die tatsächliche Storenummer für die folgenden Funktionen
selected_store_number = store_display_map[selected_store_display]
# Erhalte den Storename zur Anzeige, aber ohne ihn für weitere Funktionen zu verwenden
selected_store_name = storelist.loc[storelist["Storenummer"] == selected_store_number, "Storename"].values[0]
# Anzeige des aktuellen Stores in der Sidebar
st.sidebar.write(f"{_('current_store')}: {selected_store_name} ({selected_store_number})")


selected_tab = st.sidebar.radio("Seiten", [_("products"), _("special_products")])

st.title("Internal SST Shop")

# Seiteninhalt
if selected_tab == _("products"):
    st.header(_("products"))
    display_products(products)
elif selected_tab == _("special_products"):
    st.header(_("special_products"))
    display_products(special_products, email_mode=True)

# Funktion zur Kodierung eines Bildes als Base64
@st.cache_data
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Funktion zur Produktanzeige als Grid
def display_products(product_data, email_mode=False):
    cols = st.columns(3)

    for index, row in product_data.iterrows():
        col = cols[index % 3]
        with col:
            st.markdown("<div class='product-container'>", unsafe_allow_html=True)

            st.markdown(f"<h5>{row['Name']}</h5>", unsafe_allow_html=True)

            if not pd.isna(row.get("Bemerkungen", "")) and row["Bemerkungen"].strip():
                st.markdown(f"<p style='font-size: small; color: gray;'>{row['Bemerkungen']}</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size: small;'>&nbsp;</p>", unsafe_allow_html=True)

            # Layout mit Bild und Benachrichtigungen in einer Zeile
            img_col, msg_col = st.columns([1, 2])
            with img_col:
                image_path = os.path.join(static_folder, row["Bildname"])
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
                    st.write(f"Bild nicht gefunden: {row['Bildname']}")

            with msg_col:
                if email_mode and st.session_state.get(f"email_sent_{index}", False):
                    st.info("Email window opened.")
                elif not email_mode and st.session_state.get(f"order_saved_{index}", False):
                    st.success(_("order_success"))

            stock_text = f"**Stock:** {row['actual Stock']}"
            if row['actual Stock'] == 0:
                stock_text += f" <span class='not-available-text'>({_("not_available")})</span>"

            st.markdown(stock_text, unsafe_allow_html=True)

            qty_options = [
                int(qty) if isinstance(qty, float) and qty.is_integer() else qty
                for qty in [row.get("Qty 1"), row.get("Qty 2"), row.get("Qty 3"), row.get("Qty 4")]
                if not pd.isna(qty)
            ]

            if qty_options:
                qty_selected = st.selectbox(
                    _("order"),
                    options=qty_options,
                    format_func=lambda x: str(int(x)) if isinstance(x, (int, float)) and x == int(x) else str(x),
                    key=f"qty_{index}",
                    disabled=(row['actual Stock'] == 0)
                )

            if email_mode:
                if st.button(f"Bestellen: {row['Name']}", key=f"email_{index}", disabled=(row['actual Stock'] == 0)):
                    send_email_with_outlook(
                        row['Mail'], row['Name'], row['SAP Number'],
                        qty_selected, selected_store_name, selected_store_number
                    )
                    st.session_state[f"email_sent_{index}"] = True
                    st.rerun()
            else:
                if st.button(f"{_('order')}: {row['Name']}", key=f"save_{index}", disabled=(row['actual Stock'] == 0)):
                    save_order(selected_store_number, row["SAP Number"], qty_selected, orders_path)
                    st.session_state[f"order_saved_{index}"] = True
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #ddd; margin: 20px 0;'>", unsafe_allow_html=True)

# Funktion zur Speicherung der Bestellung
def save_order(store_number, sap_number, quantity, orders_path):
    orders_df = pd.read_excel(orders_path, index_col=0)

    if store_number not in orders_df.index:
        st.error("Storenummer nicht gefunden.")
        return
    if sap_number not in orders_df.columns:
        st.error("SAP-Nummer nicht gefunden.")
        return

    orders_df.at[store_number, sap_number] = quantity
    orders_df.to_excel(orders_path)

# Funktion zum Versenden einer E-Mail
def send_email_with_outlook(email_recipient, product_name, sap_number, quantity, store_name, store_number):
    email_body = (
        f"Hello Team%0A%0A"
        f"We order the following item:%0A%0A"
        f"Productname: {product_name}%0A"
        f"SAP Number: {sap_number}%0A"
        f"Storename: {store_name}%0A"
        f"Storenumber: {store_number}%0A"
        f"Amount: {quantity}%0A%0A"
        f"Orderer name:%0A%0A"
        f"Thanks and regards"
    )

    email_subject = f"Order: {product_name} - {sap_number}"
    mailto_link = f"mailto:{email_recipient}?subject={email_subject}&body={email_body}"
    webbrowser.open(mailto_link)

# Seiteninhalt
if selected_tab == _("products"):
    st.header(_("products"))
    display_products(products)
elif selected_tab == _("special_products"):
    st.header(_("special_products"))
    display_products(special_products, email_mode=True)
