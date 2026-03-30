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

# 4. Logique de navigation (La solution à ton erreur)
if 'recherche_key' not in st.session_state:
    st.session_state.recherche_key = ""

def clou_du_spectacle(mot):
    """Cette fonction change la valeur de la recherche proprement"""
    st.session_state.recherche_key = mot

# 5. Interface
try:
    df = charger_donnees()
    
    # Barre de recherche avec la nouvelle clé
    recherche_input = st.text_input(
        "Chercher un mot :", 
        value=st.session_state.recherche_key,
        key="barre_recherche"
    ).strip().lower()

    # Si l'utilisateur tape au clavier, on synchronise
    if recherche_input != st.session_state.recherche_key:
        st.session_state.recherche_key = recherche_input

    if st.session_state.recherche_key:
        mot_cherche = st.session_state.recherche_key
        
        # Recherche
        mask_principal = df['Mots'].str.lower() == mot_cherche
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{mot_cherche}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            row = resultat.iloc[0]
            st.subheader(f"Résultat pour : {row['Mots']}")
            st.write("---")
            
            syns = [s.strip() for s in str(row['Synonymes']).split(',')]
            syns_filtres = [s for s in syns if s.lower() != mot_cherche]
            
            if syns_filtres:
                st.write("### Synonymes cliquables :")
                cols = st.columns(6)
                for i, s in enumerate(syns_filtres):
                    # On utilise on_click pour éviter de modifier le widget directement
                    cols[i % 6].button(
                        s, 
                        key=f"btn_{s}_{i}", 
                        on_click=clou_du_spectacle, 
                        args=(s.lower(),)
                    )
            else:
                st.info("Ce mot est présent, mais n'a pas encore d'autres synonymes listés.")
        else:
            st.warning(f"Le mot '{mot_cherche}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
