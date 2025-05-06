from pathlib import Path

LANGUAGE_CODE = 'en'  # Définit l'anglais comme langue par défaut

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Liste des langues disponibles
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

BASE_DIR = Path(__file__).resolve().parent.parent

LOCALE_PATHS = [
    BASE_DIR / 'locale',  # Assurez-vous que ce chemin est correct
]