import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. CHARGEMENT ET FUSION HORIZONTALE
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees_horizontales():
    df = pd.read_csv(URL_TABLEAU)
    
    groupes = []
    tous_les_mots = set()
    
    for _, row in df.iterrows():
        # On fusionne la colonne A et la colonne B dans une seule liste
        mots_du_groupe = [str(row['Mots']).strip()] 
        syns = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip() and s.lower() != 'nan']
        groupe_complet = list(set(mots_du_groupe + syns)) # Nettoyage des doublons
        
        groupes.append(groupe_complet)
        tous_les_mots.update(groupe_complet)
    
    return groupes, sorted(list(tous_les_mots))

# 3. GESTION DE L'ÉTAT
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""

# 4. NAVIGATION
st.sidebar.title("📖 DES Créole")
page = st.sidebar.radio("Navigation", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE 1 : DICTIONNAIRE (MODE HORIZONTAL) ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Recherche Horizontale")
    
    groupes, liste_globale = charger_donnees_horizontales()

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

    # AFFICHAGE DES RÉSULTATS
    if st.session_state.mot_recherche:
        mot_cible = st.session_state.mot_recherche
        st.markdown(f"### Synonymes pour : **{mot_cible}**")
        
        # On cherche tous les synonymes dans TOUS les groupes où le mot apparaît
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

# --- PAGE 2 : ESPACE AUTEURS (CONFORME À TA VISION) ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie")
    pwd = st.text_input("Code d'accès :", type="password")
    
    if pwd == "1234":
        st.success("Mode Édition activé")
        st.markdown("""> **Note aux auteurs :** Ne vous souciez plus de l'ordre. 
        Mettez tous les mots d'un même sens sur la même ligne.""")
        
        with st.form("saisie_horizontale"):
            groupe_mots = st.text_area("Saisissez votre groupe de synonymes (séparés par des virgules) :", 
                                       placeholder="ex: Kozé, Palé, Diskuté, Bat-la-lang")
            
            if st.form_submit_button("👁️ Prévisualiser le groupe"):
                mots_liste = [m.strip() for m in groupe_mots.split(',') if m.strip()]
                if mots_liste:
                    st.write("Chaque mot ci-dessous renverra vers tous les autres :")
                    cols = st.columns(5)
                    for i, m in enumerate(mots_liste):
                        cols[i % 5].button(m, key=f"prev_{m}_{i}")
                else:
                    st.error("Veuillez saisir au moins deux mots.")   
