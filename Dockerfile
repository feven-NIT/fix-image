# Utiliser une image de base spécifiée par une variable d'environnement
FROM random

# Copier le script de mise à jour des paquets dans l'image
COPY update_packages.py /tmp/update_packages.py

# Copier le fichier CSV dans l'image
COPY scan.csv /tmp/scan.csv

RUN pip install --upgrade pip


# Exécuter le script, puis supprimer le script et le fichier CSV
RUN python3 /tmp/update_packages.py && \
    rm /tmp/update_packages.py /tmp/scan.csv

# Changer l'utilisateur à non-root
RUN useradd -m nonroot

# Définir l'utilisateur non-root
USER nonroot
