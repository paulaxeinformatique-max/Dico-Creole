import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# --- 2. CONNEXION ET CHARGEMENT ---
# URL de lecture seule (CSV) pour la rapidité
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees():
    df = pd.read_csv(URL_TABLEAU)
    groupes = []
    tous_les_mots = set()
    
    for _, row in df.iterrows():
        # On nettoie et on découpe les colonnes A et B par les virgules
        mots_a = [m.strip() for m in str(row['Mots']).split(',') if m.strip() and str(m).lower() != 'nan']
        mots_b = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip() and str(s).lower() != 'nan']
        
        # On fusionne tout dans un seul groupe "horizontal"
        groupe_complet = list(set(mots_a + mots_b))
        
        if groupe_complet:
            groupes.append(groupe_complet)
            tous_les_mots.update(groupe_complet)
            
    return groupes, sorted(list(tous_les_mots))

def enregistrer_dans_sheets(nouveau_groupe):
    # Scopes étendus pour éviter l'erreur 403
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(credentials)
    
    # OUVERTURE DU TABLEAU
    # /!\ Vérifie que le nom est EXACTEMENT "Dico Synonymes Creole." (avec le point)
    sheet = client.open("Dico Synonymes Creole.").sheet1
    sheet.append_row([nouveau_groupe]) 

# --- 3. NAVIGATION ---
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""

st.sidebar.title("📖 DES Créole")
page = st.sidebar.radio("Navigation", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE 1 : DICTIONNAIRE ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Recherche")
    
    with st.spinner("Mise à jour du dictionnaire..."):
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
        
        choix = st.selectbox(
            "Cherchez un mot (il sera trouvé même s'il est au milieu d'une liste) :", 
            options=[""] + liste_globale, 
            index=idx
        )

    if choix != st.session_state.mot_recherche:
        st.session_state.mot_recherche = choix
        st.rerun()

    if st.session_state.mot_recherche:
        mot_cible = st.session_state.mot_recherche
        st.markdown(f"### Synonymes pour : **{mot_cible}**")
        
        # Trouver tous les mots qui partagent le même groupe que le mot cible
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
        else:
            st.info("Ce mot est seul dans son groupe pour le moment.")

# --- PAGE 2 : ESPACE AUTEURS ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie")
    st.info("Les mots saisis ici apparaîtront immédiatement dans le dictionnaire.")
    
    pwd = st.text_input("Code d'accès :", type="password")
    
    if pwd == "1234":
        st.success("Accès Auteur validé")
        
        with st.form("form_saisie", clear_on_submit=True):
            st.write("Saisissez un groupe de mots synonymes :")
            nouveau_groupe = st.text_area("Exemple : Kozé, Palé, Diskuté", help="Séparez les mots par des virgules.")
            
            submit = st.form_submit_button("🚀 Enregistrer définitivement")
            
            if submit:
                if len(nouveau_groupe) > 2:
                    try:
                        with st.spinner("Connexion à Google Sheets..."):
                            enregistrer_dans_sheets(nouveau_groupe)
                        st.success(f"✅ Ajouté avec succès : {nouveau_groupe}")
                        st.cache_data.clear() # On force le dictionnaire à se recharger
                    except Exception as e:
                        st.error(f"Erreur de connexion : {e}")
                else:
                    st.warning("Veuillez saisir au moins un mot.")
    elif pwd != "":
        st.error("Code incorrect")