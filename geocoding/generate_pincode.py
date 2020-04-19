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


def send_reverese_geocoding_request(lat, lng, gmaps):
    """Responsible for sending the request to GMaps API to reverser geocode
    
    Args:
        lat (float): Latitude
        lng (float): Longitude
        gmaps (Object): gmaps object with declared API key
    
    Returns:
        dict: Response recieved from API,
        bool: Whether we could connect to API
    """
    valid_data_recieved = True
    try:
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
    except:
        logging.warning(f"Failure in reaching the API - {(lat,lng)}")
        valid_data_recieved = False
        reverse_geocode_result = None
    return reverse_geocode_result, valid_data_recieved


def retrieve_pincodes_from_response(reverse_geocode_result):
    """This takes the raw response from the API and gathers all the possible pincodes returned by the API
    
    Args:
        reverse_geocode_result (dict): Response from GMaps API
    
    Returns:
        List: List of all the possible pincodes
    """
    codes = []
    result_dicts = reverse_geocode_result[0]["address_components"]
    for result_dicts_complete in reverse_geocode_result:
        result_dicts = result_dicts_complete["address_components"]
        for result_dicts in result_dicts:
            if "postal_code" in result_dicts["types"]:
                codes.append(result_dicts["long_name"])
    return codes


def reverse_geocode(csv_sheet, api_key, output_file="AssamPincode.csv"):
    """Function which uses GMap Geocoding API to find the pincode using given latitude longitude.
    Saves in the same CSV sheet passed as parameter.
    
    Args:
        csv_sheet (str): CSV sheet that needs to be reverse geocoded for pincodes
        api_key (str): API Key to access the GMap API
        output_file (str, optional): Name of the new CSV to be stored as. Defaults to 'AssamNewAddressPincode'.
    """
    gmaps = googlemaps.Client(key=api_key)
    csv_sheet = pathlib.Path(csv_sheet)
    csv_sheet = csv_sheet.resolve()
    df = pd.read_csv(csv_sheet)
    lats, lngs = df["Latitude"].tolist(), df["Longitude"].tolist()
    postal_codes, pincode_verify = [], []
    is_assam = []
    nocode_count, nancount, success = 0, 0, 0

    def verify_ifnan(lat, lng):
        """Simply verifies if the given lat, lng is nan or not.
        If nan. Appends the neccessary content to three lists
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
        
        Returns:
            Boolean : True if the sent lat, lng were nan
        """
        if math.isnan(lat) or math.isnan(lng):
            pincode_verify.append(True)
            postal_codes.append(None)
            is_assam.append(None)
            logging.info("Could not find pincode for NaN values")
            nancount += 1
            return True
        return False

    def get_required_code(codes):
        """Takes the List of all the possible pincodes and selects the pincode for Assam

        TODO: Maintain a mapping of state to pincode and take the state as input.
        
        Args:
            codes (List): Collection of all pincodes reccieved from the API
        """
        if len(codes) == 0:
            logging.warning(f"API returned no postal code value - {(lat,lng)}")
            postal_codes.append(None)
            is_assam.append(None)
            nocode_count += 1
            return
        for code in codes:
            if str(code)[0] == "7":
                postal_codes.append(code)
                is_assam.append(True)
                return
        postal_codes.append(codes[0])
        is_assam.append(False)
        return

    for lat, lng in tqdm(zip(lats, lngs)):
        # Verify that the current lat, lng is not nan.
        if verify_ifnan(lat, lng):
            continue

        # Lat, Lng is not nan. It can sent to the GMaps Geocoding API for reverse geocoding.
        # send_reverese_geocoding_request will do that and return the raw response back.
        reverse_geocode_result, valid_data_recieved = send_reverese_geocoding_request(
            lat, lng, gmaps
        )

        # Make sure that we were able to successfully connect to the GMaps API and got a valid
        # response back.
        if not valid_data_recieved:
            pincode_verify.append(False)
            postal_codes.append(None)
            is_assam.append(None)
            continue

        # Valid respoonse was srecieved after successfully connecting to the API
        pincode_verify.append(True)

        # Clean the raw response recieved from the GMaps geocoding API. Filter out all the possible pincodes
        # sent back by the API. Out of all the codes pick the first pincode that matches an Assam pincode
        # (Assam pincode - starts with '7'). If no Assam pincode found mark it false for is_assam and pick the first pincode.
        try:
            codes = retrieve_pincodes_from_response(reverse_geocode_result)
            get_required_code(codes)
            if postal_codes[-1] is None:
                continue
            success += 1
        except:
            postal_codes.append(None)
            nocode_count += 1
            logging.warning(f"API returned no postal code value - {(lat,lng)}")

    df["pincode"] = postal_codes
    df["is_assam"] = is_assam
    logging.info(
        f"API Reached. But No pincode recorded. - {nocode_count} rows out of {len(df)}"
    )
    logging.info(
        f"Pincoded Addresses - {len(postal_codes)} , Success={success}, NaNCount={nancount}"
    )

    if len(set(pincode_verify)) > 1:
        logging.warning("There were failures when trying to reach the API.")
        df["pincode_verify"] = pincode_verify

    df.to_csv(output_file)


if __name__ == "__main__":
    fire.Fire(reverse_geocode)
