import streamlit as st
from supabase import create_client

# Charger les secrets de Streamlit Cloud
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Connexion à Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Interface utilisateur Streamlit
st.title("Nutrition App")

# Initialisation de l'état de session pour l'utilisateur
if "user" not in st.session_state:
    st.session_state["user"] = None

# Menu
menu = st.sidebar.selectbox("Menu", ["Inscription", "Connexion", "Ajouter un repas", "Voir les repas"])

# Inscription
if menu == "Inscription":
    st.header("Créer un compte")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Inscription réussie !")
        else:
            st.error(f"Erreur : {response.get('error', {}).get('message', 'Erreur inconnue')}")

# Connexion
if menu == "Connexion":
    st.header("Se connecter")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            st.success("Connexion réussie !")
            st.session_state["user"] = {"id": response.user.id, "email": response.user.email}
        else:
            st.error(f"Erreur : {response.get('error', {}).get('message', 'Erreur inconnue')}")

# Ajouter un repas
if menu == "Ajouter un repas":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour ajouter un repas.")
    else:
        st.header("Ajouter un repas")
        name = st.text_input("Nom du repas")
        calories = st.number_input("Calories", min_value=0.0)
        proteins = st.number_input("Protéines", min_value=0.0)
        carbs = st.number_input("Glucides", min_value=0.0)
        fats = st.number_input("Lipides", min_value=0.0)
        if st.button("Ajouter"):
            user_id = st.session_state["user"]["id"]
            data = {
                "user_id": user_id,
                "name": name,
                "calories": calories,
                "proteins": proteins,
                "carbs": carbs,
                "fats": fats,
            }
            
            # Debug des données envoyées
            st.write("Données envoyées à Supabase:", data)
            
            try:
                # Tentative d'insertion des données dans Supabase
                response = supabase.table("meals").insert(data).execute()

                # Vérification si l'insertion a réussi
                if response.data:  # Si des données sont retournées, l'insertion a réussi
                    st.success("Repas ajouté avec succès !")
                    st.write("Réponse de Supabase :", response.data)
                else:  # En cas d'échec, on affiche un message d'erreur
                    st.error("Erreur lors de l'ajout du repas. Vérifiez vos permissions ou vos données.")
            except Exception as e:
                # Gestion des exceptions inattendues
                st.error(f"Erreur inattendue : {str(e)}")

# Voir les repas
if menu == "Voir les repas":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour voir vos repas.")
    else:
        st.header("Vos repas")
        user_id = st.session_state["user"]["id"]
        response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
        meals = response.data
        if meals:
            for meal in meals:
                st.write(f"Nom : {meal['name']}, Calories : {meal['calories']}, Protéines : {meal['proteins']}, Glucides : {meal['carbs']}, Lipides : {meal['fats']}")
        else:
            st.info("Aucun repas enregistré.")
