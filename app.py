import streamlit as st
import pandas as pd

# 1. Configuration de la page (Format large pour ressembler au CRISCO)
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. Titre principal
st.title("📖 Dictionnaire Électronique des Synonymes Créole")
st.markdown("---")

# 3. Lien vers ton Google Sheets (Format CSV pour lecture directe)
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

# 4. Fonction de chargement des données (Cache de 5 minutes)
@st.cache_data(ttl=300)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# 5. Structure principale avec gestion d'erreurs
try:
    df = charger_donnees()
    
    # Initialisation de la variable de recherche dans la mémoire de la page
    if 'recherche' not in st.session_state:
        st.session_state.recherche = ""

    # Barre de recherche liée à la clé 'recherche' pour mise à jour immédiate
    recherche_input = st.text_input("Chercher un mot :", key="recherche").strip().lower()

    if recherche_input:
        # Recherche dans la colonne 'Mots' ET dans la colonne 'Synonymes'
        mask_principal = df['Mots'].str.lower() == recherche_input
        # On utilise une regex pour trouver le mot exact même au milieu d'une liste
        mask_synonyme = df['Synonymes'].str.lower().str.contains(f"\\b{recherche_input}\\b", na=False, regex=True)
        
        resultat = df[mask_principal | mask_synonyme]
        
        if not resultat.empty:
            # On récupère la première ligne correspondante
            row = resultat.iloc[0]
            
            # Affichage du mot principal trouvé
            st.subheader(f"Résultat pour : {row['Mots']}")
            st.write("---")
            
            # Découpage de la chaîne de synonymes en liste
            syns = [s.strip() for s in str(row['Synonymes']).split(',')]
            
            # On retire le mot recherché de la liste des boutons pour plus de clarté
            syns_filtres = [s for s in syns if s.lower() != recherche_input]
            
            if syns_filtres:
                st.write("### Synonymes cliquables :")
                # On crée une grille de 6 colonnes
                cols = st.columns(6)
                for i, s in enumerate(syns_filtres):
                    # Chaque bouton met à jour la barre de recherche et relance l'app
                    if cols[i % 6].button(s, key=f"btn_{s}_{i}"):
                        st.session_state.recherche = s.lower()
                        st.rerun()
            else:
                st.info("Ce mot est présent, mais n'a pas encore d'autres synonymes listés.")
        else:
            st.warning(f"Le mot '{recherche_input}' n'est pas encore dans le dictionnaire.")

except Exception as e:
    st.error(f"Une erreur est survenue lors de la connexion aux données : {e}")
