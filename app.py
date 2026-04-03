import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. CHARGEMENT
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees():
    return pd.read_csv(URL_TABLEAU)

# 3. NAVIGATION
st.sidebar.title("📖 Menu Principal")
page = st.sidebar.radio("Aller vers :", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE : DICTIONNAIRE ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Recherche dans le Dictionnaire")
    
    df = charger_donnees()
    liste_mots = sorted(df['Mots'].dropna().unique().tolist()) # Liste pour l'auto-complétion

    if 'mot_recherche' not in st.session_state:
        st.session_state.mot_recherche = ""

    # Ligne de recherche avec bouton "Nouvelle Recherche"
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # L'auto-complétion se fait via selectbox ici
        choix = st.selectbox("Tapez ou choisissez un mot :", 
                             options=[""] + liste_mots, 
                             index=0 if st.session_state.mot_recherche == "" else liste_mots.index(st.session_state.mot_recherche) + 1 if st.session_state.mot_recherche in liste_mots else 0)
        
    with col2:
        st.write(" ") # Calage visuel
        if st.button("🔄 Nouvelle recherche"):
            st.session_state.mot_recherche = ""
            st.rerun()

    recherche = choix.lower() if choix else ""

    if recherche:
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
                if cols[i % 5].button(s, key=f"btn_{s}_{i}"):
                    st.session_state.mot_recherche = s.strip()
                    st.rerun()

# --- PAGE : ESPACE AUTEURS ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie Sécurisé")
    
    code = st.text_input("Code d'accès :", type="password")
    
    if code == "1234":
        st.success("Accès Auteur validé")
        st.write("---")
        
        # FORMULAIRE DE SAISIE
        st.subheader("Ajouter ou modifier une entrée")
        
        with st.form("form_saisie"):
            nouveau_mot = st.text_input("Mot principal (ex: Kozé)")
            nouveaux_syns = st.text_area("Synonymes (séparés par des virgules)")
            
            submit = st.form_submit_button("Prévisualiser")
            
            if submit:
                st.info("Voici à quoi ressemblera l'entrée :")
                st.markdown(f"### **{nouveau_mot}**")
                syn_list = nouveaux_syns.split(',')
                cols = st.columns(6)
                for i, s in enumerate(syn_list):
                    cols[i % 6].button(s.strip(), key=f"preview_{i}")
                
                st.warning("⚠️ L'enregistrement automatique vers Google Sheets arrive à l'étape suivante.")

    elif code != "":
        st.error("Code incorrect")
