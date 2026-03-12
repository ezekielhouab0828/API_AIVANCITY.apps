import streamlit as st
import pandas as pd
from utils.db import fetch_all, fetch_one, execute_query

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.title("📚 Gestion des formations")

# Charger catégories
categories = fetch_all("SELECT * FROM categories ORDER BY nom ASC")
liste_categories = [c["nom"] for c in categories]

niveaux = ["Débutant", "Intermédiaire", "Avancé", "Expert"]

onglet1, onglet2 = st.tabs(["📥 Formations", "🏷️ Catégories"])

# ---------------------------------------------------------
# ONGLET 1 : FORMATIONS
# ---------------------------------------------------------
with onglet1:
    st.subheader("Ajouter une formation")

    with st.form("form_formation"):
        intitule = st.text_input("Intitulé de la formation")
        categorie = st.selectbox("Catégorie", ["-------"] + liste_categories)
        new_categorie = st.text_input("Ajouter une nouvelle catégorie (optionnel)")
        niveau = st.selectbox("Niveau", ["-------"] + niveaux)
        duree = st.text_input("Durée (ex : 35 heures, 5 jours)")
        prix = st.number_input("Prix (€)", min_value=0.0, step=50.0, format="%.2f")
        description = st.text_area("Description")

        submit_formation = st.form_submit_button("Enregistrer la formation")

    if submit_formation:
        if not intitule.strip():
            st.error("L'intitulé est obligatoire.")
        else:
            try:
                # Ajouter nouvelle catégorie si renseignée
                if new_categorie.strip():
                    execute_query(
                        "INSERT IGNORE INTO categories (nom) VALUES (%s)",
                        (new_categorie.strip(),)
                    )
                    categorie = new_categorie.strip()

                if categorie == "-------":
                    categorie_value = None
                else:
                    categorie_value = categorie

                if niveau == "-------":
                    niveau_value = None
                else:
                    niveau_value = niveau

                execute_query(
                    """
                    INSERT INTO formations (intitule, categorie, niveau, duree, prix, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (intitule, categorie_value, niveau_value, duree, prix, description)
                )
                st.success("Formation enregistrée.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.subheader("Liste des formations")

    rows = fetch_all("SELECT * FROM formations ORDER BY intitule ASC")
    if not rows:
        st.info("Aucune formation enregistrée.")
    else:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        st.subheader("Modifier / Supprimer une formation")

        options = [f"{f['id']} — {f['intitule']}" for f in rows]
        selected = st.selectbox("Sélectionner une formation", options)
        selected_id = int(selected.split(" — ")[0])

        formation = fetch_one("SELECT * FROM formations WHERE id = %s", (selected_id,))

        with st.form("edit_formation"):
            intitule_edit = st.text_input("Intitulé", value=formation["intitule"])
            categorie_edit = st.selectbox(
                "Catégorie",
                ["-------"] + liste_categories,
                index=(["-------"] + liste_categories).index(formation["categorie"])
                if formation["categorie"] in liste_categories else 0
            )
            niveau_edit = st.selectbox(
                "Niveau",
                ["-------"] + niveaux,
                index=(["-------"] + niveaux).index(formation["niveau"])
                if formation["niveau"] in niveaux else 0
            )
            duree_edit = st.text_input("Durée", value=formation["duree"] or "")
            prix_edit = st.number_input(
                "Prix (€)",
                min_value=0.0,
                step=50.0,
                format="%.2f",
                value=float(formation["prix"] or 0.0)
            )
            description_edit = st.text_area("Description", value=formation["description"] or "")

            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("💾 Enregistrer les modifications")
            with col2:
                delete_btn = st.form_submit_button("🗑️ Supprimer la formation")

        if save_btn:
            try:
                cat_val = None if categorie_edit == "-------" else categorie_edit
                niv_val = None if niveau_edit == "-------" else niveau_edit

                execute_query(
                    """
                    UPDATE formations
                    SET intitule = %s, categorie = %s, niveau = %s,
                        duree = %s, prix = %s, description = %s
                    WHERE id = %s
                    """,
                    (intitule_edit, cat_val, niv_val, duree_edit, prix_edit, description_edit, selected_id)
                )
                st.success("Formation mise à jour.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

        if delete_btn:
            try:
                execute_query("DELETE FROM formations WHERE id = %s", (selected_id,))
                st.success("Formation supprimée.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

# ---------------------------------------------------------
# ONGLET 2 : CATEGORIES
# ---------------------------------------------------------
with onglet2:
    st.subheader("Gestion des catégories")

    rows_cat = fetch_all("SELECT * FROM categories ORDER BY nom ASC")
    if not rows_cat:
        st.info("Aucune catégorie.")
    else:
        df_cat = pd.DataFrame(rows_cat)
        st.dataframe(df_cat, use_container_width=True)

    new_cat = st.text_input("Nouvelle catégorie")
    if st.button("Ajouter la catégorie"):
        if not new_cat.strip():
            st.error("Nom invalide.")
        else:
            try:
                execute_query(
                    "INSERT IGNORE INTO categories (nom) VALUES (%s)",
                    (new_cat.strip(),)
                )
                st.success("Catégorie ajoutée.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")