import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dictionnaire Créole")

# Ton lien Google Sheets
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

try:
    df = pd.read_csv(URL_TABLEAU)
    
    recherche = st.text_input("Chercher un mot (ex: Kozé) :").strip().lower()

    if recherche:
        # On crée deux "filtres" : un pour les Mots, un pour les Synonymes
        filtre_mots = df['Mots'].str.lower().str.contains(recherche, na=False)
        filtre_synonymes = df['Synonymes'].str.lower().str.contains(recherche, na=False)
        
        # On applique les filtres (Mots OU Synonymes) grâce au symbole |
        resultat = df[filtre_mots | filtre_synonymes]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.success(f"👉 **{row['Mots']}**")
                st.write(f"Synonymes : {row['Synonymes']}")
        else:
            st.warning("Mot non trouvé dans le dictionnaire.")
            
except Exception as e:
    st.error(f"Erreur technique : {e}")

Fais la modification sur GitHub (bouton "Edit", coller, puis "Commit changes"). Attends 1 minute, rafraîchis ton application sur ton téléphone, et dis-moi si "irlé" fait bien remonter la définition de "Kozé" !

