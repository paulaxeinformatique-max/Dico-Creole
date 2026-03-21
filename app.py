import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dictionnaire Créole")

# MÉTHODE DE SÉCURITÉ : On nettoie l'ID
# Copie bien l'ID entre les guillemets ci-dessous
SHEET_ID = "1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8Sstsw"
URL_TABLEAU = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600) # Pour que ça charge plus vite
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(URL_TABLEAU)
    
    recherche = st.text_input("Chercher un mot (ex: Kozé) :").strip()

    if recherche:
        # On trouve automatiquement les colonnes même si les noms changent un peu
        col_mots = [c for c in df.columns if 'mot' in c.lower()][0]
        col_syn = [c for c in df.columns if 'syn' in c.lower()][0]

        mask = df[col_mots].str.contains(recherche, case=False, na=False)
        resultat = df[mask]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.info(f"👉 **{row[col_mots]}** : {row[col_syn]}")
        else:
            st.warning(f"Le mot '{recherche}' n'est pas dans le dictionnaire.")

except Exception as e:
    st.error(f"Erreur technique : {e}")
    st.write("Vérifiez que l'ID du tableau est correct dans le code.")
