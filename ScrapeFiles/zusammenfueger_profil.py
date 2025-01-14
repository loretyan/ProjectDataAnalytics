import os
import csv

# Pfade
input_folder = r"spieler_profil_pro_verein"
output_folder = r"read_for_import"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, "spieler_profil.csv")

# Header für die konsolidierte Datei
header = [
    "Vereinsname",
    "Spieler_id",
    "Name",
    "Geburtsdatum",
    "Alter",
    "Geburtsort",
    "Staatsbuergerschaft",
    "Groesse in M",
    "Position",
    "Fuss"
]

# Funktion zum Bereinigen von Daten
def clean_value(value):
    """Ersetzt N/A durch null und gibt einen leeren String als null zurück."""
    if value in ("N/A", "", " "):
        return "null"
    return value.strip()

# Funktion zum Bereinigen der Größe
def clean_groesse(value):
    """Bereinigt die Größe und gibt sie als Zahl mit Punkt zurück."""
    if value and "m" in value:
        return value.replace("Â", "").replace(" ", "").replace("m", "").strip().replace(",", ".")
    return "null"

# Konsolidierung der Dateien
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile, delimiter=";")
    writer.writerow(header)  # Schreibe die Header-Zeile

    for filename in os.listdir(input_folder):
        if filename.endswith("_profil.csv"):
            input_file = os.path.join(input_folder, filename)
            with open(input_file, "r", newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile, delimiter=";")
                next(reader)  # Überspringe die Header-Zeile der Eingabedateien

                for row in reader:
                    # Daten bereinigen
                    geb_alter = clean_value(row[4])  # Spalte "Geb./Alter"
                    if " (" in geb_alter:
                        geburtsdatum, alter = geb_alter.split(" (")
                        alter = alter.replace(")", "").strip()
                    else:
                        geburtsdatum, alter = "null", "null"

                    geburtsdatum = clean_value(geburtsdatum)
                    alter = clean_value(alter)
                    geburtsort = clean_value(row[5])
                    staatsbuergerschaft = clean_value(row[6]).replace("Ã¼", "ue").replace("Ã", "A")
                    groesse = clean_groesse(row[7])
                    position = clean_value(row[8])
                    fuss = clean_value(row[9])

                    # Konsolidierte Zeile schreiben
                    writer.writerow([
                        clean_value(row[0]),  # Vereinsname
                        clean_value(row[1]),  # Spieler_id
                        clean_value(row[2]),  # Name
                        geburtsdatum,  # Geburtsdatum
                        alter,  # Alter
                        geburtsort,  # Geburtsort
                        staatsbuergerschaft,  # Staatsbürgerschaft
                        groesse,  # Größe in M
                        position,  # Position
                        fuss  # Fuss
                    ])

print(f"Die konsolidierte Datei wurde erfolgreich erstellt: {output_file}")
