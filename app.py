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
    
    # BARRE DE RECHERCHE (Clé dynamique pour forcer le rafraîchissement)
    recherche_saisie = st.text_input(
        "Chercher un mot :", 
        value=st.session_state.mot_recherche,
        key=f"barre_{st.session_state.compteur}" 
    ).strip().lower()

    # Si l'utilisateur tape manuellement, on synchronise et on relance
    if recherche_saisie != st.session_state.mot_recherche:
        st.session_state.mot_recherche = recherche_saisie
        st.rerun()

    # On définit le mot final à traiter
    mot_final = st.session_state.mot_recherche

    if mot_final:
        # Recherche précise dans 'Mots' ou 'Synonymes'
        mask_principal = df['Mots'].str.lower() == mot_final
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{mot_final}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            # ON RÉCUPÈRE LA LIGNE
            row = resultat.iloc[0]
            
            # --- CORRECTION DU TITRE ICI ---
            # On utilise le mot exact provenant de la base de données pour le titre
            mot_titre_reel = str(row['Mots'])
            st.markdown(f"## Résultat pour : **{mot_titre_reel}**")
            st.write("---")
            
            # Gestion des synonymes
            syns_bruts = str(row['Synonymes']).split(',')
            syns_propres = [s.strip() for s in syns_bruts if s.strip().lower() != mot_final]
            
            if syns_propres:
                st.write("### Synonymes cliquables :")
                cols = st.columns(6)
                for i, s in enumerate(syns_propres):
                    cols[i % 6].button(
                        s, 
                        key=f"btn_{s}_{i}_{st.session_state.compteur}",
                        on_click=cliquer_mot,
                        args=(s.lower(),)
                    )
            else:
                st.info("Ce mot est présent, mais n'a pas encore d'autres synonymes listés.")
        else:
            st.warning(f"Le mot '{mot_final}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
