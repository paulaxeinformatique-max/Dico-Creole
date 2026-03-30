import streamlit as st
import pandas as pd

# 1. Configuration
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. Titre
st.title("📖 Dictionnaire Électronique des Synonymes Créole")
st.markdown("---")

# 3. Données
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=300)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# 4. Initialisation du Session State
if 'recherche_key' not in st.session_state:
    st.session_state.recherche_key = ""

# 5. Interface
try:
    df = charger_donnees()
    
    # Barre de recherche (L'astuce est d'utiliser 'value' lié au session_state)
    recherche_input = st.text_input(
        "Chercher un mot :", 
        value=st.session_state.recherche_key,
        key="barre_recherche"
    ).strip().lower()

    # Si l'utilisateur tape quelque chose de nouveau, on met à jour la mémoire
    if recherche_input != st.session_state.recherche_key:
        st.session_state.recherche_key = recherche_input
        st.rerun()

    if st.session_state.recherche_key:
        mot_actuel = st.session_state.recherche_key
        
        # Recherche dans les colonnes
        mask_principal = df['Mots'].str.lower() == mot_actuel
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{mot_actuel}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            row = resultat.iloc[0]
            
            # Affichage du titre qui SE MET À JOUR
            st.subheader(f"Résultat pour : {row['Mots']}")
            st.write("---")
            
            # Gestion des synonymes
            syns = [s.strip() for s in str(row['Synonymes']).split(',')]
            # On filtre pour ne pas afficher le mot qu'on regarde déjà
            syns_filtres = [s for s in syns if s.lower() != mot_actuel]
            
            if syns_filtres:
                st.write("### Synonymes cliquables :")
                cols = st.columns(6)
                for i, s in enumerate(syns_filtres):
                    # Quand on clique, on change la mémoire ET on relance tout
                    if cols[i % 6].button(s, key=f"btn_{s}_{i}"):
                        st.session_state.recherche_key = s.lower()
                        st.rerun()
            else:
                st.info("Ce mot est présent, mais n'a pas encore d'autres synonymes listés.")
        else:
            st.warning(f"Le mot '{mot_actuel}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
