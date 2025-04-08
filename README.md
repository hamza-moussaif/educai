# Générateur de Contenu Pédagogique

Une application web permettant aux enseignants de générer automatiquement des ressources pédagogiques personnalisées en fonction d'un sujet et d'un niveau scolaire.

## Fonctionnalités

- Génération de différents types de contenu pédagogique :
  - QCM (Questions à Choix Multiples)
  - Exercices pratiques
  - Textes à trous
  - Fiches de synthèse
  - Schémas conceptuels
- Personnalisation du niveau de difficulté
- Sauvegarde de l'historique des générations
- Interface utilisateur intuitive et responsive

## Prérequis

- Python 3.8+
- Node.js 14+
- npm ou yarn
- Une clé API OpenAI

## Installation

### Backend

1. Créez un environnement virtuel Python :

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` dans le dossier `backend` avec votre clé API OpenAI :

```
OPENAI_API_KEY=votre_clé_api_ici
```

### Frontend

1. Installez les dépendances :

```bash
cd frontend
npm install
```

## Lancement de l'application

1. Démarrez le serveur backend :

```bash
cd backend
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
python server.py
```

2. Dans un autre terminal, démarrez le frontend :

```bash
cd frontend
npm start
```

3. Ouvrez votre navigateur et accédez à `http://localhost:3000`

## Structure du Projet

```
.
├── backend/
│   ├── venv/
│   ├── server.py
│   ├── content_generator.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   │   ├── SubjectInputForm.js
    │   │   └── ContentGenerator.js
    │   ├── App.js
    │   └── index.js
    ├── package.json
    └── README.md
```

## Technologies Utilisées

- Frontend :

  - React
  - React Bootstrap
  - Axios

- Backend :
  - Flask
  - SQLAlchemy
  - LangChain
  - OpenAI API

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
