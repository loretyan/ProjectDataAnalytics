import os
import csv

# Ordner konfigurieren
input_folder = r"spieler_v2_seasons"
output_folder = r"seas"
output_csv = os.path.join(output_folder, "combined_seasons.csv")

# Erstelle den Ausgabeordner, falls er nicht existiert
os.makedirs(output_folder, exist_ok=True)

# Finde alle CSV-Dateien im Eingabeordner
csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

if not csv_files:
    raise FileNotFoundError(f"Keine CSV-Dateien im Ordner {input_folder} gefunden.")

# Kombinierte CSV-Datei erstellen
with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
    writer = None

    for csv_file in csv_files:
        file_path = os.path.join(input_folder, csv_file)

        with open(file_path, "r", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=';')
            header = next(reader)  # Überspringe die Headerzeile

            if writer is None:
                # Schreibe den Header nur einmal
                writer = csv.writer(outfile, delimiter=';')
                writer.writerow(header)

            for row in reader:
                writer.writerow(row)

print(f"Alle CSV-Dateien erfolgreich kombiniert und gespeichert in {output_csv}")
