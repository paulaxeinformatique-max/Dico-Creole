import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. CHARGEMENT ET PRÉPARATION DES DONNÉES
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees_et_mots():
    df = pd.read_csv(URL_TABLEAU)
    
    # Création de la liste globale (Mots + tous les Synonymes individuels)
    mots_principaux = set(df['Mots'].dropna().unique())
    tous_les_synonymes = set()
    
    for s_row in df['Synonymes'].dropna():
        # On découpe chaque ligne de synonymes par la virgule
        mots_coupes = [m.strip() for m in str(s_row).split(',')]
        tous_les_synonymes.update(mots_coupes)
    
    # Union des deux ensembles pour avoir chaque mot une seule fois
    liste_globale = sorted(list(mots_principaux.union(tous_les_synonymes)))
    return df, liste_globale

# 3. GESTION DE L'ÉTAT
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""

# 4. NAVIGATION
st.sidebar.title("📖 DES Créole")
page = st.sidebar.radio("Navigation", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE 1 : DICTIONNAIRE ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Recherche")
    
    df, liste_mots = charger_donnees_et_mots()

    # Interface de recherche
    col_search, col_reset = st.columns([4, 1])
    
    with col_reset:
        st.write(" ") # Calage
        if st.button("🔄 Effacer", use_container_width=True):
            st.session_state.mot_recherche = ""
            st.rerun()

    with col_search:
        # On trouve l'index du mot stocké dans la session
        index_auto = 0
        if st.session_state.mot_recherche in liste_mots:
            index_auto = liste_mots.index(st.session_state.mot_recherche) + 1

        choix = st.selectbox(
            "Cherchez un mot (entrée ou synonyme) :",
            options=[""] + liste_mots,
            index=index_auto
        )

    # Si le choix change (via la box ou via un bouton de rebond)
    if choix != st.session_state.mot_recherche:
        st.session_state.mot_recherche = choix
        st.rerun()

    # --- AFFICHAGE ---
    if st.session_state.mot_recherche:
        mot_etudie = st.session_state.mot_recherche
        
        # 1. On cherche d'abord si le mot a sa propre fiche (Colonne Mots)
        fiche = df[df['Mots'].str.lower() == mot_etudie.lower()]
        
        if not fiche.empty:
            row = fiche.iloc[0]
            st.markdown(f"### Synonymes pour : **{row['Mots']}**")
            syns = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip()]
            
            cols = st.columns(5)
            for i, s in enumerate(syns):
                if cols[i % 5].button(s, key=f"btn_{s}_{i}"):
                    st.session_state.mot_recherche = s.strip()
                    st.rerun()
        
        # 2. On cherche AUSSI si ce mot apparaît dans les synonymes des autres (Inverse)
        # Cela permet de voir les liens "cachés"
        inverse = df[df['Synonymes'].str.lower().str.contains(rf"\b{mot_etudie.lower()}\b", na=False, regex=True)]
        # On enlève la fiche principale si elle existe déjà dans l'inverse pour éviter les doublons
        if not fiche.empty:
            inverse = inverse[inverse['Mots'].str.lower() != mot_etudie.lower()]
            
        if not inverse.empty:
            st.write("---")
            st.write(f"💡 **'{mot_etudie}'** est aussi cité comme synonyme de :")
            cols_inv = st.columns(5)
            for i, (idx, row_inv) in enumerate(inverse.iterrows()):
                m_inv = row_inv['Mots']
                if cols_inv[i % 5].button(m_inv, key=f"inv_{m_inv}_{i}"):
                    st.session_state.mot_recherche = m_inv
                    st.rerun()

# --- PAGE 2 : ESPACE AUTEURS (Inchangé pour l'instant) ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie")
    pwd = st.text_input("Code d'accès :", type="password")
    if pwd == "1234":
        st.success("Accès autorisé")
        with st.form("ajout"):
            m = st.text_input("Nouveau mot")
            s = st.text_area("Synonymes")
            if st.form_submit_button("Prévisualiser"):
                st.write(f"Aperçu pour **{m}**")
