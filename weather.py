import geocoder
import requests as req
from datetime import datetime
import argparse
parser = argparse.ArgumentParser(description='Process some values.')
parser.add_argument('apikey')

args = parser.parse_args()


lat, lon = geocoder.ip('me').latlng
#apikey = '2a62000b8f9c6ddaf4a13dc91e9717e0'
apikey = args.apikey
apiurl = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&units=metric'
temp_map = {(1, 15): 1, (16, 20): 2, (21, 50): 3}

response = req.get(apiurl).json()
temp = response['main']['feels_like']
timestamp = response['dt']
session = datetime.strftime(datetime.fromtimestamp(timestamp), "%p").upper()
tcs = [tc for tr, tc in temp_map.items() if temp >= tr[0] and temp <= tr[1]]
weather_prefix = session.upper() + 'R' + str(0 if len(tcs) == 0 else tcs[0]) + '-'

print(weather_prefix)

with open('/home/pi/Downloads/Schduletest/weatherFile.txt', 'w') as outFile0:
    outFile0.write(weather_prefix)
    outFile0.close()




