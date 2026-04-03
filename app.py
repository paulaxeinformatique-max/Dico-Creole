import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="DES Créole", page_icon="📖", layout="wide")

# 2. CHARGEMENT DES DONNÉES
URL_TABLEAU = "https://docs.google.com/spreadsheets/d/1x-WOFCIfgPcbH1oHiHBMJxNZ1jyQwtV2rOPxL8SStsw/export?format=csv"

@st.cache_data(ttl=60)
def charger_donnees():
    try:
        return pd.read_csv(URL_TABLEAU)
    except:
        return pd.DataFrame(columns=['Mots', 'Synonymes'])

# 3. GESTION DE L'ÉTAT (Session State)
if 'mot_recherche' not in st.session_state:
    st.session_state.mot_recherche = ""

# 4. NAVIGATION LATERALE
st.sidebar.title("📖 DES Créole")
page = st.sidebar.radio("Navigation", ["🔎 Dictionnaire", "✍️ Espace Auteurs"])

# --- PAGE 1 : DICTIONNAIRE ---
if page == "🔎 Dictionnaire":
    st.title("🔎 Recherche")
    
    df = charger_donnees()
    # Liste alphabétique des mots (Colonne A)
    liste_mots = sorted(df['Mots'].dropna().unique().tolist())

    # Barre de commande : Recherche + Reset
    col_search, col_reset = st.columns([4, 1])
    
    with col_reset:
        st.write(" ") # Alignement
        if st.button("🔄 Effacer", use_container_width=True):
            st.session_state.mot_recherche = ""
            st.rerun()

    with col_search:
        # On calcule l'index pour que la box suive le bouton cliqué
        index_auto = 0
        if st.session_state.mot_recherche in liste_mots:
            index_auto = liste_mots.index(st.session_state.mot_recherche) + 1

        choix = st.selectbox(
            "Tapez pour filtrer les mots :",
            options=[""] + liste_mots,
            index=index_auto
        )

    # Si le choix change manuellement dans la liste
    if choix != st.session_state.mot_recherche:
        st.session_state.mot_recherche = choix
        st.rerun()

    # Affichage des résultats
    if st.session_state.mot_recherche:
        mot_etudie = st.session_state.mot_recherche
        
        # On cherche la ligne correspondante
        mask = (df['Mots'].str.lower() == mot_etudie.lower())
        resultat = df[mask]
        
        if not resultat.empty:
            row = resultat.iloc[0]
            st.markdown(f"### Synonymes pour : **{row['Mots']}**")
            st.write("---")
            
            syns = [s.strip() for s in str(row['Synonymes']).split(',') if s.strip()]
            
            if syns:
                cols = st.columns(5)
                for i, s in enumerate(syns):
                    # Chaque bouton met à jour le mot_recherche
                    if cols[i % 5].button(s, key=f"btn_{s}_{i}"):
                        st.session_state.mot_recherche = s.strip()
                        st.rerun()
            else:
                st.info("Aucun synonyme listé pour ce mot.")
        else:
            # Si le mot n'est pas en colonne A mais existe dans les synonymes d'un autre
            st.warning(f"Le mot '{mot_etudie}' est mentionné comme synonyme mais n'a pas encore sa propre fiche.")

# --- PAGE 2 : ESPACE AUTEURS ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie")
    
    pwd = st.text_input("Code d'accès :", type="password")
    
    if pwd == "1234":
        st.success("Accès autorisé")
        st.write("---")
        
        with st.form("nouveau_mot_form"):
            st.subheader("Nouvelle entrée")
            mot_saisi = st.text_input("Mot principal")
            syns_saisis = st.text_area("Synonymes (séparés par des virgules)")
            
            envoi = st.form_submit_button("Prévisualiser l'affichage")
            
            if envoi:
                st.info("Aperçu de ce que verront les utilisateurs :")
                st.markdown(f"### Synonymes pour : **{mot_saisi}**")
                s_list = [x.strip() for x in syns_saisis.split(',')]
                c = st.columns(5)
                for i, s in enumerate(s_list):
                    c[i % 5].button(s, key=f"prev_{i}")
                
                st.warning("ℹ️ Note : Le bouton 'Enregistrer' sera activé après la configuration de la sécurité Google.")
    elif pwd != "":
        st.error("Code incorrect")
