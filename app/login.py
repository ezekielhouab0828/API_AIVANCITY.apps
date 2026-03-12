import streamlit as st
from utils.auth import verify_user

st.set_page_config(page_title="Connexion", layout="centered")

# ============================
# MESSAGE DE BIENVENUE
# ============================

st.markdown(
    """
    <style>
    .login-container {
        text-align: center;
        padding-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="login-container">', unsafe_allow_html=True)

st.markdown("## ✨ Bienvenue dans la Ezekiel Database")
st.markdown("### Votre espace de gestion des formations, sessions, inscrits, etc.")
st.markdown("Veuillez entrer vos identifiants pour accéder à votre tableau de bord.")
st.markdown("---")

# ============================
# FORMULAIRE DE CONNEXION
# ============================

# Le formulaire permet de valider avec la touche Entrée
with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    # Le bouton du formulaire déclenche aussi la validation avec Entrée
    submitted = st.form_submit_button("Se connecter")

# ============================
# TRAITEMENT DE LA CONNEXION
# ============================

if submitted:
    user = verify_user(username, password)

    if user:
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]

        st.success("Connexion réussie.")

        # Redirection automatique vers la page Inscriptions
        st.switch_page("pages/1_Inscriptions.py")

    else:
        st.error("Identifiants incorrects.")

st.markdown('</div>', unsafe_allow_html=True)