import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Datei- und Ordnerpfade
input_folder = r"links_zu_spieler_nach_verein"
output_folder = r"spieler_profil_pro_verein"
os.makedirs(output_folder, exist_ok=True)

# Webdriver-Setup
chromedriver_path = r"C:\Users\Simon\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
options = Options()
options.add_argument("--headless")
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(60)

# Funktion zur Umlaute-Korrektur
def replace_umlauts(text):
    return (
        text.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
        .replace("ß", "ss")
    )

# Alle Dateien im Eingabeordner durchlaufen
for filename in os.listdir(input_folder):
    if filename.endswith("_spieler.csv"):
        input_file = os.path.join(input_folder, filename)
        verein_name = filename.replace("_spieler.csv", "")
        output_file = os.path.join(output_folder, f"{verein_name}_profil.csv")

        with open(input_file, "r", newline="", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
            reader = csv.reader(infile, delimiter=";")
            writer = csv.writer(outfile, delimiter=";")

            # Header schreiben
            writer.writerow(["Vereinsname", "Spieler_id", "Name", "Link", "Geb./Alter", "Geburtsort", "Staatsbürgerschaft", "Größe", "Position", "Fuss"])

            for i, row in enumerate(reader):
                if i == 0:  # Überspringe die Kopfzeile
                    continue

                original_link = row[0]
                profile_link = original_link.replace("marktwertverlauf", "profil")

                # Spieler-ID und Name extrahieren
                parts = profile_link.split("/")
                spieler_id = parts[-1]
                spieler_name = parts[-4].replace("-", " ").title()

                try:
                    # Web-Daten abrufen
                    driver.get(profile_link)
                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    # Relevante Daten extrahieren
                    geb_alter = soup.find("span", string="Geb./Alter:").find_next_sibling("span").text.strip() if soup.find("span", string="Geb./Alter:") else "N/A"
                    geburtsort_element = soup.find("span", string="Geburtsort:")
                    geburtsort = (
                        geburtsort_element.find_next_sibling("span").text.strip() if geburtsort_element else "N/A"
                    )
                    geburtsort = replace_umlauts(geburtsort)

                    staatsbuerger = soup.find("span", string="Staatsbürgerschaft:")
                    staatsbuerger_text = (
                        "/".join(
                            img["title"]
                            for img in staatsbuerger.find_next_sibling("span").find_all("img")
                        )
                        if staatsbuerger
                        else "N/A"
                    )
                    staatsbuerger_text = replace_umlauts(staatsbuerger_text)

                    groesse_element = soup.find("span", string="Größe:")
                    groesse = (
                        groesse_element.find_next_sibling("span").text.strip().replace(",", ".").replace(" m", "")
                        if groesse_element
                        else "N/A"
                    )

                    position = soup.find("span", string="Position:").find_next_sibling("span").text.strip() if soup.find("span", string="Position:") else "N/A"
                    position = replace_umlauts(position)

                    fuss = soup.find("span", string="Fuß:").find_next_sibling("span").text.strip() if soup.find("span", string="Fuß:") else "N/A"
                    fuss = replace_umlauts(fuss)

                    # Zeile schreiben
                    writer.writerow([verein_name, spieler_id, spieler_name, profile_link, geb_alter, geburtsort, staatsbuerger_text, groesse, position, fuss])

                    print(f"Erfasst: {spieler_name} (ID: {spieler_id})")
                except Exception as e:
                    print(f"Fehler beim Verarbeiten von {spieler_name} (ID: {spieler_id}): {e}")

print(f"CSV-Erstellung abgeschlossen. Dateien sind im Ordner: {output_folder}")
driver.quit()
