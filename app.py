import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dictionnaire Créole")

# Ton lien Google Sheets
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

# --- NOUVEAUTÉ : Création de la mémoire pour le bouton ---
if "mot_cle" not in st.session_state:
    st.session_state.mot_cle = ""

def effacer_recherche():
    st.session_state.mot_cle = ""
# ---------------------------------------------------------

try:
    df = pd.read_csv(URL_TABLEAU)
    
    # On connecte la barre de recherche à notre mémoire (key="mot_cle")
    recherche = st.text_input("Chercher un mot (ex: Kozé) :", key="mot_cle").strip().lower()

    if recherche:
        # On cherche dans Mots et Synonymes
        filtre_mots = df['Mots'].str.lower().str.contains(recherche, na=False)
        filtre_synonymes = df['Synonymes'].str.lower().str.contains(recherche, na=False)
        
        resultat = df[filtre_mots | filtre_synonymes]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.success(f"👉 **{row['Mots']}**")
                st.write(f"Synonymes : {row['Synonymes']}")
        else:
            st.warning("Mot non trouvé dans le dictionnaire.")
            
        # --- NOUVEAUTÉ : Le fameux bouton pour effacer ---
        st.button("🔄 Nouvelle recherche", on_click=effacer_recherche)
            
except Exception as e:
    st.error(f"Erreur technique : {e}")
