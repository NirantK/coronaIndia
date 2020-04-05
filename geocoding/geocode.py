import pandas as pd
import googlemaps
import os

if not os.path.isdir("Sheets"):
    os.mkdir('Sheets')

# Add the sheet name that you want to geocode here.
xlsx_name = "ReportedTravel.xlsx"

temp = pd.ExcelFile(xlsx_name)
sheet_names = temp.sheet_names

gmaps = googlemaps.Client(key=' --- Add API Key here --- ')

total_xlsx_count = 0
total_none_count = 0

for sheet_name in sheet_names:
    df = pd.read_excel(xlsx_name, sheet_name=sheet_name)
    
    # If you have another column that is to be used to geocode - enter that
    # inplace of 'Address'
    addresses = df['Address'].tolist()
    count = 0
    total_count = 0
    lats, longs, geocoded = [], [], []
    print(f"{sheet_name} sheet has {len(addresses)} rows")
    print()

    for address in addresses:
        try:
            location = gmaps.geocode(address, components={"country": "IN"})
            geocoded.append(True)
        except:
            geocoded.append(False)

        try:
            location = location[0]['geometry']['location']
            lats.append(location['lat'])
            longs.append(location['lng'])
        except:
            count+=1
            lats.append(None)
            longs.append(None)
            
        total_count += 1
        
        if total_count%50==0:
            print(f"Geocoded {total_count} rows in {sheet_name}")

    df['Latitude'] = lats
    df['Longitude'] = longs
    df['Geocoded'] = geocoded

    print()
    print(f"Saving {sheet_name} with geocoded address")
    print(f"Unable to geocode - {count}")
    total_none_count+=count
    total_xlsx_count+=total_count
    print()
    df.to_csv(f"Sheets/{sheet_name}.csv", index=False)

print(f"Total Addreses - {total_xlsx_count}")
print(f"Total Addreses unable to geocode - {total_none_count}")