import streamlit as st
import pandas as pd
import os
import base64
import webbrowser
from datetime import datetime  # Fehlender Import hinzugefügt

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
# Funktion zum Laden von Daten
# ---------------------------
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# ---------------------------
# Excel-Dateipfade und Static-Folder
# ---------------------------
storelist_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\storelist.xlsx"
products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\produkte.xlsx"
special_products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\produkte special.xlsx"
orders_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\bestellungen.xlsx"
logfile_path = r"C:\Users\mzuerche\Desktop\Merch Shop\data\order_logs.xlsx"  # Einheitlicher Name
static_folder = r"C:\Users\mzuerche\Desktop\Merch Shop\static"

# ---------------------------
# Lade die Daten
# ---------------------------
storelist = load_data(storelist_path)
products = load_data(products_path)
special_products = load_data(special_products_path)

# Erstelle Mappings:
# 1. Storenummer -> Storename
store_mapping = dict(zip(storelist["Storenummer"], storelist["Storename"]))
# 2. Storenummer -> Default-Sprache (Lang); "D" für Deutsch, "F" für Französisch
store_lang_mapping = dict(zip(storelist["Storenummer"], storelist["Lang"]))

# ---------------------------
# Sidebar: Navigation und Store-Auswahl
# ---------------------------
st.sidebar.title("Navigation")

# Callback-Funktion, um die Sprache beim Store-Wechsel anzupassen
def update_language():
    selected_store = st.session_state.selected_store_number
    store_default = store_lang_mapping[selected_store]
    if store_default == "D":
        st.session_state.language = "de"
    elif store_default == "F":
        st.session_state.language = "fr"
    else:
        st.session_state.language = "en"

# Store-Auswahl mit Callback:
selected_store_number = st.sidebar.selectbox(
    TRANSLATIONS["select_store"]["de"],  # Vorläufiger Text in Deutsch
    options=list(store_mapping.keys()),
    format_func=lambda x: f"{x} - {store_mapping[x]}",
    key="selected_store_number",
    on_change=update_language
)

# Falls die Sprache noch nicht gesetzt wurde, initialisiere sie anhand des ausgewählten Stores
if "language" not in st.session_state:
    update_language()

# Sprachumschaltung: Der Benutzer kann die Sprache manuell ändern
selected_language = st.sidebar.selectbox(
    "Sprache / Language",
    options=list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state.language),
    format_func=lambda x: LANGUAGES[x]
)
st.session_state.language = selected_language

# Anzeige des aktuell gewählten Stores
selected_store_name = store_mapping[selected_store_number]
st.sidebar.write(f"{_('current_store')}: {selected_store_name} ({selected_store_number})")

# Navigation: Seiten
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
# Funktion: Zahlen formatieren (keine Dezimalstelle, wenn nicht nötig)
# ---------------------------
def format_number(num):
    try:
        if isinstance(num, float) and num.is_integer():
            return str(int(num))
        elif isinstance(num, int):
            return str(num)
        else:
            return str(num)
    except Exception:
        return str(num)

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

            # Layout mit Bild und Benachrichtigungen in einer Zeile
            img_col, msg_col = st.columns([1, 2])
            with img_col:
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
                    st.write(f"Bild nicht gefunden: {image_name}")

            with msg_col:
                if email_mode and st.session_state.get(f"email_sent_{index}", False):
                    st.info("Email window opened.")
                elif not email_mode and st.session_state.get(f"order_saved_{index}", False):
                    st.success(_("order_success"))

            # SAP-Nummer anzeigen, falls vorhanden
            if 'SAP Number' in row and not pd.isna(row['SAP Number']):
                sap_number = format_number(row['SAP Number'])
                sap_text = f"**SAP Nummer:** {sap_number}"
                st.markdown(sap_text, unsafe_allow_html=True)

            # Stock-Wert formatieren
            stock_val = format_number(row['actual Stock'])
            stock_text = f"**Stock:** {stock_val}"
            if row['actual Stock'] == 0:
                stock_text += f" <span class='not-available-text'>({_("not_available")})</span>"
            st.markdown(stock_text, unsafe_allow_html=True)

            # Bestellmengen aus den verfügbaren Spalten sammeln
            qty_options = [qty for qty in [row.get("Qty 1"), row.get("Qty 2"), row.get("Qty 3"), row.get("Qty 4")] if not pd.isna(qty)]
            
            if qty_options:
                qty_selected = st.selectbox(
                    _("order"),
                    options=qty_options,
                    format_func=format_number,
                    key=f"qty_{index}",
                    disabled=(row['actual Stock'] == 0)
                )

                if email_mode:
                    if st.button(f"{_('order')}: {row['Name']}", key=f"email_{index}", disabled=(row['actual Stock'] == 0)):
                        send_email_with_outlook(
                            row['Mail'], row['Name'], row['SAP Number'],
                            qty_selected, selected_store_name, selected_store_number
                        )
                        st.session_state[f"email_sent_{index}"] = True
                        st.rerun()
                else:
                    # Hier wird save_order mit zusätzlichem Produktnamen aufgerufen,
                    # sodass der Logeintrag erstellt werden kann.
                    if st.button(f"{_('order')}: {row['Name']}", key=f"save_{index}", disabled=(row['actual Stock'] == 0)):
                        save_order(selected_store_number, row["SAP Number"], row["Name"], qty_selected, orders_path)
                        st.session_state[f"order_saved_{index}"] = True
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #ddd; margin: 20px 0;'>", unsafe_allow_html=True)

# ---------------------------
# Funktion: Bestellung speichern und Logeintrag erstellen
# ---------------------------
def save_order(store_number, sap_number, product_name, quantity, orders_path):
    orders_df = pd.read_excel(orders_path, index_col=0)
    if store_number not in orders_df.index:
        st.error("Storenummer nicht gefunden.")
        return
    if sap_number not in orders_df.columns:
        st.error("SAP-Nummer nicht gefunden.")
        return
    orders_df.at[store_number, sap_number] = quantity
    orders_df.to_excel(orders_path)
    # Log-Eintrag nach dem Speichern erstellen
    log_order(store_number, store_mapping[store_number], sap_number, product_name, quantity)

# ---------------------------
# Funktion: Email mit Outlook öffnen
# ---------------------------
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

# ---------------------------
# Funktion: Logdatei aktualisieren
# ---------------------------
def log_order(store_number, store_name, sap_number, product_name, quantity):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    log_entry = {
        "Datum": date_str,
        "Zeit": time_str,
        "Storenummer": store_number,
        "Storename": store_name,
        "SAP Nummer": sap_number,
        "Produktname": product_name,
        "Anzahl": quantity
    }

    # Erstelle ein DataFrame für den neuen Eintrag
    new_entry_df = pd.DataFrame([log_entry])

    if os.path.exists(logfile_path):
        logs_df = pd.read_excel(logfile_path)
        # Füge den neuen Eintrag mit pd.concat() hinzu
        logs_df = pd.concat([logs_df, new_entry_df], ignore_index=True)
    else:
        logs_df = new_entry_df

    logs_df.to_excel(logfile_path, index=False)

# ---------------------------
# Seiteninhalt anzeigen
# ---------------------------
if selected_tab == _("products"):
    st.header(_("products"))
    display_products(products)
elif selected_tab == _("special_products"):
    st.header(_("special_products"))
    display_products(special_products, email_mode=True)
