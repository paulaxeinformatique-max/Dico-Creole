import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dictionnaire Créole")

# Ton lien public (formaté pour être lu directement)
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8Sstsw/export?format=csv"

try:
    # On télécharge les données du tableau
    df = pd.read_csv(URL_TABLEAU)
    
    recherche = st.text_input("Chercher un mot (ex: Kozé) :").strip()

    if recherche:
        # On filtre la colonne 'Mots'
        resultat = df[df['Mots'].str.contains(recherche, case=False, na=False)]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.info(f"👉 **{row['Mots']}** : {row['Synonymes']}")
        else:
            st.warning("Mot non trouvé dans le dictionnaire.")
except Exception as e:
    st.error("Connexion au tableau en cours... vérifiez que le partage est activé.")
