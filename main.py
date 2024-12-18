import streamlit as st
from supabase import create_client
import pandas as pd
import uuid
from datetime import datetime
import matplotlib.pyplot as plt
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import requests
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

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

# Fonction utilitaire pour enregistrer un entraînement
def add_training(user_id, training_type, date, duration, calories_burned):
    """Ajoute un entraînement pour un utilisateur."""
    # Convertir la date en format ISO (YYYY-MM-DD)
    date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)

    response = supabase.table("trainings").insert({
        "user_id": user_id,
        "training_type": training_type,
        "date": date_str,  # Utilisation de la date convertie
        "duration": duration,
        "calories_burned": calories_burned,
    }).execute()
    return response

# Fonction utilitaire pour récupérer les entraînements d'un utilisateur
def get_user_trainings(user_id):
    """Récupère les entraînements d'un utilisateur."""
    response = supabase.table("trainings").select("*").eq("user_id", user_id).execute()
    return response.data if response else []

# Interface utilisateur
def show_welcome_message():
    """Affiche un message de bienvenue pour l'utilisateur connecté."""
    user = st.session_state["user"]
    if user:
        st.markdown(f"### Bienvenue, **{user['email']}** sur l'Appapoute ! ")
    else:
        st.markdown("### Bienvenue sur l'application Nutrition App !")
# Fonction pour ajouter un pictogramme en fonction du type d'entraînement
def get_training_icon(training_type):
    icons = {
        "Course": "🏃‍♂️",
        "Vélo": "🚴‍♀️",
        "Musculation": "🏋️‍♂️",
        "Natation": "🏊‍♀️",
        "Marche": "🚶‍♂️",
    }
    return icons.get(training_type, "❓")  # Par défaut, un point d'interrogation

