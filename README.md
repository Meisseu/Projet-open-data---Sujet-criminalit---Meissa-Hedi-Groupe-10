# SafeCity - Tableau de bord sécurité urbaine

## 📋 Description

SafeCity est une application d'analyse interactive de la criminalité en France, développée dans le cadre du module Open Data & IA. Elle permet aux décideurs et analystes de visualiser, comprendre et comparer les données de criminalité à travers différents territoires et périodes.

L'application offre une interface intuitive avec des visualisations interactives, des analyses temporelles et un assistant IA pour interpréter les tendances et générer des rapports automatiques.

## 🎯 Fonctionnalités

- **📍 Vue d'ensemble**: Statistiques clés, top départements, et distribution par type de crime
- **📈 Analyse temporelle**: Évolution annuelle, tendances et cartes de chaleur
- **🗺️ Cartographie interactive**: Carte choroplèthe de France avec données par département
- **⚖️ Comparaison territoriale**: Comparaison multi-départements avec différentes métriques
- **💬 Assistant IA**: Chatbot intelligent pour l'analyse et la génération de rapports
- **🔍 Filtrage avancé**: Filtres par période, département et type de crime
- **📊 Visualisations multiples**: Graphiques interactifs (Plotly), cartes, tableaux

## 🛠️ Installation

### Prérequis

- Python 3.10 ou supérieur
- `uv` (gestionnaire de packages Python)

### Installation avec uv

```bash
# Cloner le repository
git clone https://github.com/votre-username/safecity.git
cd safecity

# Installer uv si ce n'est pas déjà fait
pip install uv

# Installer les dépendances avec uv
uv sync

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

### Configuration des clés API

Éditez le fichier `.env` et ajoutez vos clés API:

```env
# Configuration LiteLLM
LITELLM_API_KEY=votre_clé_api
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic

# Configuration des modèles
DEFAULT_MODEL=gpt-3.5-turbo
FALLBACK_MODEL=claude-3-haiku-20240307
```

**Note**: Au moins une clé API (OpenAI ou Anthropic) est nécessaire pour utiliser les fonctionnalités IA. L'application fonctionnera avec des réponses de secours si aucune clé n'est configurée.

## 🚀 Lancement

```bash
# Lancer l'application Streamlit
uv run streamlit run app.py
```

L'application sera accessible à l'adresse: `http://localhost:8501`

## 📊 Sources de données

- **[Crimes et délits enregistrés](https://www.data.gouv.fr/fr/datasets/crimes-et-delits-enregistres-par-les-services-de-gendarmerie-et-de-police-depuis-2012/)** - Ministère de l'Intérieur
  - Données détaillées des crimes et délits enregistrés par les services de police et gendarmerie depuis 2012
  - Mise à jour: Mensuelle
  
- **[Contours géographiques des départements](https://www.data.gouv.fr/fr/datasets/contours-des-departements-francais-issus-d-openstreetmap/)** - IGN/OpenStreetMap
  - Fichiers GeoJSON pour la cartographie
  
- **Données de population** - INSEE
  - Population par département (intégrée dans l'application)

## 🤖 Intégration IA

L'application utilise **LiteLLM** pour intégrer plusieurs modèles d'IA:

### Modèles supportés

- **OpenAI**: GPT-4, GPT-3.5-turbo, GPT-4-turbo-preview
- **Anthropic**: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku

### Fonctionnalités IA

- **Analyse de tendances**: Interprétation automatique des évolutions
- **Génération de rapports**: Création de synthèses textuelles
- **Comparaisons**: Contextualisation des différences territoriales
- **Chatbot**: Réponses aux questions sur les statistiques

## 📁 Structure du projet

```
safecity/
├── .env.example        # Template des variables d'environnement
├── .gitignore          # Fichiers à ignorer par Git
├── pyproject.toml      # Configuration uv et dépendances
├── README.md           # Documentation (ce fichier)
├── app.py              # Application Streamlit principale
├── utils/
│   ├── __init__.py     # Package utils
│   ├── data.py         # Chargement et traitement des données
│   ├── charts.py       # Création de visualisations
│   └── chatbot.py      # Intégration IA avec LiteLLM
├── data/
│   └── processed/      # Données en cache
└── notebooks/          # Notebooks d'exploration (optionnel)
```

## 💻 Technologies utilisées

- **Framework**: Streamlit 1.29+
- **Visualisations**: Plotly, Folium
- **Traitement de données**: Pandas, GeoPandas
- **IA**: LiteLLM (OpenAI, Anthropic)
- **Gestion de projet**: uv (pyproject.toml)

## 🎨 Captures d'écran

### Vue d'ensemble
Tableau de bord avec statistiques clés, top départements et distribution des types de crimes.

### Cartographie
Carte choroplèthe interactive montrant la répartition géographique de la criminalité.

### Assistant IA
Chatbot intelligent pour l'analyse et la génération de rapports personnalisés.

## 📈 Exemples d'utilisation

### Analyse de tendances
1. Sélectionner une période dans la sidebar
2. Choisir un département spécifique
3. Naviguer vers l'onglet "Analyse temporelle"
4. Consulter les graphiques d'évolution

### Comparaison de territoires
1. Aller dans l'onglet "Comparaison"
2. Sélectionner 2 à 5 départements
3. Choisir une métrique (total, évolution, types)
4. Analyser les différences

### Génération de rapport
1. Sélectionner un département
2. Aller dans l'onglet "Assistant IA"
3. Cliquer sur "Générer un rapport"
4. Obtenir une analyse complète

## 🔧 Configuration avancée

### Changer le modèle IA par défaut

Modifiez le fichier `.env`:
```env
DEFAULT_MODEL=gpt-4
FALLBACK_MODEL=claude-3-sonnet-20240229
```

### Ajuster la taille de l'échantillon de données

Dans [app.py](app.py), ligne 94:
```python
df = data_loader.load_crime_data(sample_size=50000)  # Modifier cette valeur
```

### Personnaliser les visualisations

Les fonctions de visualisation sont dans [utils/charts.py](utils/charts.py). Modifiez les paramètres Plotly pour personnaliser l'apparence.

## 🐛 Dépannage

### Erreur "LiteLLM not available"
```bash
# Réinstaller LiteLLM
uv pip install litellm
```

### Erreur de téléchargement des données
- Vérifiez votre connexion internet
- L'application utilisera des données de démonstration si le téléchargement échoue
- Le cache est stocké dans `data/processed/crime_data.csv`

### Problèmes de performance
- Réduire `sample_size` dans le chargement des données
- Limiter la période analysée avec les filtres
- Fermer les onglets non utilisés

## 🚀 Améliorations futures

- [ ] Export de rapports en PDF
- [ ] Analyses prédictives avec ML
- [ ] Intégration de données météo
- [ ] API REST pour l'accès aux données
- [ ] Dashboard multi-utilisateurs
- [ ] Système de notifications d'alertes

## 👥 Équipe

- **Développeur 1**: [Nom] - Architecture et backend
- **Développeur 2**: [Nom] - Interface et visualisations
- **Développeur 3**: [Nom] - Intégration IA
- **Développeur 4**: [Nom] - Documentation et tests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **data.gouv.fr** pour l'accès aux données ouvertes
- **Ministère de l'Intérieur** pour les données de criminalité
- **INSEE** pour les données démographiques
- **Streamlit** pour le framework d'application
- **LiteLLM** pour l'intégration multi-modèles IA

## 📞 Contact

Pour toute question ou suggestion:
- Email: safecity@example.com
- Issues: https://github.com/votre-username/safecity/issues

---

**Projet réalisé dans le cadre du Module Open Data & IA - 2024**
