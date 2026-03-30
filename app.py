import streamlit as st
import pandas as pd
# --- ASTUCE POUR DÉSACTIVER LE CORRECTEUR ORTHOGRAPHIQUE ---
st.markdown(
    """
    <script>
        // On cherche tous les champs de saisie (input) de la page
        var inputs = window.parent.document.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].setAttribute('spellcheck', 'false');
            inputs[i].setAttribute('autocomplete', 'off');
            inputs[i].setAttribute('autocorrect', 'off');
        }
    </script>
    """,
    unsafe_allow_html=True
)
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

# 4. Initialisation et fonctions
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""
if 'compteur' not in st.session_state:
    st.session_state.compteur = 0

def cliquer_mot(nouveau_mot):
    st.session_state.mot_recherche = nouveau_mot
    st.session_state.compteur += 1

def nouvelle_recherche():
    st.session_state.mot_recherche = ""
    st.session_state.compteur += 1

# 5. Interface
try:
    df = charger_donnees()
    
    # Barre de recherche + Bouton de réinitialisation
    col_search, col_reset = st.columns([4, 1])
    
    with col_search:
        recherche = st.text_input("Chercher un mot :", value=st.session_state.mot_recherche, key=f"input_{st.session_state.compteur}").strip().lower()
    
    with col_reset:
        st.write(" ") # Petit décalage pour aligner
        if st.button("🔄 Nouvelle recherche"):
            nouvelle_recherche()
            st.rerun()

    # Si une recherche est active (soit tapée, soit cliquée)
    mot_final = recherche if recherche else st.session_state.mot_recherche

    if mot_final:
        # Recherche dans 'Mots' ou 'Synonymes'
        mask_principal = df['Mots'].str.lower() == mot_final
        mask_synonyme = df['Synonymes'].str.lower().str.contains(rf"\b{mot_final}\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            # On prend la première ligne trouvée
            row = resultat.iloc[0]
            
            # --- AFFICHAGE DU MOT CENTRAL ---
            st.markdown(f"### Mot étudié : **{row['Mots']}**")
            st.write("---")
            
            # Liste des synonymes
            syns_bruts = str(row['Synonymes']).split(',')
            # ICI : On ne filtre plus ! On garde tous les mots
            syns_propres = [s.strip() for s in syns_bruts if s.strip()]
            
            if syns_propres:
                st.write("#### Cliquez sur un synonyme pour explorer :")
                cols = st.columns(6)
                for i, s in enumerate(syns_propres):
                    # Chaque synonyme devient un bouton
                    cols[i % 6].button(
                        s, 
                        key=f"btn_{s}_{i}_{st.session_state.compteur}",
                        on_click=cliquer_mot,
                        args=(s.lower(),)
                    )
        else:
            st.warning(f"Le mot '{mot_final}' n'est pas encore répertorié.")

except Exception as e:
    st.error("Erreur de connexion au dictionnaire.")
