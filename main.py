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

# Menu principal
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
        calories = st.slider("Calories", 0, 5000, 0)
        proteins = st.slider("Protéines (g)", 0, 100, 0)
        carbs = st.slider("Glucides (g)", 0, 100, 0)
        fats = st.slider("Lipides (g)", 0, 100, 0)

        # Upload de plusieurs photos
        uploaded_files = st.file_uploader(
            "Téléchargez une ou plusieurs photos du repas", type=["png", "jpg", "jpeg"], accept_multiple_files=True
        )

        if st.button("Ajouter"):
            user_id = st.session_state["user"]["id"]
            # Insérer les informations du repas
            meal_data = {
                "user_id": user_id,
                "name": name,
                "calories": calories,
                "proteins": proteins,
                "carbs": carbs,
                "fats": fats,
            }
            try:
                meal_response = supabase.table("meals").insert(meal_data).execute()
                if meal_response.data:
                    st.success("Repas ajouté avec succès !")
                    meal_id = meal_response.data[0]["id"]  # Récupérer l'ID du repas
                    photo_urls = []

                    # Upload des photos dans Supabase Storage
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            # Générer un nom de fichier unique avec l'extension correcte
                            file_name = f"meals/{meal_id}_{uuid.uuid4()}.jpg"
                            file_bytes = uploaded_file.read()

                            try:
                                # Upload du fichier
                                storage_response = supabase.storage.from_("photos").upload(file_name, file_bytes)

                                if hasattr(storage_response, "error_message") and storage_response.error_message:
                                    st.error(f"Erreur pour la photo {uploaded_file.name} : {storage_response.error_message}")
                                else:
                                    photo_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"
                                    photo_urls.append(photo_url)
                                    # Insérer l'URL de la photo dans la table meal_photos
                                    supabase.table("meal_photos").insert({"meal_id": meal_id, "photo_url": photo_url}).execute()
                            except Exception as e:
                                st.error(f"Erreur lors de l'upload de la photo {uploaded_file.name} : {str(e)}")

                    if photo_urls:
                        st.success(f"{len(photo_urls)} photo(s) ajoutée(s) avec succès !")
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

        # Récupérer les repas depuis Supabase
        user_id = st.session_state["user"]["id"]
        response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
        meals = response.data

        if not meals or len(meals) == 0:
            st.info("Aucun repas enregistré.")
        else:
            # Créer une liste de dictionnaires pour stocker les données formatées
            formatted_data = []

            for meal in meals:
                # Récupérer les photos associées
                photos_response = supabase.table("meal_photos").select("*").eq("meal_id", meal["id"]).execute()
                photos = photos_response.data

                # Si des photos existent, prendre la première comme miniature
                photo_url = photos[0]["photo_url"] if photos and len(photos) > 0 else None

                # Ajouter les données formatées dans la liste
                formatted_data.append({
                    "Nom": meal["name"],
                    "Calories": meal["calories"],
                    "Protéines (g)": meal["proteins"],
                    "Glucides (g)": meal["carbs"],
                    "Lipides (g)": meal["fats"],
                    "Photo": photo_url  # URL de la photo ou None
                })

            # Display meals in a table with images
            st.write("Liste de vos repas :")

            # Construct an HTML table with images
            table_html = """
            <table style="width:100%; border-collapse: collapse;">
                <thead>
                    <tr style="border: 1px solid black;">
                        <th style="text-align:left; padding: 8px;">Nom</th>
                        <th style="text-align:left; padding: 8px;">Calories</th>
                        <th style="text-align:left; padding: 8px;">Protéines (g)</th>
                        <th style="text-align:left; padding: 8px;">Glucides (g)</th>
                        <th style="text-align:left; padding: 8px;">Lipides (g)</th>
                        <th style="text-align:left; padding: 8px;">Photo</th>
                    </tr>
                </thead>
                <tbody>
            """

            for meal in formatted_data:
                photo_html = f'<img src="{meal["Photo"]}" style="width:50px; height:auto;">' if meal["Photo"] else "Aucune photo"
                table_html += f"""
                    <tr style="border: 1px solid black;">
                        <td style="padding: 8px;">{meal["Nom"]}</td>
                        <td style="padding: 8px;">{meal["Calories"]}</td>
                        <td style="padding: 8px;">{meal["Protéines (g)"]}</td>
                        <td style="padding: 8px;">{meal["Glucides (g)"]}</td>
                        <td style="padding: 8px;">{meal["Lipides (g)"]}</td>
                        <td style="padding: 8px;">{photo_html}</td>
                    </tr>
                """

            table_html += """
                </tbody>
            </table>
            """

            # Use st.markdown to render the HTML table
            st.markdown(table_html, unsafe_allow_html=True)

            # Convertir les données en DataFrame Pandas
            df = pd.DataFrame(formatted_data)

            # Afficher les données dans une colonne avec des miniatures si possible
            st.write("Liste de vos repas :")
            st.dataframe(
                df.style.format({"Photo": lambda x: f'<img src="{x}" style="width:50px;"/>' if x else "Aucune photo"}), unsafe_allow_html=True
            )
