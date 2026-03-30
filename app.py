import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# Titre
st.title("📖 Dictionnaire Électronique des Synonymes Créole")
st.markdown("---")

# Lien Google Sheets
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=600)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# --- DEBUT DU BLOC DE SECURITE ---
try:
    df = charger_donnees()
    
    if 'recherche' not in st.session_state:
        st.session_state.recherche = ""

    # Barre de recherche
    recherche_input = st.text_input("Chercher un mot :", value=st.session_state.recherche).strip().lower()

    if recherche_input:
        # On cherche dans 'Mots' ET dans 'Synonymes'
        mask_principal = df['Mots'].str.lower() == recherche_input
        mask_synonyme = df['Synonymes'].str.lower().str.contains(recherche_input, na=False)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                st.subheader(f"Résultat pour : {row['Mots']}")
                
                # Découpage des synonymes par la virgule
                syns = [s.strip() for s in str(row['Synonymes']).split(',')]
                
                # Affichage des boutons
                cols = st.columns(8)
                for i, s in enumerate(syns):
                    if s.lower() != recherche_input:
                        if cols[i % 8].button(s, key=f"{s}_{index}_{i}"):
                            st.session_state.recherche = s.lower()
                            st.rerun()
                    else:
                        cols[i % 8].markdown(f"**{s}**") 
        else:
            st.warning("Mot non trouvé dans la base actuelle.")

except Exception as e:
    # C'est ce bloc 'except' qui manquait dans ton fichier !
    st.error(f"Erreur technique : {e}")
# --- FIN DU BLOC ---
