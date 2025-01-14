import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Ordner und Webdriver konfigurieren
input_folder = r"links_zu_spieler_nach_verein"
output_folder = r"spieler_v2_seasons"
chromedriver_path = r"C:\Users\Simon\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

if not os.path.exists(chromedriver_path):
    raise FileNotFoundError(f"Chromedriver nicht gefunden unter: {chromedriver_path}")

os.makedirs(output_folder, exist_ok=True)

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# Iteriere durch alle Vereinsdateien
for file_name in os.listdir(input_folder):
    if not file_name.endswith("_spieler.csv"):
        continue

    verein_name = file_name.replace("_spieler.csv", "")
    input_file = os.path.join(input_folder, file_name)
    output_csv = os.path.join(output_folder, f"{verein_name}.csv")

    # Überprüfen, ob die Eingabedatei existiert
    if not os.path.exists(input_file):
        print(f"Eingabedatei nicht gefunden: {input_file}")
        continue

    with open(input_file, "r", encoding="utf-8") as infile, open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(infile)
        next(reader)  # Überspringe die Headerzeile

        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["spieler_id", "Wettbewerb_id", "Saison", "Wettbewerb", "Verein", "Einsätze", "Tore", "Torvorlagen", "Spiele ohne Gegentor", "Eingesetzte Minuten"])

        for row in reader:
            link = row[0].replace("marktwertverlauf", "detaillierteleistungsdaten")
            spieler_id = link.split("/")[-1]
            spieler_name = link.split("/")[-3].replace("-", " ").title()

            print(f"Verarbeite Spieler: {spieler_name} (ID: {spieler_id})")

            # Webseite laden
            try:
                driver.get(link)
            except Exception as e:
                print(f"Fehler beim Laden der Seite für Spieler {spieler_name}: {e}")
                continue

            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Iteriere durch alle "Boxes"
            for box in soup.find_all("div", class_="box"):
                h2 = box.find("h2", class_="content-box-headline")
                if not h2:
                    continue

                title = h2.text.strip()
                if "Nationale Ligen" in title:
                    wettbewerb_id = 1
                elif "Nationale Pokalwettbewerbe" in title:
                    wettbewerb_id = 2
                elif "Internationale Pokalwettbewerbe" in title:
                    wettbewerb_id = 3
                else:
                    continue

                table = box.find("table", class_="items")
                if not table:
                    continue

                # <thead> extrahieren
                thead = table.find("thead")
                if not thead:
                    continue

                column_indices = {"Saison": None, "Wettbewerb": None, "Verein": None,
                                  "Einsätze": None, "Tore": None, "Torvorlagen": None, "Spiele ohne Gegentor": None, "Eingesetzte Minuten": None}
                minus_counter = 0

                for idx, element in enumerate(thead.find_all(["a", "span"])):
                    if element.name == "a":
                        text = element.text.strip()
                        if not text or any(x in text for x in ["ASC", "DESC"]):
                            minus_counter += 1
                            continue  # Ignoriere unerwünschte Inhalte
                        if text in column_indices:
                            column_indices[text] = idx - minus_counter
                    elif element.name == "span" and "title" in element.attrs:
                        title_attr = element["title"]
                        if title_attr in column_indices:
                            column_indices[title_attr] = idx - minus_counter

                # <tbody> extrahieren und speichern
                tbody = table.find("tbody")
                if tbody:
                    for row in tbody.find_all("tr"):
                        cells = row.find_all("td")

                        if int(len(cells)) <= int(max([val for val in column_indices.values() if val is not None])):
                            continue  # Überspringen, wenn nicht genügend Zellen vorhanden

                        saison = f"'{cells[column_indices['Saison']].text.strip()}'" if column_indices["Saison"] is not None else "null"
                        wettbewerb = cells[column_indices["Wettbewerb"]+1].text.strip() if column_indices["Wettbewerb"] is not None else "null"
                        verein_element = cells[column_indices["Verein"]+1].find("img") if column_indices["Verein"] is not None else None
                        verein = verein_element["title"] if verein_element and "title" in verein_element.attrs else "null"
                        einsaetze = cells[column_indices["Einsätze"]+1].text.strip() if column_indices["Einsätze"] is not None else "null"
                        tore = cells[column_indices["Tore"]+1].text.strip() if column_indices["Tore"] is not None else "null"
                        torvorlagen = cells[column_indices["Torvorlagen"]+1].text.strip() if column_indices["Torvorlagen"] is not None else "null"
                        spiele_ohne_gegentor = cells[column_indices["Spiele ohne Gegentor"]+1].text.strip() if column_indices["Spiele ohne Gegentor"] is not None else "null"
                        eingesetzte_minuten = cells[column_indices["Eingesetzte Minuten"]+1].text.strip().replace(".", "").replace("'", "") if column_indices["Eingesetzte Minuten"] is not None else "null"

                        writer.writerow([spieler_id, wettbewerb_id, saison, wettbewerb, verein, einsaetze, tore, torvorlagen, spiele_ohne_gegentor, eingesetzte_minuten])

driver.quit()
print("Verarbeitung abgeschlossen.")
