import streamlit as st
from supabase import create_client
from io import BytesIO
import uuid

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
        calories = st.number_input("Calories", min_value=0.0)
        proteins = st.number_input("Protéines", min_value=0.0)
        carbs = st.number_input("Glucides", min_value=0.0)
        fats = st.number_input("Lipides", min_value=0.0)
        
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
                            file_name = f"meals/{meal_id}_{uuid.uuid4()}.jpg"
                            file_bytes = uploaded_file.read()
                            
                            try:
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

if menu == "Voir les repas":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour voir vos repas.")
    else:
        st.header("Vos repas")
        
        # Ajouter des styles CSS pour un design attrayant
        st.markdown(
            """
            <style>
                .meal-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .meal-table th, .meal-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                .meal-table th {
                    background-color: #333;
                    color: #fff;
                    font-weight: bold;
                }
                .meal-table tr:nth-child(even) {
                    background-color: #444;
                }
                .meal-table tr:nth-child(odd) {
                    background-color: #555;
                }
                .meal-table tr:hover {
                    background-color: #666;
                }
                .meal-photo-thumbnail {
                    width: 80px;
                    height: auto;
                    border-radius: 5px;
                    cursor: pointer;
                }
                a {
                    text-decoration: none;
                    color: #fff;
                }
                a:hover {
                    color: #00f;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        # Récupérer les repas depuis Supabase
        user_id = st.session_state["user"]["id"]
        response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
        meals = response.data
        
        # Vérification si des repas existent
        if not meals or len(meals) == 0:
            st.info("Aucun repas enregistré.")
        else:
            # Construire un tableau HTML
            table_html = """
            <table class="meal-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Calories</th>
                        <th>Protéines (g)</th>
                        <th>Glucides (g)</th>
                        <th>Lipides (g)</th>
                        <th>Photos</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for meal in meals:
                # Récupérer les photos associées au repas
                photos_response = supabase.table("meal_photos").select("*").eq("meal_id", meal["id"]).execute()
                photos = photos_response.data
                photo_thumbnails = ""

                # Ajouter des miniatures pour chaque photo
                if photos and len(photos) > 0:
                    for photo in photos:
                        photo_thumbnails += f"""
                        <a href="{photo['photo_url']}" target="_blank">
                            <img class="meal-photo-thumbnail" src="{photo['photo_url']}" alt="Photo de {meal['name']}">
                        </a>
                        """
                else:
                    photo_thumbnails = "Aucune photo"

                # Ajouter une ligne dans le tableau
                table_html += f"""
                <tr>
                    <td>{meal['name']}</td>
                    <td>{meal['calories']}</td>
                    <td>{meal['proteins']}</td>
                    <td>{meal['carbs']}</td>
                    <td>{meal['fats']}</td>
                    <td>{photo_thumbnails}</td>
                </tr>
                """
            
            table_html += "</tbody></table>"
            
            # Afficher le tableau HTML
            st.markdown(table_html, unsafe_allow_html=True)
