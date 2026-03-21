import streamlit as st

st.set_page_config(page_title="Dico Créole", page_icon="📖")

st.title("📖 Dictionnaire des Synonymes")
st.subheader("Association des Écrivains - Démo")

# On met quelques mots directement dans le code pour la démo
dico_demo = {
    "kozer": "parler, discuter, échanger",
    "zoli": "beau, joli, magnifique",
    "manzer": "manger, prendre un repas",
    "la kour": "le jardin, la cour"
}

recherche = st.text_input("Chercher un mot (ex: kozer, zoli) :").lower().strip()

if recherche:
    if recherche in dico_demo:
        st.success(f"**Synonymes :** {dico_demo[recherche]}")
    else:
        st.warning("Mot non trouvé dans cette version de démonstration.")

st.divider()
st.info("💡 Cet après-midi, nous testons l'outil. La version finale permettra à chaque écrivain d'ajouter des mots en temps réel.")
