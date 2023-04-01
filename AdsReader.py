import requests as req
import os
import shutil
import subprocess
import wget
import geocoder
from datetime import datetime
import argparse

from ClearScreen import *

parser = argparse.ArgumentParser(description='Process some values.')
parser.add_argument('deviceId',
                    help='an integer for the accumulator')
parser.add_argument('deviceMode',
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
deviceId = args.deviceId
deviceMode = args.deviceMode
    # global previous_response, media_files, media_index, media_size, media_prefix
media_prefix = str(deviceMode)+'-'
mode = str(deviceMode)
print("media_prefix start:", media_prefix)
getApi = 'http://usmgmt.iviscloud.net:777/ProximityAdvertisement/getAdsUpdateInfo_1_0/?deviceId='+ str(deviceId)
current_response = req.get(getApi).json()
print("API getAdsUpdateInfo response:", current_response , ' for ' , deviceId)

if current_response['ads_update_info']['f_deviceMode']:
    # update media prefix
    media_prefix = current_response['ads_update_info']['f_deviceMode'] + '-'
    mode = current_response['ads_update_info']['f_deviceMode']

# extract the root path of the media files
root_path = current_response['ads_update_info']['f_path']

with open("/home/pi/Downloads/Schduletest/DurationFile.txt", 'r') as file_read:
    lines = file_read.readlines()
    print("File Data-Download:",lines)


# download media files and store it in temporary directory
for lst in current_response['ads_update_info']["ads_list"]:
    video_path = os.path.join(root_path, lst['f_ads'])
    print("video_path:", video_path)
    found =0 
    if lst['f_statusList'][0] == 'A':
        print("File Data-verification-start")
         
        print("lines:", lines)
########Checking for exisitng file in Duration file , if exists, check duration values and write 
        for ads in lines: 
            print("Ads from DFILE:", ads.split('#')[0])
            print("NEW ADS       :",lst['f_ads'])
            if ads.split('#')[0] == lst['f_ads']:
                 found = 1
                 break

        if found ==0 or lines == []:
            with open("/home/pi/Downloads/Schduletest/DurationFile.txt", 'a') as dur_file:
                wget.download(video_path, out='/home/pi/Downloads/Schduletest/media/' + lst['f_ads'])
                duration = lst['f_ads'] + '#' + lst['fdurationList']
                print("NO FILES case -line:",duration)
                dur_file.write(duration)
                dur_file.write('\n')
                dur_file.close()
                        
                  

        
    elif lst['f_statusList'][0] == 'R':
        if os.path.exists('/home/pi/Downloads/Schduletest/media/' + lst['f_ads']):
            os.remove('/home/pi/Downloads/Schduletest/media/' + lst['f_ads'])
            # delete matching content from Duration file for the deleted file
            with open("/home/pi/Downloads/Schduletest/DurationFile.txt", 'r') as file:
                lines = file.readlines()

            # delete matching content
            content = lst['f_ads']
            print("Content:", content)
            with open("/home/pi/Downloads/Schduletest/DurationFile.txt", 'w') as file:
                for line in lines:
                    # readlines() includes a newline character
                    #if line.strip("\n") != content:
                    if line.find(content) != -1:
                        pass
                    else:
                        file.write(line)

                                # update media list with existing folder
print("TEST STARTS")
# prefix = media_prefix + ('' if media_prefix == 'BS-' else weather_prefix)
prefix = media_prefix
print(prefix)
media_files = [os.path.join('/home/pi/Downloads/Schduletest/media', file) for file in sorted(os.listdir('/home/pi/Downloads/Schduletest/media')) if
               file.startswith(prefix)]

media_index = 0
media_size = len(media_files)

# update sunc status to server
#req.post('http://usmgmt.iviscloud.net:777/ProximityAdvertisement/setAdsUpdateInfo/?deviceId='+ str(deviceId), 'Synced')
req.put('http://usmgmt.iviscloud.net:777/ProximityAdvertisement/setAdsUpdateInfo/?deviceId='+ str(deviceId))


# update earlier response with current response
previous_response = current_response

#open global file in writing mode
from datetime import datetime
print("Writing to file", datetime.now())
#AdsModeFile = open('AdsFile.txt','w')
#AdsModeFile.write(mode)
#AdsModeFile.close()

with open('/home/pi/Downloads/Schduletest/AdsFile.txt','w') as outFile1:
    outFile1.write(mode)
    outFile1.close()
print("Wrote to file-1")
