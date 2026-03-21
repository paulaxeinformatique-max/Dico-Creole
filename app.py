import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Dico Créole Collaboratif", layout="centered")

# --- CONNEXION À GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def charger_donnees():
    return conn.read(ttl="10m") # Cache de 10 minutes pour la rapidité

# --- INTERFACE ---
st.title("📖 Dico Créole Collaboratif")
st.info("Partagez ce lien avec l'association pour travailler ensemble !")

# Mot de passe simple pour protéger les ajouts
access_code = st.sidebar.text_input("Code d'accès membre :", type="password")
AUTHORIZED = (access_code == "creole2024") # Changez ce code !

tab1, tab2, tab3 = st.tabs(["🔍 Rechercher", "➕ Ajouter", "📚 Liste complète"])

df = charger_donnees()

with tab1:
    recherche = st.text_input("Chercher un synonyme :").lower().strip()
    if recherche and not df.empty:
        # Recherche simple dans le tableau
        resultat = df[df['mot'] == recherche]
        if not resultat.empty:
            st.success(f"**Synonymes :** {resultat.iloc[0]['synonymes']}")
        else:
            st.warning("Mot non trouvé.")

with tab2:
    if AUTHORIZED:
        with st.form("ajout"):
            m = st.text_input("Nouveau mot :").lower().strip()
            s = st.text_area("Synonymes (séparés par des virgules) :").lower().strip()
            if st.form_submit_button("Enregistrer"):
                # Ici, on ajoute la logique pour envoyer vers Google Sheets
                new_row = pd.DataFrame({"mot": [m], "synonymes": [s]})
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Enregistré sur Google Sheets !")
                st.balloons()
    else:
        st.warning("Veuillez entrer le code d'accès dans la barre latérale pour ajouter des mots.")

with tab3:
    st.dataframe(df, use_container_width=True)
