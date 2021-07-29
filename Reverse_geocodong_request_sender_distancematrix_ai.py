import csv
import datetime
import logging
import requests
import time
import os.path
import sys


BASE_URL = "https://api.distancematrix.ai"

DATA_FILE_PATH = "data.csv"
RESULT_FILE_PATH = "result.csv"
TOKEN_FILE_PATH = "token.txt"

if(os.path.exists(TOKEN_FILE_PATH)!=True):
    print('No token.txt file with API token. Please contact alina.lysykh@distancematrix.ai for help \n')
    exit=input("press close to exit")
    sys.exit()

if(os.path.exists(DATA_FILE_PATH)!=True):
    print('No data.csv file with raw data. Please contact alina.lysykh@distancematrix.ai for help \n')
    exit=input("press close to exit")
    sys.exit()

with open(TOKEN_FILE_PATH, "r") as file:
    API_KEY = file.read()
    print(f'Your API KEY is: "{API_KEY}"')

with open(DATA_FILE_PATH) as f:
   count_data_rows = sum(1 for _ in f) - 1

def load_data():
    count_rows = 0
    data = []
    with open(DATA_FILE_PATH, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='"')
        for idx, row in enumerate(rows):
            if not idx:
                continue

            latitude, longitude = row

            data.append({
                "latitude": "%s" % latitude.replace(',', '.'),
                "longitude": "%s" % longitude.replace(',', '.'),
            })
            count_rows+=1
        print(" \nTotal rows in CSV = %s \n" % (count_rows))
        return data

def make_request(base_url, api_key, latitude, longitude):
    url = "{base_url}/maps/api/geocode/json" \
          "?key={api_key}" \
          "&latlng={latitude}" \
          ",{longitude}".format(base_url=base_url,
                                api_key=api_key,
                                latitude=latitude,
                                longitude=longitude)
    # logging.info("URL: %s" % url)
    result = requests.get(url)
    return result.json()

def main():
    data = load_data()
    n=0
    with open(RESULT_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(
            ['request_time', 'latitude', 'longitude', 'formatted_address'])

        for t in data:
            time.sleep(0)
            request_time = datetime.datetime.now()
            dm_res = make_request(BASE_URL, API_KEY, t['latitude'], t['longitude'])
       
            if dm_res['status'] == 'REQUEST_DENIED':
                if dm_res['error_message'] == 'The provided API key is invalid.':
                    print(dm_res['error_message'])
                    break
            n+=1
            try:
                geo = dm_res['result'][0]['formatted_address']

            except Exception as exc:
                print("%s) Please check if the coordinates in this line are correct" % n)
                # logging.error(str(exc))
                continue

            csvwriter.writerow([
                request_time,
                t['latitude'],
                t['longitude'],
                geo       
            ])
            print("%s) %s -> %s : [geo: %s]" % (n, t['latitude'], t['longitude'], geo))

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    main()

with open(RESULT_FILE_PATH) as f:
   count_result_rows = sum(1 for _ in f) - 1

print(f' \n{count_result_rows} / {count_data_rows} -> Calculated correctly')
print(' \nHelp is needed? Please contact alina.lysykh@distancematrix.ai \n')
exit=input("Press close to exit")