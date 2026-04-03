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
# --- PAGE 2 : ESPACE AUTEURS (Saisie et Prévisualisation) ---
elif page == "✍️ Espace Auteurs":
    st.title("✍️ Espace de Saisie des Auteurs")
    st.write("Cet outil vous permet de préparer vos fiches avant de les ajouter au dictionnaire.")

    # 1. Sécurité
    pwd = st.text_input("Entrez votre code d'accès :", type="password")
    
    if pwd == "1234":
        st.success("Identification réussie. Vous pouvez saisir un mot.")
        st.write("---")

        # 2. Formulaire de saisie
        with st.form("formulaire_saisie"):
            col_m, col_s = st.columns([1, 2])
            with col_m:
                nouveau_mot = st.text_input("Mot à ajouter :", placeholder="ex: Kozé").strip()
            with col_s:
                nouveaux_syns = st.text_area("Synonymes (séparez par des virgules) :", placeholder="ex: Palé, Diskuté, Bat-la-lang")
            
            # Bouton de validation du formulaire
            bouton_preview = st.form_submit_button("👁️ Prévisualiser la fiche")

        # 3. Logique de Prévisualisation
        if bouton_preview:
            if not nouveau_mot:
                st.error("Veuillez au moins saisir un mot principal.")
            else:
                st.write("### Aperçu du résultat final :")
                st.info("C'est ainsi que les utilisateurs verront votre saisie dans le dictionnaire.")
                
                # Encadré visuel pour la preview
                with st.container(border=True):
                    st.markdown(f"### Synonymes pour : **{nouveau_mot}**")
                    
                    # On nettoie la liste des synonymes
                    if nouveaux_syns:
                        liste_preview = [s.strip() for s in nouveaux_syns.split(',') if s.strip()]
                        
                        if liste_preview:
                            cols = st.columns(5)
                            for i, s in enumerate(liste_preview):
                                cols[i % 5].button(s, key=f"preview_btn_{i}")
                        else:
                            st.warning("Aucun synonyme valide détecté (vérifiez les virgules).")
                    else:
                        st.write("*Aucun synonyme saisi.*")
                
                st.write("---")
                st.warning("⚠️ **Note technique** : Le bouton 'Enregistrer définitivement' sera ajouté dès que nous aurons configuré la connexion sécurisée avec votre Google Sheet.")

    elif pwd != "":
        st.error("Code d'accès incorrect. Veuillez recommencer.")    
