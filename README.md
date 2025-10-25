# Syntaiz

Bienvenue dans le projet **Syntaiz**.

## Description

Ce projet est une application Django conçue pour ....

## Prérequis

- Python 3.8+
- Django 5.x


## Installation

```bash
git clone https://github.com/sylvere36/syntaiz-public.git
cd syntaiz.django
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environnement
Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
SECRET_KEY=django-insecure-s0-tcc+*ybjpku5e(o027w)g78u@+r53cu%hc=geln0v=dbvax
DEBUG=True
ENV=testing
OPENAI_API_KEY=sk-remplacez_par_votre_cle
OPENAI_MODEL=gpt-4o-mini
```

- `SECRET_KEY` : Clé secrète Django (à personnaliser pour la production).
- `DEBUG` : Active le mode debug (`True` pour le développement, `False` pour la production).
- `ENV` : Peut prendre la valeur `testing` ou `production` selon l'environnement.
- `OPENAI_API_KEY` : (Optionnel) Clé API OpenAI. Si absente, le traitement IA utilise un mock.
- `OPENAI_MODEL` : (Optionnel) Nom du modèle OpenAI à utiliser (`gpt-4o-mini` par défaut).

Assurez-vous de ne jamais partager votre clé secrète en production.

## Utilisation

1. Cree une nouvelle application
    ```bash
    python manage.py startapp nom_de_votre_app
    ```
    Remplacez `nom_de_votre_app` par le nom souhaité pour l'application.

2. Make migration
    ```bash
    python manage.py makemigrations
    ```

3. Appliquer les migrations :
    ```bash
    python manage.py migrate
    ```
4. Lancer le serveur de développement :
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
5. Pour y acceder dans le navigateur :
    ```bash
    127.0.0.1:8000
    ```

## Traitement de texte avec OpenAI (Optionnel)

Le module `scanned_text/helpers/ai_utils.py` expose des fonctions :

- `process_with_ai_or_mock(text)` : renvoie un dict `{processed, detected_type, summary}`.
- `openai_summarize(text)` et `openai_detect_type(text)` : utilisent OpenAI si configuré.

Sans variables OpenAI, le système retombe sur une génération et classification simulées.
