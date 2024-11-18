import streamlit as st
from supabase import create_client
from io import BytesIO
import uuid
import pandas as pd

# Configurer l'application en mode large
st.set_page_config(layout="wide")

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

# Fonctions utilitaires


def get_user_meals(user_id):
    """Récupère les repas d'un utilisateur."""
    return supabase.table("meals").select("*").eq("user_id", user_id).execute().data


def get_meal_photos(meal_id):
    """Récupère les photos associées à un repas."""
    return supabase.table("meal_photos").select("*").eq("meal_id", meal_id).execute().data


def generate_secure_photo_url(file_name):
    """Génère une URL temporaire sécurisée pour une photo."""
    return supabase.storage.from_("photos").create_signed_url(file_name, 3600).link


# Menu principal
menu = st.sidebar.selectbox(
    "Menu", ["Inscription", "Connexion", "Ajouter un repas", "Voir les repas"]
)

# Inscription
if menu == "Inscription":
    st.header("Créer un compte")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                st.success("Inscription réussie !")
            else:
                st.error(f"Erreur : {response.get('error', {}).get('message', 'Erreur inconnue')}")
        except Exception as e:
            st.error(f"Erreur inattendue : {str(e)}")

# Connexion
if menu == "Connexion":
    st.header("Se connecter")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                st.success("Connexion réussie !")
                st.session_state["user"] = {"id": response.user.id, "email": response.user.email}
            else:
                st.error(f"Erreur : {response.get('error', {}).get('message', 'Erreur inconnue')}")
        except Exception as e:
            st.error(f"Erreur inattendue : {str(e)}")

# Ajouter un repas
if menu == "Ajouter un repas":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour ajouter un repas.")
    else:
        st.header("Ajouter un repas")
        name = st.text_input("Nom du repas")
        calories = st.slider("Calories", 0, 5000, 0)
        proteins = st.slider("Protéines (g)", 0, 100, 0)
        carbs = st.slider("Glucides (g)", 0, 100, 0)
        fats = st.slider("Lipides (g)", 0, 100, 0)

        uploaded_files = st.file_uploader(
            "Téléchargez une ou plusieurs photos du repas", type=["png", "jpg", "jpeg"], accept_multiple_files=True
        )

        if st.button("Ajouter"):
            try:
                user_id = st.session_state["user"]["id"]
                meal_data = {
                    "user_id": user_id,
                    "name": name,
                    "calories": calories,
                    "proteins": proteins,
                    "carbs": carbs,
                    "fats": fats,
                }
                meal_response = supabase.table("meals").insert(meal_data).execute()
                if meal_response.data:
                    meal_id = meal_response.data[0]["id"]
                    for uploaded_file in uploaded_files:
                        file_name = f"meals/{meal_id}_{uuid.uuid4()}.jpg"
                        file_bytes = uploaded_file.read()
                        supabase.storage.from_("photos").upload(file_name, file_bytes)
                        supabase.table("meal_photos").insert(
                            {"meal_id": meal_id, "photo_url": file_name}
                        ).execute()
                    st.success("Repas ajouté avec succès !")
                else:
                    st.error("Erreur lors de l'ajout du repas.")
            except Exception as e:
                st.error(f"Erreur inattendue : {str(e)}")

# Voir les repas
if menu == "Voir les repas":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour voir vos repas.")
    else:
        st.header("Vos repas")
        user_id = st.session_state["user"]["id"]
        meals = get_user_meals(user_id)

        if not meals:
            st.info("Aucun repas enregistré.")
        else:
            for meal in meals:
                st.subheader(meal["name"])
                st.write(f"Calories : {meal['calories']}")
                st.write(f"Protéines : {meal['proteins']} g")
                st.write(f"Glucides : {meal['carbs']} g")
                st.write(f"Lipides : {meal['fats']} g")

                photos = get_meal_photos(meal["id"])
                if photos:
                    for photo in photos:
                        url = generate_secure_photo_url(photo["photo_url"])
                        st.image(url, use_column_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Modifier {meal['id']}"):
                        st.warning("Fonction d'édition à implémenter.")
                with col2:
                    if st.button(f"Supprimer {meal['id']}"):
                        try:
                            supabase.table("meals").delete().eq("id", meal["id"]).execute()
                            st.success("Repas supprimé.")
                        except Exception as e:
                            st.error(f"Erreur lors de la suppression : {str(e)}")
