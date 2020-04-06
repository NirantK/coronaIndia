import fire
import pandas as pd


def cleaner(excel_sheet):
    """Will combine all the CSV's formed during the geocoding process
    
    Args:
        excel_sheet (str): The excel sheet that was geocoded
    """
    temp = pd.ExcelFile(excel_sheet)
    sheet_names = temp.sheet_names

    maindf = pd.read_csv(f"Sheets/{sheet_names[0]}.csv")
    maindf = maindf.drop("Geocoded", axis=1)

    total = len(maindf)
    for sheet_name in sheet_names[1:]:
        df = pd.read_csv(f"Sheets/{sheet_name}.csv")
        df = df.drop("Geocoded", axis=1)
        maindf = pd.concat([maindf, df])
        total += len(df)

    print(total, len(maindf))

    maindf.to_csv(f"Sheets/{excel_sheet.split('.')[0]}.csv")


if __name__ == "__main__":
    fire.Fire(cleaner)
