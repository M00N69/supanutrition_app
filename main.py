import streamlit as st
from supabase import create_client
import pandas as pd

# Streamlit page configuration
st.set_page_config(layout="wide")

# Load secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ensure user is authenticated
if "user" not in st.session_state:
    st.session_state["user"] = None

menu = st.sidebar.selectbox("Menu", ["Connexion", "Voir les repas"])

if menu == "Connexion":
    st.header("Connexion")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            st.session_state["user"] = {"id": response.user.id, "email": response.user.email}
            st.success("Connexion réussie !")
        else:
            st.error("Erreur lors de la connexion.")

if menu == "Voir les repas" and st.session_state["user"]:
    st.header("Vos repas")

    # Fetch meals from Supabase
    user_id = st.session_state["user"]["id"]
    response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
    meals = response.data

    if not meals:
        st.info("Aucun repas trouvé.")
    else:
        formatted_data = []

        for meal in meals:
            # Fetch associated photos
            photos_response = supabase.table("meal_photos").select("*").eq("meal_id", meal["id"]).execute()
            photos = photos_response.data

            # Use the first photo URL if available
            photo_url = photos[0]["photo_url"] if photos and len(photos) > 0 else None

            formatted_data.append({
                "Nom": meal["name"],
                "Calories": meal["calories"],
                "Protéines (g)": meal["proteins"],
                "Glucides (g)": meal["carbs"],
                "Lipides (g)": meal["fats"],
                "Photo": photo_url,  # URL for previewing images
            })

        # Convert data to DataFrame
        df = pd.DataFrame(formatted_data)

        # Use st.dataframe with custom column config
        st.dataframe(
            df,
            column_config={
                "Photo": st.column_config.ImageColumn(
                    "Preview",
                    use_container_width=True,
                ),
                "Calories": st.column_config.ProgressColumn(
                    "Calories",
                    min_value=0,
                    max_value=5000,
                    format="%d",
                ),
                "Protéines (g)": st.column_config.ProgressColumn(
                    "Protéines (g)",
                    min_value=0,
                    max_value=100,
                    format="%d",
                ),
                "Glucides (g)": st.column_config.ProgressColumn(
                    "Glucides (g)",
                    min_value=0,
                    max_value=100,
                    format="%d",
                ),
                "Lipides (g)": st.column_config.ProgressColumn(
                    "Lipides (g)",
                    min_value=0,
                    max_value=100,
                    format="%d",
                ),
            },
            use_container_width=True,
        )
