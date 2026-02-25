from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from .coords_finder import normalize_teryt
from .geocoder import geocode_address
from .writer import append_to_jsonl
from .config import (
    OUTPUT_FAILED,
    OUTPUT_SUCCESS,
    PARTY_ROWS,
    RESULTS_FILE,
    STATIONS_FILE,
    FINAL_FILE,
    TOTAL_POPS_COL,
    TOTAL_VOTES_COL
)

from .validate_points import PointValidator


def load_processed_addresses():
    """Load already processed addresses from checkpoint."""
    processed = set()

    if Path(OUTPUT_SUCCESS).exists():
        data = pd.read_json(OUTPUT_SUCCESS, lines=True)
        processed = set(data['address_id'])
    return processed


def main():
    Path(OUTPUT_SUCCESS).parent.mkdir(parents=True, exist_ok=True)

    print("Loading dataset...")
    df = pd.read_csv(STATIONS_FILE, sep=";")
    df_results = pd.read_csv(RESULTS_FILE, sep=";")
    df_results = df_results.rename(columns={
        "Kod TERYT": 'Teryt Gminy',
        "Numer": "Nr komisji"
    })
    df = df.rename(columns={
        "Numer": "Nr komisji"
    })
    df = df[df["TERYT gminy"].notna()]
    df_results = df_results[df_results["Teryt Gminy"].notna()]


    df_results["TERYT gminy"] = df_results["Teryt Gminy"].apply(normalize_teryt)
    party_cols = [col for col in PARTY_ROWS if col in df_results.columns]
    results_lookup = df_results[["TERYT gminy", "Nr komisji", TOTAL_POPS_COL, TOTAL_VOTES_COL]+party_cols]

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
    df_unique = df.drop_duplicates(subset=["address_id"], keep="first")

    print(f"Total records: {len(df)}")
    print(f"Unique addresses: {len(df_unique)}")

    processed = load_processed_addresses()
    df_todo = df_unique[~df_unique["address_id"].isin(processed)]

    print(f"Already processed: {len(processed)}")
    print(f"To process: {len(df_todo)}")

    success_count = 0
    failed_count = 0

    with tqdm(total=len(df_todo)) as pbar:
        with ThreadPoolExecutor(max_workers=20) as executor:
            todo = [
                executor.submit(geocode_row, row)
                for row in df_todo.to_dict(orient="records")
            ]
            for future in as_completed(todo):
                record, point, method = future.result()
                if point is not None:
                    record.update({"geometry": point})
                    record.update({"method": method})
                    append_to_jsonl(record, OUTPUT_SUCCESS)
                    success_count += 1
                else:
                    append_to_jsonl(record, OUTPUT_FAILED)
                    failed_count += 1
                pbar.update(1)

    print(f"Geocoding finished. Success: {success_count}, Failed: {failed_count}")
    df_processed = pd.read_json(OUTPUT_SUCCESS, lines=True)
    df_processed = df_processed.set_index('address_id', drop=True)
    df_final = (df[['TERYT gminy', 'Nr komisji', 'address_id']].copy()
        .merge(df_processed[['geometry']], left_on='address_id', right_index=True, how='left')
        .merge(results_lookup, on=["TERYT gminy", "Nr komisji"], how='left')
    )
    df_final = df_final.sort_values(by=["TERYT gminy", "Nr komisji"], ignore_index=True)

    df_final = df_final.rename(columns=PARTY_ROWS)
    df_final = df_final.rename(columns={
        TOTAL_POPS_COL: "total_pops",
        TOTAL_VOTES_COL: "total_votes",
        "TERTY gminy": "teryt",
        "Nr komisji": "num"
    })
    df_final.to_csv(FINAL_FILE, index=False)

def geocode_row(row):
    locality = row["Miejscowość"]
    street = row["Ulica"]
    number = str(row["Numer posesji"]).strip()
    teryt = row["TERYT gminy"]

    if "/" in number:
        number = number.split("/")[0].strip()

    result, method = geocode_address(locality, street, number, teryt)

    record = {
        "address_id": row["address_id"]
    }

    point = None
    if result and PointValidator.validate_point(teryt, result):
        point = result
    elif result and PointValidator.validate_point(
        teryt, new_point := PointValidator.inverse_coords(result)
    ):
        point = new_point
        method = "Inverted coords"
    else:
        point = PointValidator.get_centroid(teryt)
        method = "Centroid"

    return record, point, method


if __name__ == "__main__":
    main()
