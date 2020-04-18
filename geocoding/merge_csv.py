import fire
import pandas as pd
from pathlib import Path

def merge_csv(sheet_folder, save_as="Merged.csv"):
    """
    Will combine all the CSV's formed during the geocoding process.
    
    Args:
        sheet_folder (str): Path to the folder where all the sheets are stored
        save_as (str, optional): Name of the merged CSV to save as. Defaults to "Merged.csv".
    """
    sheet_folder_path = Path(sheet_folder)
    sheet_folder_path = sheet_folder_path.resolve()
    all_csv_sheets = list(sheet_folder_path.glob('**/*.csv'))

    main_df = pd.read_csv(all_csv_sheets[0]) # Store the first sheet in main_df
    main_df = main_df.drop("Geocoded", axis=1)

    total = len(main_df)
    for csv_sheet in all_csv_sheets[1:]: # Start iterating from the second sheet and keep joining.
        df = pd.read_csv(csv_sheet)
        df = df.drop("Geocoded", axis=1)
        main_df = pd.concat([main_df, df])
        total += len(df)

    print(total, len(main_df))
    save_csv_path = sheet_folder_path / save_as
    main_df.to_csv(save_csv_path)


if __name__ == "__main__":
    fire.Fire(cleaner)
