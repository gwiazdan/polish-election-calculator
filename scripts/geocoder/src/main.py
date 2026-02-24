from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from .coords_finder import normalize_teryt
from .geocoder import geocode_address
from .writer import append_to_jsonl, save_checkpoint
from .config import (
    CHECKPOINT_FILE,
    OUTPUT_FAILED,
    OUTPUT_SUCCESS,
    PARTY_ROWS,
    RESULTS_FILE,
    STATIONS_FILE,
)

from .validate_points import PointValidator


def load_processed_addresses():
    """Load already processed addresses from checkpoint."""
    processed = set()

    if Path(CHECKPOINT_FILE).exists():
        with open(CHECKPOINT_FILE, "r") as f:
            for line in f:
                processed.add(line.strip())

    return processed

def main():
    Path(OUTPUT_SUCCESS).parent.mkdir(parents=True, exist_ok=True)

    print("Loading dataset...")
    df = pd.read_csv(STATIONS_FILE, sep=";")
    df_results = pd.read_csv(RESULTS_FILE, sep=";")

    df = df[df["TERYT gminy"].notna()]
    df_results = df_results[df_results["Teryt Gminy"].notna()]

    total_votes_col = (
        "Liczba głosów ważnych oddanych łącznie na wszystkich kandydatów "
        "(z kart ważnych)"
    )
    total_pops_col = (
        "Liczba wyborców uprawnionych do głosowania (umieszczonych w spisie, "
        "z uwzględnieniem dodatkowych formularzy) w chwili zakończenia głosowania"
    )

    df_results["teryt_norm"] = df_results["Teryt Gminy"].apply(normalize_teryt)
    df_results["komisja"] = df_results["Nr komisji"].astype(str)
    results_lookup = df_results.set_index(["teryt_norm", "komisja"], drop=False)
    results_lookup_map = results_lookup.to_dict(orient="index")

    df["Ulica"] = df["Ulica"].fillna("")
    df["Numer posesji"] = df["Numer posesji"].fillna("")

    for prefix in ["ul. ", "pl. ", "al. ", "os. "]:
        df["Ulica"] = df["Ulica"].str.removeprefix(prefix)

    df["address_id"] = (
        df["Miejscowość"].astype(str)
        + "_"
        + df["Ulica"].astype(str)
        + "_"
        + df["Numer posesji"].astype(str)
    )
    df["TERYT gminy"] = df["TERYT gminy"].apply(normalize_teryt)
    mask = df["TERYT gminy"].astype(str).str.fullmatch(r"1465(0[2-9]|1[0-9])")
    df.loc[mask, "TERYT gminy"] = "146501"
    df_unique = df.drop_duplicates(subset=["address_id"], keep="first")

    print(f"Total records: {len(df)}")
    print(f"Unique addresses: {len(df_unique)}")

    processed = load_processed_addresses()
    df_todo = df_unique[~df_unique["address_id"].isin(processed)]


    print(f"Already processed: {len(processed)}")
    print(f"To process: {len(df_todo)}")

    if len(df_todo) == 0:
        print("All addresses already geocoded!")
        return

    success_count = 0
    failed_count = 0

    with tqdm(total=len(df_todo)) as pbar:
        with ThreadPoolExecutor(max_workers=8) as executor:
            todo = [
                executor.submit(geocode_row, row, results_lookup_map, total_votes_col, total_pops_col)
                for row in df_todo.to_dict(orient="records")
            ]
            for future in as_completed(todo):
                record, point, method, address_id = future.result()
                if point is not None:
                    record.update({"geometry": point})
                    record.update({"method": method})
                    append_to_jsonl(record, OUTPUT_SUCCESS)
                    success_count += 1
                else:
                    append_to_jsonl(record, OUTPUT_FAILED)
                    failed_count += 1
                save_checkpoint(address_id)
                pbar.update(1)

    print(f"Geocoding finished. Success: {success_count}, Failed: {failed_count}")
            

def geocode_row(row, results_lookup_map, total_votes_col, total_pops_col):
    locality = row["Miejscowość"]
    street = row["Ulica"]
    number = str(row["Numer posesji"]).strip()
    teryt = row["TERYT gminy"]

    if "/" in number:
        number = number.split("/")[0].strip()

    result, method = geocode_address(locality, street, number, teryt)

    numer = row["Numer"]
    key = (teryt, str(numer))
    row_results = results_lookup_map.get(key)

    record = {
        "teryt": teryt,
        "numer": numer,
        "municipality": row["Gmina"],
        "county": row["Powiat"],
        "voivodeship": row["Województwo"],
        "total_votes": (
            row_results[total_votes_col] if row_results is not None else None
        ),
        "total_pops": (
            row_results[total_pops_col] if row_results is not None else None
        ),
    }

    if row_results is not None:
        record.update(
            {
                short: int(row_results[full])
                for full, short in PARTY_ROWS.items()
                if row_results.get(full) is not None
            }
        )

    point = None
    if result and PointValidator.validate_point(teryt,result):
        point = result
    elif result and PointValidator.validate_point(teryt, new_point := PointValidator.inverse_coords(result)):
        point = new_point
        method = "Inverted coords"
    else:
        point = PointValidator.get_centroid(teryt)
        method = "Centroid"

    return record, point, method, row["address_id"]
    
if __name__ == "__main__":
    main()
