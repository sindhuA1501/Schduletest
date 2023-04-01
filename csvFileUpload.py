# importing the required modules
import glob
import requests as req
import os
import time
# specifying the path to csv files
path = "/home/pi/Downloads/Schduletest"

f = open('/home/pi/Downloads/Schduletest/AdsManager.txt', 'r')
detectData = eval(f.read())
f.close()
siteId = detectData['Device_details']['siteId']
deviceUnitId = detectData['Device_details']['deviceId']
# csv files in the path
files = glob.glob(path + "/*.csv")
print(files)

jsonData = {'file'}
for filepath in files:
    filename = filepath.split('/')[-1]

    url = "http://usmgmt.iviscloud.net:777/ProximityAdvertisement/uploadCsvFile_1_0"

    payload = {'siteId': siteId,
               'deviceId': deviceUnitId}
    files = [
        ('file', (filename, open(filepath, 'rb'), 'text/csv'))
    ]
    headers = {}

    response = req.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)
    print(response.status_code)
    if response.status_code == 200:
        os.remove(filepath)
