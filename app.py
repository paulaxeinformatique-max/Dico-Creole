import streamlit as st
from st_gsheets_connection import GSheetsConnection

# Configuration
st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dico Créole Interactif")

# Connexion
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()

    recherche = st.text_input("Chercher un mot (ex: Kozé) :").strip()

    if recherche:
        resultats = df[df['Mots'].str.contains(recherche, case=False, na=False)]
        if not resultats.empty:
            for index, row in resultats.iterrows():
                st.success(f"**{row['Mots']}** : {row['Synonymes']}")
        else:
            st.warning("Mot non trouvé.")
except Exception as e:
    st.error("Connexion au tableau en cours... Vérifiez les Secrets.")
