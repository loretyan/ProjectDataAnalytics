import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Ordner und Webdriver konfigurieren
output_folder = r"output"
chromedriver_path = r"C:\Users\Simon\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

if not os.path.exists(chromedriver_path):
    raise FileNotFoundError(f"Chromedriver nicht gefunden unter: {chromedriver_path}")

os.makedirs(output_folder, exist_ok=True)

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# Ziel-URL
url = "https://www.transfermarkt.ch/robin-zentner/marktwertverlauf/spieler/160963"

data_points = []  # Sicherstellen, dass data_points definiert ist

try:
    # Webseite laden
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # SVG-Element finden
    svg = soup.find("svg", class_="svelte-gaklzv")
    if not svg:
        raise ValueError("Kein <svg>-Tag gefunden.")

    # Achsendaten extrahieren
    x_axis = svg.find("g", class_="axis svelte-3ta12v")
    y_axis = svg.find("g", class_="axis svelte-oklk3z")
    if not x_axis or not y_axis:
        raise ValueError("Erforderliche Achsenabschnitte nicht gefunden.")

    # Maximalwert für Marktwert
    max_market_value_text = y_axis.find_all("text")[-1].text.strip()
    if "M" in max_market_value_text:
        max_market_value = float(max_market_value_text.replace("M", "")) * 1_000_000
    elif "K" in max_market_value_text:
        max_market_value = float(max_market_value_text.replace("K", "")) * 1_000
    else:
        max_market_value = float(max_market_value_text)

    # Frühestes Jahr
    earliest_year_text = x_axis.find_all("text")[0].text.strip()
    earliest_year = float(earliest_year_text)

    # Korrektur des frühesten Jahres
    year_difference = 2025 - earliest_year
    correction = year_difference / 5  # Ein Fünftel des Unterschieds
    earliest_year -= correction

    # Punkte aus "chart-dots" extrahieren
    chart_dots = svg.find("g", class_="chart-dots")
    if not chart_dots:
        raise ValueError("Kein <g>-Tag mit class 'chart-dots' gefunden.")

    for img in chart_dots.find_all("image"):
        try:
            x = float(img["x"])
            y = float(img["y"])
            print(f"Gefundener Punkt: x={x}, y={y}")

            # Prozentwerte berechnen (Y startet bei 0)
            x_percent = (677 - x) / (677 - 50) * 100
            y_percent = (y / 320) * 100

            # Jahr und Marktwert berechnen
            # Höchste Prozentwerte sind am nächsten bei 2025
            year = 2025 - ((100 - x_percent) / 100) * (2025 - earliest_year)
            market_value = (y_percent / 100) * max_market_value

            data_points.append((x, y, round(x_percent, 2), round(y_percent, 2), round(year, 2), round(market_value, 2)))
        except KeyError:
            print("Ein Image-Element hat keine x oder y Attribute. Übersprungen.")
            continue

except Exception as e:
    print(f"Fehler beim Verarbeiten: {e}")
finally:
    driver.quit()

# Ergebnisse speichern, ohne Reihenfolge ändern
output_file = os.path.join(output_folder, "market_value_data.txt")
with open(output_file, "w", encoding="utf-8") as file:
    file.write("x\ty\tx_percent\ty_percent\tyear\tmarket_value\n")
    for point in data_points:
        file.write("\t".join(map(str, point)) + "\n")

print("Verarbeitung abgeschlossen. Ergebnisse in 'market_value_data.txt' gespeichert.")
