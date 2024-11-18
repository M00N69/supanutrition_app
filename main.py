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


# Fonctions utilitaires
def get_user_meals(user_id):
    """Récupère les repas d'un utilisateur."""
    response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
    return response.data if response else []


def get_meal_photos(meal_id):
    """Récupère les photos associées à un repas."""
    response = supabase.table("meal_photos").select("*").eq("meal_id", meal_id).execute()
    return response.data if response else []


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
                            {"meal_id": meal_id, "photo_url": f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"}
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
            # Préparer les données pour le DataFrame
            meal_data = []
            for meal in meals:
                photos = get_meal_photos(meal["id"])
                preview_url = photos[0]["photo_url"] if photos else None  # Utilise directement l'URL

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
