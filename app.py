import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dictionnaire Créole")

# Le lien corrigé avec le grand "S" !
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

try:
    df = pd.read_csv(URL_TABLEAU)
    
    recherche = st.text_input("Chercher un mot (ex: Kozé) :").strip().lower()

    if recherche:
        # On cherche dans la colonne 'Mots'
        resultat = df[df['Mots'].str.lower().str.contains(recherche, na=False)]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.success(f"👉 **{row['Mots']}**")
                st.write(f"Synonymes : {row['Synonymes']}")
        else:
            st.warning("Mot non trouvé dans le dictionnaire.")
            
except Exception as e:
    st.error(f"Erreur technique : {e}")
    st.write("Vérifiez que l'ID du tableau est correct dans le code.")

