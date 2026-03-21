import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dico Créole", page_icon="📖")
st.title("📖 Dictionnaire Créole")

# Ton lien public
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8Sstsw/export?format=csv"

try:
    # On essaie de lire le tableau
    df = pd.read_csv(URL_TABLEAU)
    
    # --- TEST DE DIAGNOSTIC ---
    # st.write("Colonnes trouvées :", df.columns.tolist()) 
    # ---------------------------

    recherche = st.text_input("Chercher un mot (ex: Kozé) :").strip()

    if recherche:
        # On vérifie si la colonne s'appelle bien 'Mots' (attention aux majuscules !)
        # Si ton tableau utilise 'MOTS' ou 'mots', on s'adapte :
        colonne_mots = "Mots" if "Mots" in df.columns else df.columns[0]
        colonne_syn = "Synonymes" if "Synonymes" in df.columns else df.columns[1]

        resultat = df[df[colonne_mots].str.contains(recherche, case=False, na=False)]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.info(f"👉 **{row[colonne_mots]}** : {row[colonne_syn]}")
        else:
            st.warning(f"Le mot '{recherche}' n'est pas dans le dictionnaire.")

except Exception as e:
    # ICI : On affiche l'erreur réelle pour comprendre le problème
    st.error(f"Erreur technique : {e}")
    st.info("Vérifiez que le fichier Google Sheets est bien partagé en 'Public' (Tous les utilisateurs disposant du lien).")
