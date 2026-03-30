import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# Nouveau Titre inspiré du CRISCO
st.title("📖 Dictionnaire Électronique des Synonymes Créole")
st.markdown("---")

# Lien de ton Google Sheets (Format CSV)
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

# Fonction pour charger les données (avec cache pour la rapidité)
@st.cache_data(ttl=600)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

try:
    df = charger_donnees()
    
    # Gestion de la recherche (Session State permet le clic sur les mots)
    if 'recherche' not in st.session_state:
        st.session_state.recherche = ""

    # Barre de recherche
    recherche_input = st.text_input("Chercher un mot :", value=st.session_state.recherche).strip().lower()

if recherche_input:
        # On cherche si le mot est un MOT PRINCIPAL ou s'il est CONTENU dans les synonymes
        mask_principal = df['Mots'].str.lower() == recherche_input
        mask_synonyme = df['Synonymes'].str.lower().str.contains(recherche_input, na=False)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            for index, row in resultat.iterrows():
                # On affiche le mot trouvé (ou le mot dont il est le synonyme)
                st.subheader(f"Résultat pour : {row['Mots']}")
                
                # On sépare les synonymes par la virgule
                syns = [s.strip() for s in str(row['Synonymes']).split(',')]
                
                # Création des boutons cliquables
                cols = st.columns(len(syns) if len(syns) < 8 else 8)
                for i, s in enumerate(syns):
                    # On crée le bouton (on évite que le mot se cherche lui-même)
                    if s.lower() != recherche_input:
                        if cols[i % 8].button(s, key=f"{s}_{index}_{i}"):
                            st.session_state.recherche = s.lower()
                            st.rerun()
                    else:
                        cols[i % 8].write(f"**{s}**") # On affiche en gras le mot cherché
        else:
            st.warning("Mot non trouvé. Les écrivains y travaillent peut-être déjà !")
            
except Exception as e:
    st.error("Connexion au dictionnaire en cours... Veuillez patienter.")
