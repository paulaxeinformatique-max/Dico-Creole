import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. CHARGEMENT DES DONNÉES
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60) # Cache de 1 minute pour voir les modifs rapidement
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# 3. BARRE LATÉRALE (NAVIGATION)
st.sidebar.title("📖 Menu Principal")
page = st.sidebar.radio("Aller vers :", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE : DICTIONNAIRE (RECHERCHE) ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Dictionnaire des Synonymes")
    
    if 'mot_recherche' not in st.session_state:
        st.session_state.mot_recherche = ""
    if 'compteur' not in st.session_state:
        st.session_state.compteur = 0

    def cliquer_mot(nouveau_mot):
        st.session_state.mot_recherche = nouveau_mot
        st.session_state.compteur += 1

    # Barre de recherche
    recherche = st.text_input("Chercher un mot :", value=st.session_state.mot_recherche, key=f"in_{st.session_state.compteur}").strip().lower()

    if recherche:
        try:
            df = charger_donnees()
            mask = (df['Mots'].str.lower() == recherche) | (df['Synonymes'].str.lower().str.contains(rf"\b{recherche}\b", na=False, regex=True))
            resultat = df[mask]
            
            if not resultat.empty:
                row = resultat.iloc[0]
                st.markdown(f"### Mot étudié : **{row['Mots']}**")
                
                syns = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip()]
                st.write("---")
                st.write("#### Synonymes :")
                cols = st.columns(5)
                for i, s in enumerate(syns):
                    if cols[i % 5].button(s, key=f"btn_{s}_{i}_{st.session_state.compteur}"):
                        cliquer_mot(s.lower())
                        st.rerun()
            else:
                st.warning(f"Le mot '{recherche}' n'est pas encore répertorié.")
        except Exception as e:
            st.error("Erreur lors du chargement du dictionnaire.")

# --- PAGE : ESPACE AUTEURS (SÉCURISÉ) ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie Sécurisé")
    st.write("Cet espace est réservé aux écrivains pour l'enrichissement du dictionnaire.")
    
    # Simple protection par mot de passe
    code = st.text_input("Entrez votre code d'accès :", type="password")
    
    if code == "1234": # C'est le code temporaire, on le changera ensemble
        st.success("Bienvenue ! Vous êtes identifié.")
        st.info("Bientôt, vous trouverez ici le formulaire pour ajouter des mots directement.")
        # C'est ici que nous coderons le formulaire à l'étape suivante
    elif code != "":
        st.error("Code d'accès incorrect.")
