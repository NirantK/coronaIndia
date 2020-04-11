import logging
import math
import pathlib

import fire
import googlemaps
import pandas as pd
from tqdm import tqdm

logging.basicConfig(
    filename="pincoding.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logging.info("Logger Setup Complete")


def reverse_geocode(csv_sheet, api_key):
    """Function which uses GMap Geocoding API to find the pincode using given latitude longitude.
    Saves in the same CSV sheet passed as parameter.
    
    Args:
        csv_sheet (str): Name of file to add pincodes in
        api_key (str): API Key for using GMap API
    """
    gmaps = googlemaps.Client(key=api_key)
    csv_sheet = pathlib.Path.cwd() / csv_sheet
    df = pd.read_csv(csv_sheet)
    lats, lngs = df["Latitude"].tolist(), df["Longitude"].tolist()
    postal_codes, pincode_verify = [], []
    is_assam = []
    count = 0
    nancount = 0
    success = 0
    index = 0
    for lat, lng in tqdm(zip(lats, lngs)):
        index += 1
        if math.isnan(lat) or math.isnan(lng):
            pincode_verify.append(True)
            postal_codes.append(None)
            is_assam.append(None)
            logging.info("Could not find pincode for NaN values")
            nancount += 1
            continue

        try:
            reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
            pincode_verify.append(True)
        except:
            logging.warning(f"Failure in reaching the API - {(lat,lng)}")
            pincode_verify.append(False)
            postal_codes.append(None)
            is_assam.append(None)
            continue

        try:
            codes = []
            result_dicts = reverse_geocode_result[0]["address_components"]
            for result_dicts_complete in reverse_geocode_result:
                result_dicts = result_dicts_complete["address_components"]
                for result_dicts in result_dicts:
                    if "postal_code" in result_dicts["types"]:
                        codes.append(result_dicts["long_name"])
            if len(codes) == 0:
                postal_codes.append(None)
                is_assam.append(None)
                count += 1
                logging.warning(f"API returned no postal code value - {(lat,lng)}")
                continue

            success += 1

            for code in codes:
                if str(code)[0] == "7":
                    postal_codes.append(code)
                    is_assam.append(True)
                    codes = []
                    break
            if len(codes) > 0:
                postal_codes.append(codes[0])
                is_assam.append(False)
        except:
            postal_codes.append(None)
            count += 1
            logging.warning(f"API returned no postal code value - {(lat,lng)}")

    if len(set(pincode_verify)) > 1:
        logging.info("There were failures when trying to reach the API.")
        logging.info(f"API could not find address for - {count} rows out of {len(df)}")
        df["pincode_verify"] = pincode_verify
        df["pincode"] = postal_codes
        df['is_assam'] = is_assam
        df.to_csv("AssamNewAddressPincode.csv")
    else:
        logging.info("No error reaching api")
        logging.info(f"API could not find address for - {count} rows out of {len(df)}")
        logging.info(
            f"Pincoded Addresses - {len(postal_codes)} , Success={success}, NaNCount={nancount}"
        )
        df["pincode"] = postal_codes
        df['is_assam'] = is_assam
        df.to_csv("AssamNewAddressPincode.csv")


if __name__ == "__main__":
    fire.Fire(reverse_geocode)
