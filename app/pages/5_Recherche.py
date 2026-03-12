import streamlit as st
import pandas as pd
from utils.db import fetch_all

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.title("🔍 Recherche avancée")

rows = fetch_all("SELECT * FROM formation_inscrits")
df = pd.DataFrame(rows)

if df.empty:
    st.info("Aucun inscrit dans la base.")
    st.stop()

df = df.fillna("")

st.subheader("Rechercher un inscrit")

col1, col2 = st.columns(2)

with col1:
    search_name = st.text_input("Nom contient :")
    search_email = st.text_input("Email contient :")

with col2:
    search_societe = st.text_input("Société contient :")
    search_formation = st.text_input("Intitulé formation contient :")

st.subheader("Filtres")

col3, col4, col5 = st.columns(3)

with col3:
    type_financement = st.selectbox(
        "Type de financement",
        ["Tous", "CPF", "Bourse", "Fond propre", "Alternance responsable", "OPCO & Entreprise"]
    )

with col4:
    mode_paiement = st.selectbox(
        "Mode de paiement",
        ["Tous", "Carte bancaire", "Virement", "Chèque", "Espèces"]
    )

with col5:
    statut = st.selectbox(
        "Statut",
        ["Tous", "en cours d inscription", "inscrit", "désinscrit"]
    )

filtered_df = df.copy()

if search_name:
    filtered_df = filtered_df[filtered_df["nom"].str.contains(search_name, case=False, na=False)]

if search_email:
    filtered_df = filtered_df[filtered_df["email"].str.contains(search_email, case=False, na=False)]

if search_societe:
    filtered_df = filtered_df[filtered_df["societe"].str.contains(search_societe, case=False, na=False)]

if search_formation:
    filtered_df = filtered_df[filtered_df["intitule_formation"].str.contains(search_formation, case=False, na=False)]

if type_financement != "Tous":
    filtered_df = filtered_df[filtered_df["type_financement"] == type_financement]

if mode_paiement != "Tous":
    filtered_df = filtered_df[filtered_df["mode_paiement"] == mode_paiement]

if statut != "Tous":
    filtered_df = filtered_df[filtered_df["statut"] == statut]

st.subheader("Résultats")

if filtered_df.empty:
    st.warning("Aucun résultat trouvé.")
else:
    st.success(f"{len(filtered_df)} résultat(s) trouvé(s).")
    st.dataframe(filtered_df, use_container_width=True)