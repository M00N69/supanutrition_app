# Appapoute - Application de Nutrition et Entraînements

Appapoute est une application interactive développée avec **Streamlit** et **Supabase**. Elle permet aux utilisateurs de suivre leurs repas et leurs entraînements, d'obtenir des suggestions de recettes personnalisées, et de visualiser leurs performances sportives à l'aide de graphiques.

---

## 🗂️ Table des matières

1. [Technologies utilisées](#technologies-utilisées)
2. [Architecture de l'application](#architecture-de-lapplication)
3. [Structure des fonctionnalités](#structure-des-fonctionnalités)
4. [Instructions pour l'installation](#instructions-pour-linstallation)
5. [Améliorations futures](#améliorations-futures)

---

## 🛠️ Technologies utilisées

### **Frontend**
- **Streamlit** : Framework Python pour créer des interfaces interactives.
- **st-aggrid** : Pour afficher des tableaux interactifs et paginés.

### **Backend**
- **Supabase** :
  - **Base de données PostgreSQL** : Stockage des repas, entraînements, et utilisateurs.
  - **Authentification** : Gestion sécurisée des utilisateurs.
  - **Stockage** : Gestion des photos des repas.

### **Machine Learning**
- **scikit-learn** : Utilisé pour prédire les calories brûlées lors des entraînements.

### **API externe**
- **Spoonacular** : Fournit des suggestions de recettes adaptées aux besoins nutritionnels des utilisateurs.

---

## 🌟 Architecture de l'application

L'application est structurée autour de **menus** principaux :

1. **Inscription et Connexion**
   - Authentification via Supabase.
   - Gestion des sessions utilisateur avec `st.session_state`.

2. **Mon Profil**
   - Visualisation des informations utilisateur.
   - Option de déconnexion.

3. **Gestion des repas**
   - Ajout de repas : Formulaire permettant de renseigner calories, protéines, glucides, lipides, et upload d'images.
   - Visualisation des repas : Liste des repas avec détails nutritionnels et photos.

4. **Gestion des entraînements**
   - Ajout d'entraînements : Saisie de la durée, du type d'activité, et des calories brûlées.
   - Visualisation des entraînements : Tableau interactif affiché avec AgGrid.

5. **Suggestions personnalisées**
   - Analyse du déficit ou surplus calorique basé sur les repas et entraînements enregistrés.
   - Utilisation de l'API Spoonacular pour suggérer des recettes adaptées aux besoins nutritionnels.

6. **Visualisations avancées**
   - Graphiques et analyses des calories brûlées vs consommées.
   - Histogramme des durées d'entraînement.

---

## 🏗️ Structure des fonctionnalités

### **Modules principaux**
- **Fonctions utilitaires** :
  - `get_user_meals(user_id)` : Récupère les repas enregistrés pour un utilisateur.
  - `get_meal_photos(meal_id)` : Récupère les photos des repas.
  - `get_user_trainings(user_id)` : Récupère les entraînements de l'utilisateur.
  - `add_training()` : Ajoute un entraînement à la base de données.
  - `get_recipes_from_spoonacular()` : Appelle l'API Spoonacular pour récupérer des recettes.

- **Machine Learning** :
  - `train_predictive_model(trainings)` :
    - Entraîne un modèle de régression linéaire pour prédire les calories brûlées.
    - Entrée : Durée des entraînements.
    - Sortie : Calories estimées.

- **Visualisations** :
  - Graphique des calories brûlées vs consommées.
  - Histogramme des durées d'entraînement.

### **Menus de navigation**
Les menus sont définis à l'aide de `st.sidebar.selectbox` :
- **Repas** :
  - Ajouter un repas.
  - Voir les repas enregistrés.
- **Entraînements** :
  - Ajouter un entraînement.
  - Voir les entraînements enregistrés.
- **Suggestions personnalisées** :
  - Analyse des besoins nutritionnels.
  - Suggestions de recettes via Spoonacular.
- **Visualisations avancées** :
  - Analyse et graphiques des performances sportives et nutritionnelles.

---

## 🚀 Instructions pour l'installation

### **Pré-requis**
1. **Python 3.8** ou supérieur.
2. Une clé API Spoonacular (ajoutée dans les secrets Streamlit).

### **Étapes d'installation**

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/username/appapoute.git
   cd appapoute
Installer les dépendances : Créez un environnement virtuel et installez les packages nécessaires :

bash
Copier le code
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt
Configurer les secrets Streamlit : Créez un fichier .streamlit/secrets.toml dans le répertoire racine, avec le contenu suivant :

toml
Copier le code
[secrets]
SUPABASE_URL = "votre_supabase_url"
SUPABASE_KEY = "votre_supabase_key"
SPOONACULAR_API_KEY = "votre_spoonacular_api_key"
Lancer l'application :

bash
Copier le code
streamlit run main.py
📈 Améliorations futures
Fonctionnalités à développer
Suivi personnalisé :

Ajout d'objectifs nutritionnels (perte de poids, prise de masse).
Notifications pour le suivi des repas et entraînements.
Modèle prédictif amélioré :

Intégration de données supplémentaires pour des prédictions plus précises.
Suggestions automatiques basées sur les prédictions.
Social :

Fonctionnalités pour partager des repas/entraînements avec des amis.
Classements et défis sportifs.
Expérience utilisateur :

Optimisation de l'interface pour une utilisation mobile.
Création d'une version Progressive Web App (PWA).
