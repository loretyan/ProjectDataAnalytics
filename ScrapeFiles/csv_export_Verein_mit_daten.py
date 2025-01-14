import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Pfad zum ChromeDriver
CHROME_DRIVER_PATH = r"C:\Users\Simon\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Selenium Webdriver konfigurieren
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service)

# URL der Bundesliga-Vereine-Seite
URL = "https://www.transfermarkt.ch/bundesliga/startseite/wettbewerb/L1"
driver.get(URL)
time.sleep(5)  # Zeit zum Laden der Seite

# Vereine und zugehörige Daten extrahieren
vereine = []
rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'items')]/tbody/tr")
for row in rows:
    try:
        verein_name = row.find_element(By.XPATH, ".//td[2]//a").text
        verein_url = row.find_element(By.XPATH, ".//td[2]//a").get_attribute("href")
        kader = row.find_element(By.XPATH, ".//td[3]//a").text
        durchschnittsalter = row.find_element(By.XPATH, ".//td[4]").text.replace(",", ".")
        legionäre = row.find_element(By.XPATH, ".//td[5]").text
        durchschnittlicher_marktwert = row.find_element(By.XPATH, ".//td[6]").text.replace(" Mio. €", "").replace(",", ".")
        durchschnittlicher_marktwert = float(durchschnittlicher_marktwert) * 1_000_000
        gesamtmarktwert = row.find_element(By.XPATH, ".//td[7]//a").text.replace(" Mio. €", "").replace(",", ".")
        gesamtmarktwert = float(gesamtmarktwert) * 1_000_000

        vereine.append({
            "Verein": verein_name,
            "URL": verein_url,
            "Kader": kader,
            "Durchschnittsalter": durchschnittsalter,
            "Legionäre": legionäre,
            "Durchschnittlicher Marktwert in Euro": int(durchschnittlicher_marktwert),
            "Gesamtmarktwert in Euro": int(gesamtmarktwert)
        })
    except Exception as e:
        print(f"Fehler beim Verarbeiten einer Zeile: {e}")
        continue

# CSV-Datei speichern mit Semikolon als Trennzeichen und Leerzeichen nach dem Trennzeichen
output_csv = "vereine.csv"
with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=vereine[0].keys(), delimiter=";")
    writer.writeheader()
    for verein in vereine:
        # Hinzufügen von Leerzeichen nach Semikolon
        row = {key: f"{value}" for key, value in verein.items()}
        writer.writerow(row)

# Selenium beenden
driver.quit()
