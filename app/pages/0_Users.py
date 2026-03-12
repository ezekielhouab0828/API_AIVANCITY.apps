
import streamlit as st
from utils.db import fetch_all, execute_query
from utils.auth import create_user

if "role" not in st.session_state or st.session_state.role != "admin":
    st.error("Accès réservé aux administrateurs.")
    st.stop()

st.title("👤 Gestion des utilisateurs")

# ---------------------------------------------------------
# Liste des utilisateurs
# ---------------------------------------------------------
users = fetch_all("SELECT id, username, role FROM users")
st.subheader("Liste des utilisateurs")
st.table(users)

# ---------------------------------------------------------
# Ajouter un utilisateur
# ---------------------------------------------------------
st.subheader("Ajouter un utilisateur")

new_username = st.text_input("Nom d'utilisateur")
new_password = st.text_input("Mot de passe", type="password")
new_role = st.selectbox("Rôle", ["user", "admin"])

if st.button("Créer l'utilisateur"):
    try:
        create_user(new_username, new_password, new_role)
        st.success("Utilisateur créé.")
        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

# ---------------------------------------------------------
# Supprimer un utilisateur
# ---------------------------------------------------------
st.subheader("Supprimer un utilisateur")

user_list = [f"{u['id']} — {u['username']} ({u['role']})" for u in users]
selected_user = st.selectbox("Sélectionner un utilisateur", user_list)

if st.button("Supprimer l'utilisateur"):
    user_id = int(selected_user.split(" — ")[0])
    execute_query("DELETE FROM users WHERE id = %s", (user_id,))
    st.success("Utilisateur supprimé.")
    st.rerun()