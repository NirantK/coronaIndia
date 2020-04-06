import pathlib

import fire
import googlemaps
import pandas as pd
from tqdm import tqdm


def make_dir():
    """Responsible for creating the folder in which the CSV's will
    be stored in.
    """
    sheets_dir = pathlib.Path.cwd() / "Sheets"

    if not sheets_dir.is_dir():
        sheets_dir.mkdir()


def geocode(excel_sheet, api_key, use_column="Address"):
    """Will take the an excel sheet as input and save a CSV after geocoding the
    address mentioned by the column stated.
    
    Args:
        excel_sheet (str): Path to the sheet that is to be geocoded.
        api_key (str): API key for Google Map Geocoding API
        use_column (str, optional): The column that is to be used as input to API while geocoding. Defaults to "Address".
    """
    make_dir()
    xlsx_name = pathlib.Path.cwd() / excel_sheet
    temp = pd.ExcelFile(xlsx_name)
    sheet_names = temp.sheet_names

    gmaps = googlemaps.Client(key=api_key)

    total_xlsx_count = 0
    total_none_count = 0

    for sheet_name in sheet_names:
        df = pd.read_excel(xlsx_name, sheet_name=sheet_name)
        addresses = df[use_column].tolist()
        count = 0
        total_count = 0
        lats, longs, geocoded = [], [], []
        print(f"{sheet_name} sheet has {len(addresses)} rows")
        print()

        for address in tqdm(addresses):
            try:
                location = gmaps.geocode(address, components={"country": "IN"})
                geocoded.append(True)
            except:
                geocoded.append(False)

            try:
                location = location[0]["geometry"]["location"]
                lats.append(location["lat"])
                longs.append(location["lng"])
            except:
                count += 1
                lats.append(None)
                longs.append(None)
            total_count += 1

        df["Latitude"] = lats
        df["Longitude"] = longs
        df["Geocoded"] = geocoded

        print()
        print(f"Saving {sheet_name} with geocoded address")
        print(f"Unable to geocode - {count}")
        total_none_count += count
        total_xlsx_count += total_count
        print()
        df.to_csv(f"Sheets/{sheet_name}.csv", index=False)

    print(f"Total Addreses - {total_xlsx_count}")
    print(f"Total Addreses unable to geocode - {total_none_count}")


if __name__ == "__main__":
    fire.Fire(geocode)
