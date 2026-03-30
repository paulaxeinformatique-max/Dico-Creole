import streamlit as st
import pandas as pd

# 1. Configuration
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. Titre principal de l'application
st.title("📖 Dictionnaire Électronique des Synonymes Créole")
st.markdown("---")

# 3. Données
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=300)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# 4. Initialisation du Session State
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""
if 'compteur' not in st.session_state:
    st.session_state.compteur = 0

# Fonction de mise à jour lors du clic
def cliquer_mot(nouveau_mot):
    st.session_state.mot_recherche = nouveau_mot
    st.session_state.compteur += 1

# 5. Interface
try:
    df = charger_donnees()
    
    # BARRE DE RECHERCHE (Clé dynamique pour le rafraîchissement)
    recherche_saisie = st.text_input(
        "Chercher un mot :", 
        value=st.session_state.mot_recherche,
        key=f"barre_{st.session_state.compteur}" 
    ).strip().lower()

    # Synchronisation manuelle
    if recherche_saisie != st.session_state.mot_recherche:
        st.session_state.mot_recherche = recherche_saisie
        st.rerun()

    mot_final = st.session_state.mot_recherche

    if mot_final:
        # Recherche dans 'Mots' ou 'Synonymes'
        mask_principal = df['Mots'].str.lower() == mot_final
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{mot_final}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            row = resultat.iloc[0]
            
            # On a supprimé la ligne "Résultat pour :" ici pour épurer
            
            # Gestion et affichage des synonymes
            syns_bruts = str(row['Synonymes']).split(',')
            syns_propres = [s.strip() for s in syns_bruts if s.strip().lower() != mot_final]
            
            if syns_propres:
                st.write(f"### Synonymes pour **{row['Mots']}** :")
                cols = st.columns(6)
                for i, s in enumerate(syns_propres):
                    cols[i % 6].button(
                        s, 
                        key=f"btn_{s}_{i}_{st.session_state.compteur}",
                        on_click=cliquer_mot,
                        args=(s.lower(),)
                    )
            else:
                st.info(f"Le mot **{row['Mots']}** est présent, mais n'a pas encore d'autres synonymes listés.")
        else:
            st.warning(f"Le mot '{mot_final}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
