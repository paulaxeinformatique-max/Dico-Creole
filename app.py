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
    
    # BARRE DE RECHERCHE
    # On utilise une astuce : on ne lie pas 'value' directement pour éviter les conflits
    recherche_saisie = st.text_input(
        "Chercher un mot :", 
        value=st.session_state.recherche_key,
        key="barre_recherche"
    ).strip().lower()

    # Si la saisie change, on met à jour la mémoire et on relance
    if recherche_saisie != st.session_state.recherche_key:
        st.session_state.recherche_key = recherche_saisie
        st.rerun()

    # LE MOT À AFFICHER EST CELUI EN MÉMOIRE
    mot_actuel = st.session_state.recherche_key

    if mot_actuel:
        # Recherche
        mask_principal = df['Mots'].str.lower() == mot_actuel
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{mot_actuel}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            # ON PREND LE MOT DE LA LIGNE TROUVÉE
            row = resultat.iloc[0]
            nom_mot_trouve = str(row['Mots'])
            
            # AFFICHAGE DU TITRE DYNAMIQUE
            # Ici, on force l'affichage du mot correspondant à la recherche
            st.subheader(f"Résultat pour : {nom_mot_trouve}")
            st.write("---")
            
            # Gestion des synonymes
            syns = [s.strip() for s in str(row['Synonymes']).split(',')]
            syns_filtres = [s for s in syns if s.lower() != mot_actuel]
            
            if syns_filtres:
                st.write("### Synonymes cliquables :")
                cols = st.columns(6)
                for i, s in enumerate(syns_filtres):
                    # Quand on clique, on force la mémoire et on rerun
                    if cols[i % 6].button(s, key=f"btn_{s}_{i}"):
                        st.session_state.recherche_key = s.lower()
                        st.rerun()
            else:
                st.info("Ce mot est présent, mais n'a pas d'autres synonymes listés.")
        else:
            st.warning(f"Le mot '{mot_actuel}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
