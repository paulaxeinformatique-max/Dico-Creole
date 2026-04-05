import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# --- 2. CONNEXION ET CHARGEMENT ---
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees():
    try:
        df = pd.read_csv(URL_TABLEAU)
        groupes = []
        tous_les_mots = set()
        
        for _, row in df.iterrows():
            # Découpage et nettoyage des colonnes A et B
            mots_a = [m.strip() for m in str(row['Mots']).split(',') if m.strip() and str(m).lower() != 'nan']
            mots_b = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip() and str(s).lower() != 'nan']
            
            groupe_complet = list(set(mots_a + mots_b))
            if groupe_complet:
                groupes.append(groupe_complet)
                tous_les_mots.update(groupe_complet)
        return groupes, sorted(list(tous_les_mots))
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return [], []

def enregistrer_dans_sheets(nouveau_groupe):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(credentials)
    
    # Ouverture du tableau (Nom exact requis)
    sheet = client.open("Dico Synonymes Creole.").sheet1
    sheet.append_row([nouveau_groupe])

# --- 3. GESTION DE L'ÉTAT ET NAVIGATION ---
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""

st.sidebar.title("📖 Menu Principal")
page = st.sidebar.radio("Navigation", ["🔎 Recherche", "📖 Le Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE 1 : RECHERCHE ---
if page == "🔎 Recherche":
    st.title("🔎 Trouver un synonyme")
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
        choix = st.selectbox("Tapez un mot :", options=[""] + liste_globale, index=idx)

    if choix != st.session_state.mot_recherche:
        st.session_state.mot_recherche = choix
        st.rerun()

    if st.session_state.mot_recherche:
        mot_cible = st.session_state.mot_recherche
        st.subheader(f"Synonymes pour : {mot_cible}")
        
        synonymes_trouves = set()
        for g in groupes:
            if mot_cible in g:
                synonymes_trouves.update([m for m in g if m != mot_cible])
        
        if synonymes_trouves:
            cols = st.columns(5)
            for i, s in enumerate(sorted(list(synonymes_trouves))):
                if cols[i % 5].button(s, key=f"btn_{s}_{i}"):
                    st.session_state.mot_recherche = s
                    st.rerun()
        else:
            st.info("Aucun synonyme répertorié pour ce mot.")

# --- PAGE 2 : LE DICTIONNAIRE COMPLET (LA NOUVEAUTÉ) ---
elif page == "📖 Le Dictionnaire":
    st.title("📖 Liste Alphabétique")
    groupes, liste_globale = charger_donnees()
    
    if not liste_globale:
        st.info("Le dictionnaire est en cours de création...")
    else:
        # Index alphabétique
        lettres = sorted(list(set([m[0].upper() for m in liste_globale])))
        choix_lettre = st.pills("Choisir une lettre :", lettres, selection_mode="single", default=lettres[0])

        st.markdown("---")
        
        # Filtrer et afficher les mots
        for mot in liste_globale:
            if mot.upper().startswith(choix_lettre):
                # Trouver ses synonymes pour l'affichage
                ses_syns = set()
                for g in groupes:
                    if mot in g:
                        ses_syns.update([m for m in g if m != mot])
                
                # Mise en page : Mot à gauche, Synonymes à droite
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.markdown(f"**{mot}**")
                with c2:
                    if ses_syns:
                        st.write(f"👉 {', '.join(sorted(list(ses_syns)))}")
                    else:
                        st.write("*(Seul)*")
                st.divider()

# --- PAGE 3 : ESPACE AUTEURS ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Saisie de nouveaux mots")
    pwd = st.text_input("Code secret :", type="password")
    
    if pwd == "1234":
        st.success("Accès autorisé")
        with st.form("form_saisie", clear_on_submit=True):
            nouveaux_mots = st.text_area("Entrez vos synonymes (ex: Mot1, Mot2, Mot3) :")
            submit = st.form_submit_button("🚀 Enregistrer dans la base")
            
            if submit:
                if len(nouveaux_mots) > 2:
                    try:
                        with st.spinner("Enregistrement..."):
                            enregistrer_dans_sheets(nouveaux_mots)
                        st.success("C'est enregistré !")
                        st.cache_data.clear() 
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                else:
                    st.warning("Texte trop court.")
    elif pwd != "":
        st.error("Code incorrect")