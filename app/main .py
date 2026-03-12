import streamlit as st

# 🔐 Protection
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Accès refusé. Veuillez vous connecter.")
    st.stop()

st.set_page_config(page_title="Gestion des formations", layout="wide")

st.title("🏠 Tableau de bord - Gestion des formations")

st.write("Bienvenue dans votre application de gestion. Utilisez le menu à gauche pour naviguer.")

st.markdown("""
### 📌 Sections disponibles

- 📄 **Inscriptions** : ajouter et gérer les inscrits  
- 🔍 **Recherche** : rechercher un inscrit  
- 📊 **Tableau de bord** : statistiques et graphiques  
- 📁 **Importation / Exportation** : importer ou exporter les données  
- 🏫 **Formations** : gérer les formations  
- 🔔 **Relances** : envoyer des relances automatiques  
- ✉️ **Emails** : envoyer des emails personnalisés  
""")