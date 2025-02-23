import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
import win32com.client as win32

# Dateipfade zu den benötigten Excel-Dateien und dem statischen Bildordner
storelist_path = r"C:\Users\mzuerche\Desktop\Merch Shop\storelist.xlsx"
products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\produkte.xlsx"
special_products_path = r"C:\Users\mzuerche\Desktop\Merch Shop\produkte special.xlsx"
orders_path = r"C:\Users\mzuerche\Desktop\Merch Shop\bestellungen.xlsx"
static_folder = r"C:\Users\mzuerche\Desktop\Merch Shop\static"

# Funktion zum Laden von Daten aus einer Excel-Datei
def load_data(file_path):
    return pd.read_excel(file_path)

# Laden der Daten aus den Dateien
storelist = load_data(storelist_path)
products = load_data(products_path)
special_products = load_data(special_products_path)
orders = load_data(orders_path)

# Streamlit-Seitenlayout konfigurieren
st.set_page_config(page_title="Internal Store Shop", layout="wide")

# Seitenleiste für die Auswahl des Stores und Navigation
st.sidebar.title("Navigation")
selected_store_number = st.sidebar.selectbox("Wähle deine Store-Nummer:", storelist["Storenummer"])
selected_store_name = storelist.loc[storelist["Storenummer"] == selected_store_number, "Storename"].values[0]
st.sidebar.write(f"Aktueller Store: {selected_store_name} ({selected_store_number})")

selected_tab = st.sidebar.radio("Seiten", ["Produkte", "Spezialprodukte"])

# Funktion zur Kodierung einer Bilddatei als Base64-String
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Funktion zum Senden einer E-Mail-Bestellung
def send_email(recipient, product_name, qty, store_number, store_name, sap_number):
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = recipient
        mail.Subject = f"Bestellung: {product_name}"
        mail.Body = (
            f"Hello Team\n\n"
            f"We order the following item:\n\n"
            f"Storenumber: {store_number}\n"
            f"Storename: {store_name}\n"
            f"SAP Number: {sap_number}\n"
            f"Name: {product_name}\n"
            f"Amount: {qty}\n\n"
            f"Order name:\n\n"
            f"Thanks and regards"
        )
        mail.Display()
    except Exception as e:
        st.error(f"Fehler beim Senden der E-Mail: {e}")

# CSS-Styling für ein sauberes Layout mit dünnen Linien
st.markdown(
    """
    <style>
    .product-container {
        border-bottom: 1px solid #ddd;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #ffffff;
    }
    .resized-image {
        height: 100px;
        width: auto;
        display: block;
        margin: 0 auto;
    }
    .spacer {
        height: 10px;
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Funktion zum Speichern einer Bestellung in die Excel-Datei
def save_order(store_number, sap_number, quantity):
    try:
        df_orders = pd.read_excel(orders_path, index_col=0)
        if store_number in df_orders.index and sap_number in df_orders.columns:
            df_orders.at[store_number, sap_number] = quantity
        else:
            st.error("Bestellung kann nicht gespeichert werden. Storenummer oder SAP-Nummer nicht gefunden.")
            return
        df_orders.to_excel(orders_path)
        st.success("Bestellung wurde erfolgreich gespeichert!")
    except Exception as e:
        st.error(f"Fehler beim Speichern der Bestellung: {e}")

# Funktion zur Anzeige der Produkte mit optimiertem Layout
def display_products(product_data, email_mode=False):
    col1, col2 = st.columns(2)  # Stellt sicher, dass zwei Produkte pro Reihe angezeigt werden
    
    for index, row in product_data.iterrows():
        with (col1 if index % 2 == 0 else col2):
            image_path = os.path.join(static_folder, row["Bildname"])
            try:
                st.markdown('<div class="product-container">', unsafe_allow_html=True)
                
                # Produktbild anzeigen
                if os.path.exists(image_path):
                    image_base64 = get_image_base64(image_path)
                    st.markdown(
                        f"""
                        <div>
                            <img src="data:image/png;base64,{image_base64}" class="resized-image" alt="{row['Name']}">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.write(f"Bild nicht gefunden: {row['Bildname']}")

                # Produktdetails anzeigen
                st.write(f"**SAP Nummer:** {row['SAP Number']}")
                st.write(f"**Lagerbestand:** {row['actual Stock']}")

                # Bestellung nur erlauben, wenn Lagerbestand verfügbar ist
                if row['actual Stock'] > 0:
                    qty_selected = st.selectbox(
                        "Menge auswählen:",
                        options=[row["Qty 1"], row["Qty 2"], row["Qty 3"], row["Qty 4"]],
                        key=f"qty_{index}"
                    )

                    if email_mode:
                        if st.button(f"Per Mail bestellen: {row['Name']}", key=f"email_{index}"):
                            send_email(row["Mail"], row["Name"], qty_selected, selected_store_number, selected_store_name, row["SAP Number"])
                    else:
                        if st.button(f"Bestellung speichern: {row['Name']}", key=f"save_{index}"):
                            save_order(selected_store_number, row["SAP Number"], qty_selected)
                else:
                    # Warnmeldung anzeigen und für gleichmäßige Höhe sorgen
                    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
                    st.warning(f"{row['Name']} ist nicht verfügbar und kann nicht bestellt werden.")
                    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.write(f"Fehler beim Laden des Bildes: {e}")

# Die ausgewählte Seite und die relevanten Produkte anzeigen
if selected_tab == "Produkte":
    st.header("Produkte")
    display_products(products)
elif selected_tab == "Spezialprodukte":
    st.header("Spezialprodukte")
    display_products(special_products, email_mode=True)
