import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import TimeoutException

# Pfad zum ChromeDriver
CHROME_DRIVER_PATH = r"C:\Users\Simon\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# ChromeDriver starten
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service)
driver.set_page_load_timeout(120)  # Timeout auf 120 Sekunden setzen

# CSV-Datei lesen
with open("vereine.csv", mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', skipinitialspace=True)
    for row in reader:
        # URL und Vereinsname auslesen
        verein_name = row['Verein']
        verein_url = row['URL']

        print(f"Rufe URL auf: {verein_url}")

        # Retry-Mechanismus für Timeout
        retries = 3
        for attempt in range(retries):
            try:
                # Seite aufrufen
                driver.get(verein_url)
                time.sleep(3)  # Wartezeit, um sicherzustellen, dass die Seite geladen ist

                # Quellcode analysieren
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Links zu Spielern finden
                spieler_links = []
                for td in soup.find_all('td', class_='rechts hauptlink'):
                    a_tag = td.find('a', href=True)
                    if a_tag:
                        spieler_links.append(f"https://www.transfermarkt.ch{a_tag['href']}")

                # Links in CSV speichern
                output_folder = "links_zu_spieler_nach_verein"
                csv_filename = f"{output_folder}/{verein_name}_spieler.csv"
                with open(csv_filename, mode='w', newline='', encoding='utf-8') as output_file:
                    writer = csv.writer(output_file, delimiter=';')
                    writer.writerow(["Spieler-Link"])
                    for link in spieler_links:
                        writer.writerow([link])
                    print(f"Spieler-Links für {verein_name} in {csv_filename} gespeichert.")
                break  # Erfolgreich, Schleife verlassen
            except TimeoutException:
                print(f"Timeout bei {verein_url}, Versuch {attempt + 1} von {retries}")
                if attempt == retries - 1:
                    print(f"Fehler: konnte {verein_url} nach {retries} Versuchen nicht laden.")

# ChromeDriver schließen
driver.quit()
