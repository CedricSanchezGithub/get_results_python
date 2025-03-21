import os

from bs4 import BeautifulSoup

folder = "data"

def get_content(driver, category, tag_name=None ):
    """Récupère le contenu d'une balise ou d'une classe HTML spécifiée et l'enregistre dans un fichier HTML,
     dans un dossier spécifié."""

    html_filename = f"get_content_{category}.html"

    # Créer le dossier s'il n'existe pas
    if not os.path.exists(folder):
        os.makedirs(folder)

    html_filepath = os.path.join(folder, html_filename)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Recherche de la balise ou classe spécifiée
    if tag_name:
        content = soup.find(tag_name)
    else:
        print("Ni balise ni classe spécifiée. Aucun contenu récupéré.")
        return

    if content:
        # Sauvegarde en fichier HTML
        with open(html_filepath, "w", encoding="utf-8") as file:
            file.write(str(content))
        print(f"Contenu de <{tag_name}> sauvegardé dans le fichier : {html_filepath}")


