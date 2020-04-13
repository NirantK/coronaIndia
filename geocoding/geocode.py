import logging
import pathlib

import fire
import googlemaps
import pandas as pd
from tqdm import tqdm

logging.basicConfig(
    filename="geocoding.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logging.info("Logger Setup Complete")


def geocode_df(df, gmaps, use_column):
    addresses = df[use_column].tolist()
    count = 0
    total_count = 0
    lats, longs, geocoded = [], [], []
    logging.info(f"Sheet has {len(addresses)} rows")

    for address in tqdm(addresses):
        try:
            location = gmaps.geocode(address, components={"country": "IN"})
            geocoded.append(True)
        except:
            geocoded.append(False)
            logging.warning(f"Failed to reach API in sheet")

        try:
            location = location[0]["geometry"]["location"]
            lats.append(location["lat"])
            longs.append(location["lng"])
        except:
            count += 1
            lats.append(None)
            longs.append(None)
            logging.info(f"Could not geocode - {address} in sheet")
        total_count += 1

    df["Latitude"] = lats
    df["Longitude"] = longs
    df["Geocoded"] = geocoded

    return df, count, total_count


def geocode_json(data_file, gmaps, use_column):
    json_name = pathlib.Path.cwd() / data_file
    df = pd.read_json(json_name)

    total_none_count = 0
    total_overall_count = 0

    logging.info(f"Starting to geocode json - {data_file}")

    df, count, total_count = geocode_df(df, gmaps, use_column)
    logging.info(f"Saving {data_file} with geocoded address")
    logging.info(f"Unable to geocode in current sheet - {count}")
    total_none_count += count
    total_overall_count += total_count
    df.to_csv(f"Sheets/{data_file.split('.')[0]}.csv", index=False)

    logging.info(f"Total Addreses - {total_overall_count}")
    logging.info(f"Total Addreses unable to geocode - {total_none_count}")


def geocode_excel_sheet(data_file, gmaps, use_column):
    xlsx_name = pathlib.Path.cwd() / data_file
    temp = pd.ExcelFile(xlsx_name)
    sheet_names = temp.sheet_names

    total_xlsx_count = 0
    total_none_count = 0

    logging.info(f"Geocoding a total of - {len(sheet_names)} sheets")

    for sheet_name in sheet_names[:1]:
        df = pd.read_excel(xlsx_name, sheet_name=sheet_name)
        df, count, total_count = geocode_df(df, gmaps, use_column)
        logging.info(f"Saving {sheet_name} with geocoded address")
        logging.info(f"Unable to geocode - {count}")
        total_none_count += count
        total_xlsx_count += total_count
        df.to_csv(f"Sheets/{sheet_name}.csv", index=False)

    logging.info(f"Total Addreses - {total_xlsx_count}")
    logging.info(f"Total Addreses unable to geocode - {total_none_count}")


def geocode(data_file, api_key, use_column="Address"):
    """Will take the an excel sheet as input and save a CSV after geocoding the
    address mentioned by the column stated.
    
    Args:
        data_file (str): Path to the sheet that is to be geocoded.
        api_key (str): API key for Google Map Geocoding API
        use_column (str, optional): The column that is to be used as input to API while geocoding. Defaults to "Address".
    """
    (pathlib.Path.cwd() / "Sheets").mkdir(parents=True, exist_ok=True)
    gmaps = googlemaps.Client(key=api_key)

    if data_file.endswith(".json"):
        geocode_json(data_file, gmaps, use_column)
    else:
        geocode_excel_sheet(data_file, gmaps, use_column)


if __name__ == "__main__":
    fire.Fire(geocode)
