import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dico Créole Interactif")

# Connexion au Google Sheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # On lit le tableau (TTL 0 pour avoir les changements tout de suite)
    df = conn.read(ttl=0)

    recherche = st.text_input("Chercher un synonyme (ex: Kozé) :").strip()

    if recherche:
        # On cherche dans ta colonne 'Mots'
        resultat = df[df['Mots'].str.contains(recherche, case=False, na=False)]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.info(f"👉 **{row['Mots']}** : {row['Synonymes']}")
        else:
            st.warning("Ce mot n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error("L'application se connecte au tableau, patientez un instant...")
