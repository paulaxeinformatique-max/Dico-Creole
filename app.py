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
        # On s'assure que la session_state est à jour avec la saisie manuelle
        st.session_state.recherche = recherche_input
        
        # Recherche dans les deux colonnes
        mask_principal = df['Mots'].str.lower() == recherche_input
        mask_synonyme = df['Synonymes'].str.lower().str.contains(recherche_input, na=False)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            # On ne prend que le premier résultat pour éviter les doublons d'affichage
            row = resultat.iloc[0] 
            
            # MISE À JOUR DYNAMIQUE DU TITRE
            st.subheader(f"Résultat pour : {row['Mots']}")
            st.write("---")
            
            # Découpage des synonymes
            syns = [s.strip() for s in str(row['Synonymes']).split(',')]
            
            st.write("### Synonymes cliquables :")
            # On filtre la liste pour NE PAS afficher le mot qu'on vient de chercher
            syns_filtres = [s for s in syns if s.lower() != recherche_input]
            
            if syns_filtres:
                cols = st.columns(6) # 6 colonnes pour que ce soit lisible sur mobile
                for i, s in enumerate(syns_filtres):
                    # Chaque bouton met à jour la recherche et relance l'app
                    if cols[i % 6].button(s, key=f"btn_{s}_{i}"):
                        st.session_state.recherche = s.lower()
                        st.rerun()
            else:
                st.info("Ce mot est présent, mais n'a pas d'autres synonymes listés ici.")
        else:
            st.warning(f"Le mot '{recherche_input}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    # C'est ce bloc 'except' qui manquait dans ton fichier !
    st.error(f"Erreur technique : {e}")
# --- FIN DU BLOC ---
