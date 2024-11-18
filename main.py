import streamlit as st
from supabase import create_client
import pandas as pd
import uuid

# Configurer l'application en mode large
st.set_page_config(layout="wide")

# Charger les secrets de Streamlit Cloud
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Connexion à Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialisation de l'état de session pour l'utilisateur
if "user" not in st.session_state:
    st.session_state["user"] = None

# Fonctions utilitaires
def get_user_meals(user_id):
    """Récupère les repas d'un utilisateur."""
    response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
    return response.data if response else []


def get_meal_photos(meal_id):
    """Récupère les photos associées à un repas."""
    response = supabase.table("meal_photos").select("*").eq("meal_id", meal_id).execute()
    return response.data if response else []


# Interface utilisateur
def show_welcome_message():
    """Affiche un message de bienvenue pour l'utilisateur connecté."""
    user = st.session_state["user"]
    if user:
        st.markdown(f"### Bonjour, **{user['email']}** ! Passez une excellente journée.")
    else:
        st.markdown("### Bienvenue sur l'application Nutrition App !")


# Menu principal
menu = st.sidebar.selectbox(
    "Menu", ["Inscription", "Connexion", "Mon Profil", "Ajouter un repas", "Voir les repas"]
)

show_welcome_message()

if menu == "Inscription":
    st.header("Créer un compte")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            if response.user:
                st.success("Inscription réussie ! Un email de vérification a été envoyé.")
            elif response.error:
                st.error(f"Erreur : {response.error['message']}")
            else:
                st.error("Une erreur inconnue s'est produite.")
        except Exception as e:
            st.error(f"Erreur inattendue : {str(e)}")

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

if menu == "Mon Profil":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour accéder à votre profil.")
    else:
        user = st.session_state["user"]
        st.header("Votre Profil")
        st.markdown(f"**Email** : {user['email']}")
        if st.button("Déconnexion"):
            st.session_state["user"] = None
            st.success("Vous avez été déconnecté.")

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
                            {"meal_id": meal_id, "photo_url": f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"}
                        ).execute()
                    st.success("Repas ajouté avec succès !")
                else:
                    st.error("Erreur lors de l'ajout du repas.")
            except Exception as e:
                st.error(f"Erreur inattendue : {str(e)}")

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
            df = pd.DataFrame(meals)
            df = df[["name", "calories", "proteins", "carbs", "fats"]]  # Sélectionner les colonnes pertinentes
            st.dataframe(df)

            for meal in meals:
                photos = get_meal_photos(meal["id"])
                if photos:
                    st.image(photos[0]["photo_url"], use_column_width=True)
                st.markdown("---")
