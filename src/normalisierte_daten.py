from pathlib import Path
from decimal import Decimal
import pandas as pd

# Wo Daten holen und speichern?
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

html_file = DATA_DIR / "unnormalisierte_daten.html"

# HTML lesen und zu einer DataFrame in Pandas umwandeln
tables = pd.read_html(html_file)
df_raw = tables[0]

# ffill füllt leere Zeilen mit dem Wert aus der Zeile darüber
# rowspan wird aufgelöst
''' 
df_1nf inhalt / Jede Series:
  - Bestellnummer
  - Bestelldatum
  - Kundennummer
  - Kundenname
  - Kundenadresse
  - Produktnummer
  - Produktbezeichnung
  - Menge
  - Einzelpreis
  - Hersteller
  - Hersteller-Land
  - Versandkosten
  - Gesamtkosten 
  '''
df_3nf = df_raw.ffill()

# Für die genauigkeit Geldwerte als Decimal ausgeben (werden damit zum Objekt):
for col in ["Einzelpreis", "Versandkosten", "Gesamtkosten"]:
    df_3nf[col] = df_3nf[col].astype(str).apply(Decimal)

# Tabellen für 3. NF:
df_kunden = df_3nf[["Kundennummer", "Kundenname", "Kundenadresse"]].drop_duplicates()

df_bestellungen = df_3nf[
    ["Bestellnummer", "Bestelldatum", "Kundennummer", "Versandkosten", "Gesamtkosten"]
].drop_duplicates()

df_produkte = df_3nf[
    ["Produktnummer", "Produktbezeichnung", "Hersteller"]
].drop_duplicates()

df_hersteller = df_3nf[
    ["Hersteller", "Hersteller-Land"]
].drop_duplicates()

df_positionen = df_3nf[
    ["Bestellnummer", "Produktnummer", "Menge", "Einzelpreis"]
]

# prüfen, dass es nur eine Bestellnummer zu einer Produktnummer gibt
assert df_positionen[["Bestellnummer", "Produktnummer"]].duplicated().sum() == 0

OUTPUT_DIR.mkdir(exist_ok=True)

df_kunden.to_csv(OUTPUT_DIR / "kunden_3nf.csv", index=False)
df_bestellungen.to_csv(OUTPUT_DIR / "bestellungen_3nf.csv", index=False)
df_produkte.to_csv(OUTPUT_DIR / "produkte_3nf.csv", index=False)
df_hersteller.to_csv(OUTPUT_DIR / "hersteller_3nf.csv", index=False)
df_positionen.to_csv(OUTPUT_DIR / "bestellpositionen_3nf.csv", index=False)

print("Kunden:", df_kunden.shape)
print("Bestellungen:", df_bestellungen.shape)
print("Produkte:", df_produkte.shape)
print("Hersteller:", df_hersteller.shape)
print("Positionen:", df_positionen.shape)
print(df_3nf.dtypes)