# Fonction pour appeler l'API Spoonacular
def get_recipes_from_spoonacular(calories, proteins, carbs, fats):
    """Récupère des recettes adaptées aux macronutriments via Spoonacular."""
    API_KEY = st.secrets["SPOONACULAR_API_KEY"]  # Ajoutez votre clé API dans les secrets
    url = "https://api.spoonacular.com/recipes/findByNutrients"

    params = {
        "minCalories": max(0, calories - 50),
        "maxCalories": calories + 50,
        "minProtein": max(0, proteins - 5),
        "maxProtein": proteins + 5,
        "minCarbs": max(0, carbs - 10),
        "maxCarbs": carbs + 10,
        "minFat": max(0, fats - 5),
        "maxFat": fats + 5,
        "number": 3,  # Nombre de recettes à récupérer
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur API Spoonacular : {response.json()}")
        return []
        
# Modèle prédictif pour les calories brûlées
def train_predictive_model(trainings):
    """Entraîne un modèle de régression pour prédire les calories brûlées."""
    if len(trainings) < 5:  # Vérifier qu'il y a assez de données
        st.warning("Pas assez de données d'entraînement pour le modèle prédictif.")
        return None

    df = pd.DataFrame(trainings)
    X = df[["duration"]]  # Utilise la durée comme caractéristique
    y = df["calories_burned"]

    # Diviser en ensemble d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entraîner le modèle
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Tester le modèle
    y_pred = model.predict(X_test)
    st.write("Précision du modèle (R²) :", model.score(X_test, y_test))
    return model



# Menu principal mis à jour
menu = st.sidebar.selectbox(
    "Menu", [
        "Inscription", 
        "Connexion", 
        "Mon Profil", 
        "Ajouter un repas", 
        "Voir les repas", 
        "Ajouter un entraînement", 
        "Voir les entraînements", 
        "Suggestions personnalisées", 
        "Visualisations avancées"
    ]
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
            for meal in meals:
                photos = get_meal_photos(meal["id"])
                
                col1, col2 = st.columns([3, 1])  # Disposition : Infos à gauche, photo à droite
                with col1:
                    st.subheader(f"🍴 {meal['name']}")  # Titre en gras avec emoji
                    st.write(f"**Calories**: {meal['calories']} kcal")
                    st.write(f"**Protéines**: {meal['proteins']} g")
                    st.write(f"**Glucides**: {meal['carbs']} g")
                    st.write(f"**Lipides**: {meal['fats']} g")

                with col2:
                    if photos:
                        st.image(photos[0]["photo_url"], width=200)  # Miniature harmonieuse
                    else:
                        st.write("Pas de photo.")

                st.markdown("---")  # Séparation visuelle
# Ajouter des entraînements
if menu == "Ajouter un entraînement":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour ajouter un entraînement.")
    else:
        st.header("Ajouter un entraînement")

        training_type = st.selectbox(
            "Type d’entraînement", ["Course", "Vélo", "Musculation", "Natation", "Marche"]
        )
        date = st.date_input("Date de l’entraînement", value=datetime.now())
        duration = st.slider("Durée (en minutes)", 0, 300, 60)
        calories_burned = st.slider("Calories brûlées", 0, 2000, 300)

        if st.button("Ajouter l’entraînement"):
            user_id = st.session_state["user"]["id"]
            response = add_training(user_id, training_type, date, duration, calories_burned)
            if response.data:
                st.success("Entraînement ajouté avec succès !")
            else:
                st.error("Erreur lors de l'ajout de l'entraînement.")

# Voir les performances sportives
if menu == "Voir les entraînements":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour voir vos entraînements.")
    else:
        st.header("Vos entraînements")

        user_id = st.session_state["user"]["id"]
        trainings = get_user_trainings(user_id)

        if not trainings:
            st.info("Aucun entraînement enregistré.")
        else:
            # Convertir les données en DataFrame
            df = pd.DataFrame(trainings)

            # Ajouter les colonnes formatées pour un meilleur affichage
            df["Icone"] = df["training_type"].apply(get_training_icon)
            df["Date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y")  # Format : 01 Jan 2024
            df["Durée (min)"] = df["duration"]
            df["Calories brûlées"] = df["calories_burned"]

            # Garder uniquement les colonnes nécessaires
            display_df = df[["Icone", "Date", "training_type", "Durée (min)", "Calories brûlées"]]
            display_df.rename(
                columns={
                    "Icone": "Type",
                    "training_type": "Activité",
                },
                inplace=True,
            )

            # Utiliser AgGrid pour un tableau interactif
            gb = GridOptionsBuilder.from_dataframe(display_df)
            gb.configure_pagination(enabled=True)  # Activer la pagination
            gb.configure_column("Type", width=70)  # Ajuster la largeur de la colonne "Type"
            gb.configure_column("Activité", width=150)  # Ajuster la largeur de la colonne "Activité"
            gb.configure_column("Durée (min)", width=100)  # Ajuster la largeur de la colonne "Durée (min)"
            gb.configure_column("Calories brûlées", width=150)  # Ajuster la largeur de la colonne "Calories brûlées"

            grid_options = gb.build()

            st.markdown("### Tableau des entraînements")
            AgGrid(
                display_df,
                gridOptions=grid_options,
                theme="balham",  # Thème clair
                fit_columns_on_grid_load=True,  # Adapter les colonnes à la largeur
            )
            
# Suggestions personnalisées améliorées avec API Spoonacular
if menu == "Suggestions personnalisées":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour voir vos suggestions.")
    else:
        st.header("Suggestions personnalisées")

        user_id = st.session_state["user"]["id"]
        trainings = get_user_trainings(user_id)
        meals = get_user_meals(user_id)

        if not trainings:
            st.info("Aucun entraînement trouvé pour générer des suggestions.")
        elif not meals:
            st.info("Aucun repas trouvé pour générer des suggestions.")
        else:
            total_burned = sum([t["calories_burned"] for t in trainings])
            total_calories = sum([m["calories"] for m in meals])

            st.markdown(f"### **Calories brûlées cette semaine** : {total_burned} kcal")
            st.markdown(f"### **Calories consommées cette semaine** : {total_calories} kcal")

            # Suggestions basées sur le déficit calorique
            deficit = total_burned - total_calories
            if deficit > 0:
                st.success(
                    f"Vous avez un déficit calorique de {deficit} kcal. Nous vous recommandons de consommer des repas plus caloriques."
                )
            else:
                st.warning(
                    f"Vous avez un surplus calorique de {-deficit} kcal. Essayez de réduire les calories dans vos repas."
                )

            # Calcul des besoins nutritionnels pour Spoonacular
            predicted_calories = abs(deficit)  # Déficit ou surplus converti en absolu pour ajuster les besoins
            proteins_needed = 50 if predicted_calories > 400 else 30
            carbs_needed = 100 if predicted_calories > 600 else 50
            fats_needed = 20

            st.markdown(f"### Besoins estimés pour combler l'écart :")
            st.write(f"- Calories : {predicted_calories} kcal")
            st.write(f"- Protéines : {proteins_needed} g")
            st.write(f"- Glucides : {carbs_needed} g")
            st.write(f"- Lipides : {fats_needed} g")

            # Appel à l'API Spoonacular
            st.markdown("### Recettes suggérées :")
            recipes = get_recipes_from_spoonacular(predicted_calories, proteins_needed, carbs_needed, fats_needed)

            if recipes:
                for recipe in recipes:
                    st.markdown(f"### {recipe['title']}")
                    st.image(recipe["image"], width=300)  # Ajuster uniquement la largeur   
                    st.write(f"Calories : {recipe['calories']} kcal")
                    st.write(f"[Voir la recette complète](https://spoonacular.com/recipes/{recipe['id']})")
            else:
                st.error("Aucune recette trouvée correspondant aux besoins nutritionnels.")


# Visualisations avancées
if menu == "Visualisations avancées":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour accéder aux visualisations.")
    else:
        st.header("Visualisations avancées")

        user_id = st.session_state["user"]["id"]
        trainings = get_user_trainings(user_id)
        meals = get_user_meals(user_id)

        if not trainings or not meals:
            st.info("Données insuffisantes pour générer des visualisations.")
        else:
            # Préparer les données
            training_dates = [t["date"] for t in trainings]
            calories_burned = [t["calories_burned"] for t in trainings]
            meal_dates = [m["date"] for m in meals]
            calories_consumed = [m["calories"] for m in meals]

            # Graphique 1 : Calories brûlées vs consommées
            plt.figure(figsize=(10, 5))
            plt.plot(training_dates, calories_burned, label="Calories brûlées", marker="o")
            plt.plot(meal_dates, calories_consumed, label="Calories consommées", marker="o")
            plt.xlabel("Date")
            plt.ylabel("Calories")
            plt.title("Calories brûlées vs consommées")
            plt.legend()
            st.pyplot(plt)

if menu == "Suggestions personnalisées":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour voir vos suggestions.")
    else:
        st.header("Suggestions personnalisées")

        user_id = st.session_state["user"]["id"]
        trainings = get_user_trainings(user_id)
        meals = get_user_meals(user_id)

        if not trainings or not meals:
            st.info("Ajoutez plus de données pour générer des suggestions.")
        else:
            # Entraîner un modèle prédictif
            model = train_predictive_model(trainings)

            if model:
                # Prédire les calories pour un nouvel entraînement
                next_training_duration = st.slider("Durée du prochain entraînement (min)", 10, 120, 30)
                predicted_calories = model.predict(np.array([[next_training_duration]]))[0]
                st.write(f"Calories estimées pour le prochain entraînement : {predicted_calories:.2f} kcal")

                # Calcul des besoins nutritionnels
                proteins_needed = 50 if predicted_calories > 400 else 30
                carbs_needed = 100 if predicted_calories > 600 else 50
                fats_needed = 20

                # Appeler l'API Spoonacular
                recipes = get_recipes_from_spoonacular(predicted_calories, proteins_needed, carbs_needed, fats_needed)

                # Afficher les recettes
                st.subheader("Recettes suggérées")
                for recipe in recipes:
                    st.markdown(f"### {recipe['title']}")
                    st.image(recipe["image"])
                    st.write(f"Calories : {recipe['calories']} kcal")

if menu == "Visualisations avancées":
    if st.session_state["user"] is None:
        st.warning("Veuillez vous connecter pour accéder aux visualisations.")
    else:
        st.header("Visualisations avancées")

        user_id = st.session_state["user"]["id"]
        trainings = get_user_trainings(user_id)
        meals = get_user_meals(user_id)

        if not trainings or not meals:
            st.info("Données insuffisantes pour générer des visualisations.")
        else:
            # Afficher les calories brûlées et consommées
            training_dates = [t["date"] for t in trainings]
            calories_burned = [t["calories_burned"] for t in trainings]
            meal_dates = [m["date"] for m in meals]
            calories_consumed = [m["calories"] for m in meals]

            plt.figure(figsize=(10, 5))
            plt.plot(training_dates, calories_burned, label="Calories brûlées", marker="o")
            plt.plot(meal_dates, calories_consumed, label="Calories consommées", marker="o")
            plt.xlabel("Date")
            plt.ylabel("Calories")
            plt.title("Calories brûlées vs consommées")
            plt.legend()
            st.pyplot(plt)

            # Histogramme des durées d'entraînement
            durations = [t["duration"] for t in trainings]
            plt.figure(figsize=(10, 5))
            plt.hist(durations, bins=10, alpha=0.7)
            plt.xlabel("Durée (min)")
            plt.ylabel("Fréquence")
            plt.title("Répartition des durées d'entraînement")
            st.pyplot(plt)
            
