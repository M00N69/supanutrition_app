# supanutrition_app
Application de Nutrition et Entraînements - Appapoute
Cette application est une plateforme interactive construite avec Streamlit et Supabase. Elle permet aux utilisateurs de suivre leurs repas et entraînements, d'obtenir des suggestions personnalisées de recettes basées sur leurs besoins nutritionnels, et de visualiser leurs performances sportives.

Table des matières
Technologies utilisées
Architecture de l'application
Structure des fonctionnalités
Instructions pour l'installation
Améliorations futures
Technologies utilisées
Frontend
Streamlit : Framework Python pour le développement d'interfaces utilisateur interactives.
st-aggrid : Pour afficher des tableaux interactifs et paginés.
Backend
Supabase :
Base de données PostgreSQL : Stockage des repas, entraînements, et utilisateurs.
Authentification : Gestion des utilisateurs.
Stockage : Gestion des photos des repas.
Machine Learning
scikit-learn : Pour créer un modèle prédictif des calories brûlées lors des entraînements.
API externe
Spoonacular : Pour récupérer des suggestions de recettes adaptées aux besoins nutritionnels.
Architecture de l'application
L'application est organisée autour de plusieurs menus principaux :

Inscription et Connexion

Gestion des utilisateurs via Supabase Auth.
Stockage des identifiants et sessions dans st.session_state.
Mon Profil

Visualisation des informations utilisateur.
Option de déconnexion.
Gestion des repas

Ajout de repas : Formulaire avec calories, protéines, glucides, lipides et upload d'images.
Visualisation des repas : Liste des repas avec détails et photos.
Gestion des entraînements

Ajout d'entraînements : Durée, type d'activité, calories brûlées.
Visualisation des entraînements : Tableau interactif avec AgGrid.
Suggestions personnalisées

Analyse du déficit/surplus calorique basé sur les repas et entraînements enregistrés.
Utilisation de l'API Spoonacular pour suggérer des recettes.
Visualisations avancées

Graphiques et analyses des calories brûlées et consommées.
Histogramme des durées d'entraînement.
Structure des fonctionnalités
Modules clés
Fonctions utilitaires

get_user_meals(user_id) : Récupère les repas de l'utilisateur.
get_meal_photos(meal_id) : Récupère les photos associées à un repas.
get_user_trainings(user_id) : Récupère les entraînements de l'utilisateur.
add_training() : Ajoute un nouvel entraînement à la base de données.
get_recipes_from_spoonacular() : Appelle l'API Spoonacular pour des suggestions de recettes.
Machine Learning

train_predictive_model(trainings) :
Entraîne un modèle de régression linéaire pour prédire les calories brûlées.
Entrée : Durée des entraînements.
Sortie : Calories brûlées estimées.
Visualisations

Graphiques des calories brûlées vs consommées (matplotlib).
Histogramme des durées d'entraînement.
Menu
Les menus sont définis à l'aide de st.sidebar.selectbox. Chaque option affiche un ensemble d'actions ou visualisations spécifiques :

Repas :
Ajouter un repas.
Voir les repas (infos + photos).
Entraînements :
Ajouter un entraînement.
Voir les entraînements (tableau interactif).
Suggestions personnalisées :
Analyse du déficit/surplus calorique.
Recommandation de recettes via l'API Spoonacular.
Visualisations avancées :
Graphiques des performances.
Instructions pour l'installation
Pré-requis
Python 3.8 ou supérieur.
Clé API Spoonacular (ajoutée aux secrets de Streamlit).
Étapes d'installation
Clonez le dépôt :

bash
Copier le code
git clone https://github.com/username/appapoute.git
cd appapoute
Installez les dépendances : Créez un environnement virtuel et installez les dépendances :

bash
Copier le code
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt
Ajoutez les secrets de Streamlit : Créez un fichier .streamlit/secrets.toml et ajoutez les informations suivantes :

toml
Copier le code
[secrets]
SUPABASE_URL = "votre_supabase_url"
SUPABASE_KEY = "votre_supabase_key"
SPOONACULAR_API_KEY = "votre_spoonacular_api_key"
Lancez l'application :

bash
Copier le code
streamlit run main.py
Améliorations futures
Fonctionnalités
Suivi personnalisé

Intégration d’objectifs nutritionnels spécifiques (ex. : perte de poids, prise de masse).
Notifications ou rappels pour suivre les repas et entraînements.
Modèle prédictif amélioré

Enrichir les données d'entraînement pour intégrer plusieurs caractéristiques (type d'entraînement, intensité).
Ajouter des recommandations automatiques basées sur les prédictions.
Social

Fonctionnalités de partage de repas/entraînements avec d'autres utilisateurs.
Classements et défis sportifs.
Mobile-friendly

Optimisation de l'interface pour une meilleure expérience mobile.
Intégration progressive d'une PWA (Progressive Web App).
