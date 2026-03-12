import streamlit as st
import pandas as pd
from utils.db import fetch_all, execute_query

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.title("✉️ Emails automatiques")

execute_query("""
CREATE TABLE IF NOT EXISTS email_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_email VARCHAR(50) UNIQUE,
    sujet VARCHAR(255),
    contenu TEXT
)
""")

templates = fetch_all("SELECT * FROM email_templates")

if not templates:
    st.warning("Aucun modèle d'email trouvé.")
else:
    df_templates = pd.DataFrame(templates)
    st.subheader("📋 Modèles existants")
    st.dataframe(df_templates, use_container_width=True)

st.divider()

st.subheader("➕ Ajouter ou modifier un modèle")

type_email = st.selectbox(
    "Type d'email",
    ["inscription", "validation", "desinscription", "autre"]
)

sujet = st.text_input("Sujet")
contenu = st.text_area("Contenu")

if st.button("Enregistrer"):
    if not sujet or not contenu:
        st.error("Sujet et contenu obligatoires.")
    else:
        existing = fetch_all(
            "SELECT * FROM email_templates WHERE type_email = %s",
            (type_email,)
        )

        if existing:
            execute_query("""
                UPDATE email_templates
                SET sujet = %s, contenu = %s
                WHERE type_email = %s
            """, (sujet, contenu, type_email))
            st.success("Modèle mis à jour.")
        else:
            execute_query("""
                INSERT INTO email_templates (type_email, sujet, contenu)
                VALUES (%s, %s, %s)
            """, (type_email, sujet, contenu))
            st.success("Modèle ajouté.")

        st.rerun()

st.divider()

st.subheader("📨 Envoyer un email automatique")

inscrits = fetch_all("SELECT * FROM formation_inscrits")
df_inscrits = pd.DataFrame(inscrits)

if df_inscrits.empty:
    st.info("Aucun inscrit.")
    st.stop()

email_type = st.selectbox(
    "Type d'email à envoyer",
    ["inscription", "validation", "desinscription"]
)

emails = df_inscrits["email"].tolist()
email_selection = st.multiselect("Destinataires", emails)

if st.button("Envoyer"):
    if not email_selection:
        st.error("Sélectionnez au moins une personne.")
    else:
        template = fetch_all(
            "SELECT * FROM email_templates WHERE type_email = %s",
            (email_type,)
        )

        if not template:
            st.error("Aucun modèle trouvé.")
        else:
            sujet = template[0]["sujet"]
            contenu = template[0]["contenu"]

            for email in email_selection:
                st.success(f"Email envoyé à {email} — Sujet : {sujet}")

            st.info("⚠️ Simulation : aucun email réel n'a été envoyé.")