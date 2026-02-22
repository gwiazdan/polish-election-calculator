URL = "https://services.gugik.gov.pl/uug"
STATIONS_FILE = "data/raw/obwody_glosowania_utf8.csv"
RESULTS_FILE  = "data/raw/protokoly_po_obwodach_utf8.csv"
OUTPUT_SUCCESS = "data/processed/geocoded_success.jsonl"
OUTPUT_FAILED = "data/processed/geocoded_failed.jsonl"
CHECKPOINT_FILE = "data/processed/.checkpoint"

GEODATA_FILE = "zip://data/raw/00_jednostki_administracyjne.zip!A03_Granice_gmin.shp"

PARTY_ROWS = {
    'BIEJAT Magdalena Agnieszka': 'nowa_lewica',
    'BRAUN Grzegorz Michał': 'kkp',
    'HOŁOWNIA Szymon Franciszek': 'pl2050', 
    'MENTZEN Sławomir Jerzy': 'konfederacja',
    'NAWROCKI Karol Tadeusz': 'pis', 
    'TRZASKOWSKI Rafał Kazimierz': 'ko',
    'ZANDBERG Adrian Tadeusz': 'razem'
}
