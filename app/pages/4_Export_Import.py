import streamlit as st
import pandas as pd
import io
from utils.db import execute_query, fetch_one, fetch_all

st.title("📦 Importation / Exportation des inscrits")

# =========================================================
# 1) TÉLÉCHARGER LE FICHIER CSV MODÈLE
# =========================================================

st.subheader("📥 Télécharger le modèle CSV")

colonnes = [
    "id_formation",
    "id_session",
    "intitule_formation",
    "nom",
    "prenom",
    "email",
    "telephone",
    "statut",
    "type_financement",
    "societe",
    "session",
    "indicatif",
    "mode_paiement"
]

df_template = pd.DataFrame(columns=colonnes)

buffer = io.StringIO()
df_template.to_csv(buffer, index=False)
csv_data = buffer.getvalue()

st.download_button(
    label="📄 Télécharger le fichier CSV modèle",
    data=csv_data,
    file_name="modele_import_inscrits.csv",
    mime="text/csv"
)

st.markdown("---")

# =========================================================
# 2) IMPORTATION AVEC MODE SIMULATION
# =========================================================

st.subheader("📤 Importer un fichier CSV")

uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df_import = pd.read_csv(uploaded_file)

        # Vérification des colonnes
        colonnes_attendues = set(colonnes)
        colonnes_fichier = set(df_import.columns)

        if colonnes_attendues != colonnes_fichier:
            st.error("❌ Le fichier CSV ne correspond pas au modèle attendu.")
            st.write("Colonnes attendues :", colonnes_attendues)
            st.write("Colonnes trouvées :", colonnes_fichier)
            st.stop()

        st.success("✔️ Fichier valide. Simulation prête.")

        # ---------------------------------------------------------
        # MODE SIMULATION
        # ---------------------------------------------------------
        if st.button("🧪 Lancer la simulation"):
            lignes_valides = []
            lignes_invalides = []

            for index, row in df_import.iterrows():
                erreurs_ligne = []

                # 1️⃣ Champs obligatoires
                champs_obligatoires = ["nom", "prenom", "email", "telephone", "id_formation", "type_financement"]
                for champ in champs_obligatoires:
                    if pd.isna(row[champ]) or str(row[champ]).strip() == "":
                        erreurs_ligne.append(f"Champ obligatoire manquant : {champ}")

                # 2️⃣ id_formation existe ?
                formation = fetch_one("SELECT * FROM formations WHERE id = %s", (row["id_formation"],))
                if not formation:
                    erreurs_ligne.append(f"id_formation inexistant : {row['id_formation']}")

                # 3️⃣ id_session appartient à la formation ?
                if not pd.isna(row["id_session"]):
                    session = fetch_one(
                        "SELECT * FROM sessions WHERE id = %s AND id_formation = %s",
                        (row["id_session"], row["id_formation"])
                    )
                    if not session:
                        erreurs_ligne.append("id_session invalide ou n'appartient pas à la formation")

                # Résultat
                if erreurs_ligne:
                    lignes_invalides.append((index + 1, erreurs_ligne))
                else:
                    lignes_valides.append(index + 1)

            # ---------------------------------------------------------
            # AFFICHAGE DES RÉSULTATS
            # ---------------------------------------------------------
            st.subheader("🟢 Lignes valides")
            if lignes_valides:
                st.success(f"{len(lignes_valides)} lignes prêtes à être importées : {lignes_valides}")
            else:
                st.info("Aucune ligne valide.")

            st.subheader("🔴 Lignes invalides")
            if lignes_invalides:
                for num, errs in lignes_invalides:
                    st.error(f"Ligne {num} :")
                    for e in errs:
                        st.write(f"- {e}")
            else:
                st.success("Aucune erreur détectée.")

            # ---------------------------------------------------------
            # IMPORT RÉEL
            # ---------------------------------------------------------
            if lignes_valides and st.button("🚀 Importer réellement les lignes valides"):
                succes = 0
                for index in lignes_valides:
                    row = df_import.iloc[index - 1]

                    try:
                        execute_query("""
                            INSERT INTO formation_inscrits
                            (id_formation, id_session, intitule_formation, nom, prenom, email,
                             telephone, statut, type_financement, societe, session, indicatif, mode_paiement)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row["id_formation"],
                            row["id_session"],
                            row["intitule_formation"],
                            row["nom"],
                            row["prenom"],
                            row["email"],
                            row["telephone"],
                            row["statut"],
                            row["type_financement"],
                            row["societe"],
                            row["session"],
                            row["indicatif"],
                            row["mode_paiement"]
                        ))
                        succes += 1

                    except Exception as e:
                        st.error(f"Erreur SQL ligne {index} : {e}")

                st.success(f"✔️ Importation terminée : {succes} lignes importées avec succès.")

    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

st.markdown("---")

# =========================================================
# 3) EXPORTATION DES INSCRITS (A + B)
# =========================================================

st.subheader("📤 Exportation des inscrits")

# ---------------------------------------------------------
# A) EXPORT COMPLET
# ---------------------------------------------------------

st.markdown("### 🟦 Exporter tous les inscrits")

if st.button("📄 Télécharger tous les inscrits (CSV)"):
    try:
        rows = fetch_all("SELECT * FROM formation_inscrits ORDER BY id DESC")
        if not rows:
            st.warning("Aucun inscrit trouvé.")
        else:
            df = pd.DataFrame(rows)

            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            csv_data = buffer.getvalue()

            st.download_button(
                label="📥 Télécharger le fichier CSV complet",
                data=csv_data,
                file_name="export_inscrits_complet.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Erreur lors de l'export : {e}")

# ---------------------------------------------------------
# B) EXPORT PAR FORMATION
# ---------------------------------------------------------

st.markdown("### 🟩 Exporter les inscrits par formation")

formations = fetch_all("SELECT id, intitule FROM formations ORDER BY intitule ASC")

if not formations:
    st.info("Aucune formation disponible.")
else:
    options_formations = [f"{f['id']} — {f['intitule']}" for f in formations]

    formation_sel = st.selectbox("Choisir une formation", options_formations)

    id_formation = int(formation_sel.split(" — ")[0])
    nom_formation = formation_sel.split(" — ")[1]

    if st.button("📄 Télécharger les inscrits de cette formation"):
        try:
            rows = fetch_all(
                "SELECT * FROM formation_inscrits WHERE id_formation = %s ORDER BY id DESC",
                (id_formation,)
            )

            if not rows:
                st.warning(f"Aucun inscrit trouvé pour la formation : {nom_formation}")
            else:
                df = pd.DataFrame(rows)

                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                csv_data = buffer.getvalue()

                st.download_button(
                    label=f"📥 Télécharger les inscrits — {nom_formation}",
                    data=csv_data,
                    file_name=f"export_inscrits_{nom_formation.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Erreur lors de l'export : {e}")