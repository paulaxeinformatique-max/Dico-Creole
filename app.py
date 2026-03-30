import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. Titre et Style
st.title("📖 Dictionnaire Électronique des Synonymes Créole")
st.markdown("---")

# 3. Lien Google Sheets (Format CSV)
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

# 4. Fonction de chargement avec Cache
@st.cache_data(ttl=300)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# 5. Structure principale (Le bloc Try/Except)
try:
    df = charger_donnees()
    
    # Initialisation de la variable de recherche dans la mémoire de la page
    if 'recherche' not in st.session_state:
        st.session_state.recherche = ""

    # Barre de recherche (liée à la session_state)
    recherche_input = st.text_input("Chercher un mot :", value=st.session_state.recherche).strip().lower()

    if recherche_input:
        # On met à jour la mémoire si l'utilisateur tape manuellement
        st.session_state.recherche = recherche_input
        
        # Recherche dans 'Mots' ET dans 'Synonymes'
        mask_principal = df['Mots'].str.lower() == recherche_input
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{recherche_input}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            # On affiche le premier résultat trouvé
            row = resultat.iloc[0]
            st.subheader(f"Résultat pour : {row['Mots']}")
            st.write("---")
            
            # Découpage des synonymes par la virgule
            syns = [s.strip() for s in str(row['Synonymes']).split(',')]
            
            # On retire le mot recherché de la liste des boutons
            syns_filtres = [s for s in syns if s.lower() != recherche_input]
            
            if syns_filtres:
                st.write("### Synonymes cliquables :")
                cols = st.columns(6)
                for i, s in enumerate(syns_filtres):
                    # Chaque bouton déclenche une nouvelle recherche
                    if cols[i % 6].button(s, key=f"btn_{s}_{i}"):
                        st.session_state.recherche = s.lower()
                        st.rerun()
            else:
                st.info("Ce mot est connu, mais n'a pas d'autres synonymes enregistrés.")
        else:
            st.warning(f"Le mot '{recherche_input}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Oups ! Un petit problème technique : {e}")
