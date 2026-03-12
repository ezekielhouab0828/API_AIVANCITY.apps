import streamlit as st
import pandas as pd

from utils.db import fetch_all, execute_query, fetch_one
from utils.helpers import is_valid_email, is_valid_phone
from utils.email_sender import send_email

# ---------------------------------------------------------
# Protection
# ---------------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.title("📄 Gestion des inscriptions")

# ---------------------------------------------------------
# Charger les formations
# ---------------------------------------------------------
formations = fetch_all("SELECT id, intitule FROM formations")
liste_formations = ["-------"] + [f["intitule"] for f in formations]

# ---------------------------------------------------------
# Reset automatique du formulaire
# ---------------------------------------------------------
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

if st.session_state.reset_form:
    st.session_state.nom = ""
    st.session_state.prenom = ""
    st.session_state.email = ""
    st.session_state.societe = ""
    st.session_state.intitule_formation = "-------"
    st.session_state.telephone = ""
    st.session_state.reset_form = False

# ---------------------------------------------------------
# Onglets
# ---------------------------------------------------------
onglet1, onglet2 = st.tabs(["📝 Ajouter un inscrit", "🛠️ Gérer les statuts"])

# ---------------------------------------------------------
# ONGLET 1 — FORMULAIRE + TABLEAU
# ---------------------------------------------------------
with onglet1:

    st.subheader("➕ Ajouter une nouvelle formation")

    # Ajouter une formation
    with st.expander("Ajouter une formation"):
        new_formation = st.text_input("Intitulé de la nouvelle formation")

        if st.button("Enregistrer la formation"):
            if not new_formation.strip():
                st.error("Veuillez entrer un intitulé valide.")
            else:
                try:
                    execute_query(
                        "INSERT INTO formations (intitule) VALUES (%s)",
                        (new_formation,)
                    )
                    st.success("Formation ajoutée avec succès.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout : {e}")

    st.subheader("Nouvelle inscription")

    with st.form("form_inscription"):
        nom = st.text_input("Nom", key="nom")
        prenom = st.text_input("Prénom", key="prenom")
        email = st.text_input("Email", key="email")
        societe = st.text_input("Société", key="societe")

        # Formation
        intitule_formation = st.selectbox(
            "Choisir une formation",
            liste_formations,
            key="intitule_formation"
        )

        if intitule_formation == "-------":
            id_formation = None
        else:
            id_formation = next(
                (f["id"] for f in formations if f["intitule"] == intitule_formation),
                None
            )

        # Type de financement
        types_financement = [
            "-------",
            "CPF",
            "Bourse",
            "Fond propre",
            "Alternance responsable",
            "OPCO & Entreprise"
        ]

        type_financement = st.selectbox(
            "Type de financement",
            types_financement
        )

        # Mode de paiement si Fond propre
        mode_paiement = None
        if type_financement == "Fond propre":
            mode_paiement = st.selectbox(
                "Mode de paiement",
                ["Carte bancaire", "Virement", "Chèque", "Espèces"]
            )

        # Téléphone
        indicatifs = {
            "🇫🇷 France (+33)": "+33",
            "🇧🇪 Belgique (+32)": "+32",
            "🇨🇭 Suisse (+41)": "+41",
            "🇨🇦 Canada (+1)": "+1",
            "🇨🇮 Côte d'Ivoire (+225)": "+225",
            "🇨🇬 Congo (+242)": "+242",
            "🇬🇦 Gabon (+241)": "+241"
        }

        indicatif_label = st.selectbox("Indicatif téléphonique", list(indicatifs.keys()))
        indicatif = indicatifs[indicatif_label]

        telephone = st.text_input("Numéro de téléphone (sans indicatif)", key="telephone")

        submit = st.form_submit_button("Inscrire")

    # ---------------------------------------------------------
    # Validation + Enregistrement
    # ---------------------------------------------------------
    if submit:
        if not nom or not prenom or not email or not telephone:
            st.error("Veuillez remplir tous les champs obligatoires.")
        elif intitule_formation == "-------" or id_formation is None:
            st.error("Veuillez sélectionner une formation.")
        elif type_financement == "-------":
            st.error("Veuillez sélectionner un type de financement.")
        elif not is_valid_email(email):
            st.error("Email invalide (.fr ou .com)")
        elif not is_valid_phone(telephone):
            st.error("Téléphone invalide")
        elif type_financement == "Fond propre" and mode_paiement is None:
            st.error("Veuillez sélectionner un mode de paiement.")
        else:
            try:
                execute_query("""
                    INSERT INTO formation_inscrits
                    (id_formation, intitule_formation, nom, prenom, email, telephone, statut,
                     type_financement, societe, session, indicatif, mode_paiement)
                    VALUES (%s, %s, %s, %s, %s, %s, 'en cours d inscription',
                            %s, %s, 'Non définie', %s, %s)
                """, (
                    id_formation, intitule_formation, nom, prenom, email, telephone,
                    type_financement, societe, indicatif, mode_paiement
                ))

                # Email automatique
                template = fetch_one(
                    "SELECT sujet, contenu FROM email_templates WHERE type_email = %s",
                    ("inscription",)
                )

                if template:
                    sujet = template["sujet"]
                    contenu = template["contenu"]
                    contenu = contenu.replace("{{prenom}}", prenom)
                    contenu = contenu.replace("{{formation}}", intitule_formation)

                    try:
                        send_email(email, sujet, contenu)
                    except Exception as e:
                        st.warning(f"Inscription enregistrée, mais erreur lors de l'envoi de l'email : {e}")

                st.success("Inscription enregistrée.")
                st.session_state.reset_form = True
                st.rerun()

            except Exception as e:
                st.error(f"Erreur : {e}")

    # ---------------------------------------------------------
    # Tableau des inscrits
    # ---------------------------------------------------------
    st.subheader("Liste des inscrits")
    rows = fetch_all("SELECT * FROM formation_inscrits")
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("Aucun inscrit pour le moment.")
    else:
        # Afficher indicatif + téléphone
        if "indicatif" in df.columns and "telephone" in df.columns:
            df["telephone"] = df["indicatif"].astype(str) + " " + df["telephone"].astype(str)

        st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# ONGLET 2 — GESTION DES STATUTS
# ---------------------------------------------------------
with onglet2:

    st.subheader("Modifier le statut d'un inscrit")

    rows = fetch_all("SELECT * FROM formation_inscrits")
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("Aucun inscrit.")
        st.stop()

    df["display"] = df["nom"] + " " + df["prenom"] + " — " + df["intitule_formation"]

    selected_display = st.selectbox("Sélectionner un inscrit", df["display"].tolist())

    selected_id = int(df[df["display"] == selected_display]["id"].iloc[0])

    new_status = st.selectbox(
        "Nouveau statut",
        ["en cours d inscription", "inscrit", "désinscrit"]
    )

    if st.button("Mettre à jour le statut"):

        execute_query(
            "UPDATE formation_inscrits SET statut = %s WHERE id = %s",
            (new_status, selected_id)
        )

        if new_status == "inscrit":
            execute_query(
                "UPDATE formation_inscrits SET date_inscription = NOW(), date_desinscription = NULL WHERE id = %s",
                (selected_id,)
            )

        elif new_status == "désinscrit":
            execute_query(
                "UPDATE formation_inscrits SET date_desinscription = NOW() WHERE id = %s",
                (selected_id,)
            )

        elif new_status == "en cours d inscription":
            execute_query(
                "UPDATE formation_inscrits SET date_inscription = NULL, date_desinscription = NULL WHERE id = %s",
                (selected_id,)
            )

        st.success("Statut mis à jour.")
        st.rerun()