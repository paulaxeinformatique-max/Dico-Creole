import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# --- 2. CONNEXION GOOGLE SHEETS ---
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees():
    df = pd.read_csv(URL_TABLEAU)
    groupes = []
    tous_les_mots = set()
    for _, row in df.iterrows():
        mots_du_groupe = [str(row['Mots']).strip()] 
        syns = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip() and s.lower() != 'nan']
        groupe_complet = list(set(mots_du_groupe + syns))
        groupes.append(groupe_complet)
        tous_les_mots.update(groupe_complet)
    return groupes, sorted(list(tous_les_mots))

def enregistrer_dans_sheets(nouveau_groupe):
    # --- C'EST ICI QUE ÇA SE PASSE ---
    # On ajoute la permission "drive" pour pouvoir modifier le fichier
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # --------------------------------
    
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(credentials)
    
    # Le reste ne change pas...
    sheet = client.open("Dico Synonymes Creole.").sheet1
    sheet.append_row([nouveau_groupe, ""])

# --- 3. LOGIQUE DE NAVIGATION ---
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""

st.sidebar.title("📖 DES Créole")
page = st.sidebar.radio("Navigation", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE : DICTIONNAIRE ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Recherche")
    groupes, liste_globale = charger_donnees()
    
    col_search, col_reset = st.columns([4, 1])
    with col_reset:
        st.write(" ")
        if st.button("🔄 Effacer", use_container_width=True):
            st.session_state.mot_recherche = ""
            st.rerun()

    with col_search:
        idx = 0
        if st.session_state.mot_recherche in liste_globale:
            idx = liste_globale.index(st.session_state.mot_recherche) + 1
        choix = st.selectbox("Cherchez un mot :", options=[""] + liste_globale, index=idx)

    if choix != st.session_state.mot_recherche:
        st.session_state.mot_recherche = choix
        st.rerun()

    if st.session_state.mot_recherche:
        mot_cible = st.session_state.mot_recherche
        st.markdown(f"### Synonymes pour : **{mot_cible}**")
        synonymes_trouves = set()
        for g in groupes:
            if mot_cible in g:
                for m in g:
                    if m != mot_cible:
                        synonymes_trouves.add(m)
        
        if synonymes_trouves:
            cols = st.columns(5)
            for i, s in enumerate(sorted(list(synonymes_trouves))):
                if cols[i % 5].button(s, key=f"btn_{s}_{i}"):
                    st.session_state.mot_recherche = s
                    st.rerun()

# --- PAGE : ESPACE AUTEURS ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie")
    pwd = st.text_input("Code d'accès :", type="password")
    
    if pwd == "1234":
        st.success("Accès Auteur validé")
        with st.form("form_saisie", clear_on_submit=True):
            nouveau_groupe = st.text_area("Entrez les mots séparés par des virgules :")
            submit = st.form_submit_button("🚀 Enregistrer définitivement")
            
            if submit:
                if len(nouveau_groupe) > 2:
                    try:
                        with st.spinner("Enregistrement en cours..."):
                            enregistrer_dans_sheets(nouveau_groupe)
                        st.success("✅ C'est enregistré dans le Google Sheet !")
                        st.cache_data.clear() # On vide le cache pour voir le mot tout de suite
                    except Exception as e:
                        st.error(f"Erreur de connexion : {e}")
                else:
                    st.warning("Veuillez saisir au moins un mot.")