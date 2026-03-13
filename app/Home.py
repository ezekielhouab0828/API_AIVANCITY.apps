
import streamlit as st

# Centrer le contenu
st.markdown(
    """
    <style>
    .centered {
        text-align: center;
        padding-top: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="centered">', unsafe_allow_html=True)

st.markdown("## ✨ Bienvenue dans la AIvancity Database")
st.markdown("### Votre espace de gestion des formations, sessions et inscrits")
st.markdown("Veuillez entrer vos identifiants pour accéder à votre tableau de bord.")
st.markdown("---")

# Formulaire de connexion
username = st.text_input("Identifiant")
password = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    st.success("Connexion réussie ! Accedez via la barre laterale")

st.markdown('</div>', unsafe_allow_html=True)
