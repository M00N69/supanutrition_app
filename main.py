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

# Interface utilisateur Streamlit
st.title("Nutrition App")

# Initialisation de l'état de session pour l'utilisateur
if "user" not in st.session_state:
    st.session_state["user"] = None


def get_user_meals(user_id):
    """Récupère les repas d'un utilisateur."""
    response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
    return response.data if response else []


def get_meal_photos(meal_id):
    """Récupère les photos associées à un repas."""
    response = supabase.table("meal_photos").select("*").eq("meal_id", meal_id).execute()
    return response.data if response else []


def generate_secure_photo_url(file_name):
    """Génère une URL temporaire sécurisée pour une photo."""
    try:
        response = supabase.storage.from_("photos").create_signed_url(file_name, 3600)
        return response.link
    except Exception as e:
        st.error(f"Erreur lors de la génération de l'URL sécurisée pour {file_name}: {str(e)}")
        return None


# Menu principal
menu = st.sidebar.selectbox(
    "Menu", ["Inscription", "Connexion", "Ajouter un repas", "Voir les repas"]
)

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
            # Préparer les données pour le DataFrame
            meal_data = []
            for meal in meals:
                photos = get_meal_photos(meal["id"])
                preview_url = None
                if photos:
                    preview_url = generate_secure_photo_url(photos[0]["photo_url"])
                meal_data.append(
                    {
                        "Nom": meal["name"],
                        "Calories": meal["calories"],
                        "Protéines": meal["proteins"],
                        "Glucides": meal["carbs"],
                        "Lipides": meal["fats"],
                        "Aperçu": preview_url,
                        "Progression": meal["calories"] / 5000,  # Exemple d'une progression
                    }
                )

            # Convertir en DataFrame
            df = pd.DataFrame(meal_data)

            # Configurer les colonnes personnalisées
            st.data_editor(
                df,
                column_config={
                    "Aperçu": st.column_config.ImageColumn("Aperçu", use_container_width=True),
                    "Progression": st.column_config.ProgressColumn(
                        "Progression",
                        format="{:.0%}",
                        use_container_width=True,
                    ),
                    "Nom": "Nom du repas",
                    "Calories": "Calories",
                    "Protéines": "Protéines (g)",
                    "Glucides": "Glucides (g)",
                    "Lipides": "Lipides (g)",
                },
                hide_index=True,
            )
