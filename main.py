import os
from supabase import create_client
from dotenv import load_dotenv
import streamlit as st

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connexion à Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Interface utilisateur Streamlit
st.title("Nutrition App")

# Menu
menu = st.sidebar.selectbox("Menu", ["Inscription", "Connexion", "Ajouter un repas", "Voir les repas"])

# Inscription
if menu == "Inscription":
    st.header("Créer un compte")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.get("user"):
            st.success("Inscription réussie !")
        else:
            st.error(f"Erreur : {response.get('error', {}).get('message')}")

# Connexion
if menu == "Connexion":
    st.header("Se connecter")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.get("user"):
            st.success("Connexion réussie !")
            st.session_state["user"] = response["user"]
        else:
            st.error(f"Erreur : {response.get('error', {}).get('message')}")

# Ajouter un repas
if menu == "Ajouter un repas" and "user" in st.session_state:
    st.header("Ajouter un repas")
    name = st.text_input("Nom du repas")
    calories = st.number_input("Calories")
    proteins = st.number_input("Protéines")
    carbs = st.number_input("Glucides")
    fats = st.number_input("Lipides")
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
        response = supabase.table("meals").insert(data).execute()
        if response.get("status_code") == 200:
            st.success("Repas ajouté avec succès !")
        else:
            st.error("Erreur lors de l'ajout du repas.")

# Voir les repas
if menu == "Voir les repas" and "user" in st.session_state:
    st.header("Vos repas")
    user_id = st.session_state["user"]["id"]
    response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
    meals = response.get("data", [])
    if meals:
        for meal in meals:
            st.write(f"Nom : {meal['name']}, Calories : {meal['calories']}")
    else:
        st.info("Aucun repas enregistré.")