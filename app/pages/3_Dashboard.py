import streamlit as st
import pandas as pd
from utils.db import fetch_all
import plotly.express as px

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.title("📊 Dashboard des inscriptions")

rows = fetch_all("SELECT * FROM formation_inscrits")
df = pd.DataFrame(rows)

if df.empty:
    st.info("Aucune donnée disponible.")
    st.stop()

df = df.fillna("")

st.subheader("📌 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total inscrits", len(df))

with col2:
    st.metric("En cours", len(df[df["statut"] == "en cours d inscription"]))

with col3:
    st.metric("Inscrits validés", len(df[df["statut"] == "inscrit"]))

with col4:
    st.metric("Désinscrits", len(df[df["statut"] == "désinscrit"]))

st.divider()

st.subheader("📌 Répartition par statut")

fig_statut = px.pie(df, names="statut", title="Répartition des statuts")
st.plotly_chart(fig_statut, use_container_width=True)

st.divider()

st.subheader("📌 Répartition par type de financement")

df_fin = df.groupby("type_financement").size().reset_index(name="count")

fig_fin = px.bar(df_fin, x="type_financement", y="count", title="Par type de financement")
st.plotly_chart(fig_fin, use_container_width=True)

st.divider()

st.subheader("📌 Répartition par formation")

df_form = df.groupby("intitule_formation").size().reset_index(name="count")

fig_form = px.bar(df_form, x="intitule_formation", y="count", title="Par formation")
st.plotly_chart(fig_form, use_container_width=True)

st.divider()

st.subheader("📌 Répartition par société")

df_soc = df.groupby("societe").size().reset_index(name="count")

fig_soc = px.bar(df_soc, x="societe", y="count", title="Par société")
st.plotly_chart(fig_soc, use_container_width=True)