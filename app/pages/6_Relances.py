import streamlit as st
import pandas as pd
from utils.db import fetch_all, execute_query

# ---------------------------------------------------------
# 🔐 Protection : accès réservé aux utilisateurs connectés
# ---------------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.title("🎓 Gestion des formations")

# ---------------------------------------------------------
# 🗂️ Création automatique de la table si elle n'existe pas
# ---------------------------------------------------------
execute_query("""
CREATE TABLE IF NOT EXISTS formations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    intitule VARCHAR(255) UNIQUE,
    description TEXT,
    duree VARCHAR(100),
    prix VARCHAR(100)
)
""")

# ---------------------------------------------------------
# ➕ AJOUTER UNE FORMATION
# ---------------------------------------------------------
st.subheader("➕ Ajouter une nouvelle formation")

with st.form("add_formation"):
    intitule = st.text_input("Intitulé de la formation")
    description = st.text_area("Description")
    duree = st.text_input("Durée (ex : 3 mois, 120h...)")
    prix = st.text_input("Prix (ex : 1500€, 2500€...)")

    submit = st.form_submit_button("Ajouter")

if submit:
    if not intitule:
        st.error("L'intitulé est obligatoire.")
    else:
        try:
            execute_query("""
                INSERT INTO formations (intitule, description, duree, prix)
                VALUES (%s, %s, %s, %s)
            """, (intitule, description, duree, prix))

            st.success("Formation ajoutée avec succès.")
            st.rerun()  # 🔄 nouvelle version correcte

        except Exception as e:
            st.error(f"Erreur : {e}")

st.divider()

# ---------------------------------------------------------
# 📋 LISTE DES FORMATIONS
# ---------------------------------------------------------
st.subheader("📋 Liste des formations")

formations = fetch_all("SELECT * FROM formations ORDER BY id DESC")
df = pd.DataFrame(formations)

if df.empty:
    st.info("Aucune formation enregistrée.")
else:
    st.dataframe(df, use_container_width=True)

    # ---------------------------------------------------------
    # 🗑️ SUPPRESSION D'UNE FORMATION
    # ---------------------------------------------------------
    st.subheader("🗑️ Supprimer une formation")

    ids = df["id"].tolist()
    choix = st.selectbox("Sélectionner une formation à supprimer", ids)

    if st.button("Supprimer"):
        execute_query("DELETE FROM formations WHERE id = %s", (choix,))
        st.success("Formation supprimée.")
        st.rerun()  # 🔄 rafraîchissement propre