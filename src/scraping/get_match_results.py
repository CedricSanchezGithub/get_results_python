import locale
import os
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from pandas.io.formats import string

from src.scraping.get_competition_and_day import get_day_via_url, get_competition_via_url
from src.saving.save_data_csv import save_data


def get_pool_results(driver, category):

    csv_filename = f"pool_{category}.csv"
    folder = "data"
    os.makedirs(folder, exist_ok=True)
    csv_filepath = os.path.join(folder, csv_filename)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    competition = get_competition_via_url(driver)
    day = get_day_via_url(driver)

    main_containers = soup.find_all(class_="styles_rencontre__9O0P0")
    if not main_containers:
        print(f"Aucune balise trouvée pour la classe 'styles_rencontre__9O0P0")
        return

    match_data = []

    for container in main_containers:
        try:
            date_container = container.find("p", class_="block_date__dYMQX")
            date_string = date_container.text.strip() if date_container else None
            team_left_name, team_left_score = extract_team_data(container, "styles_left__svLY+")
            team_right_name, team_right_score = extract_team_data(container, "styles_right__wdfIf")
            match_link = container.get("href", None)

            match_data.append({
                "date_string": parse_date_to_milliseconds(date_string),
                "team_1_name": team_left_name,
                "team_1_score": team_left_score,
                "team_2_name": team_right_name,
                "team_2_score": team_right_score,
                "match_link": match_link,
                "competition": competition,
                "journee": day
            })

        except AttributeError as e:
            print(f"Erreur dans un conteneur : {e}")
            continue

    all_data = pd.DataFrame(match_data)

    save_data(csv_filepath, all_data)


def extract_team_data(container, side_class):

    team_container = container.find("div", class_=side_class)
    if not team_container:
        return "Nom non disponible", None

    # Nom de l'équipe
    team_name = (
        team_container.find("div", class_="styles_teamName__aH4Gu").text.strip()
        if team_container.find("div", class_="styles_teamName__aH4Gu")
        else "Nom non disponible"
    )

    # Score de l'équipe
    team_score = (
        team_container.find("div", class_="styles_score__ELPXO").text.strip()
        if team_container.find("div", class_="styles_score__ELPXO")
        else "-"
    )

    return team_name, team_score


def parse_date_to_milliseconds(date_string):

    if date_string is not string:
        print("Date invalide ou vide")
        return 0

    # Définir la locale pour reconnaître les noms de jours et mois en français
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    # Remplacer "à" et "H" pour faciliter le parsing
    date_string = date_string.replace(" à ", " ").replace("H", ":")

    # Parser la date
    date_format = "%A %d %B %Y %H:%M"
    try:
        dt = datetime.strptime(date_string, date_format)
        # Convertir en timestamp en millisecondes
        timestamp_ms = int(dt.timestamp() * 1000)
        return timestamp_ms
    except ValueError as e:
        print(f"Erreur lors du parsing de la date : {e}")
        return None