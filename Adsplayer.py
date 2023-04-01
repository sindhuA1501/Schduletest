import os
import subprocess
from datetime import datetime
import schedule
import time
import json
# from omxplayer.player importqq OMXPlayer
from pathlib import Path
from time import sleep
import pandas as pd
import socket

# from objdet import count_people_tflite
from detect import *

# socket variables
HEADER = 64

PORT = 6666
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "ec2-18-213-63-73.compute-1.amazonaws.com"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    print("333333333333333", msg)
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))


current_time = str(datetime.now()).split(' ')
timeStamp = datetime.today().strftime("%p")
filename = "/home/pi/Downloads/Schduletest/" + str(timeStamp) + "_AdsManagerData_" + str(current_time[0]) + '_' + str(
    current_time[1]) + ".csv"

###### Initialize variables
media_files = [],
media_index = 0,
media_size = 0
media_prefix = ''
weather_prefix = 'None'
noads_flag = 'F'
ads_flag = 'F'

previous_mode = ''
mode_default = 'BS'
mode = ''
objDetectTimestamp = ''

"""
Read model data from ADSManager.txt
"""
modelData = open("/home/pi/Downloads/Schduletest/AdsManager.txt", "r")
modelData = (eval(modelData.read()))
print("%%%:", modelData)
objectCount = 0
gender = 'Male'
cameraUrl = modelData['Device_details']['cameraUrl']
print("@camurl:", cameraUrl)
width = modelData['Device_details']['width']
height = modelData['Device_details']['height']
modelName = '/home/pi/Downloads/Schduletest/' + modelData['Device_details']['modelName']
print("######################modelName:",modelName)
threshold = modelData['Device_details']['threshold']
maxNo = modelData['Device_details']['maxNo']
objectName = modelData['Device_details']['objectName']
remarks = 'Ads'

# open global file in reading mode

d = {}

adsCsvData = {'siteId': [], 'deviceUnitId': [], 'asset_name': [], 'assetDuration': [], 'adsMode': [], 'objectName': [],
              'objectCount': [], 'weatherPrefix': [], 'ageRange': [], 'gender': [],
              'adPlayedTimestamp': [], 'remarks': []}


def excelFunc():
    df = pd.DataFrame(adsCsvData)
    df.to_csv(filename, index=False, header=True)


schedule.every(1).minutes.do(excelFunc)


def get_pair(line):
    key, sep, value = line.strip().partition("#")
    return key, value


count = ''
cnt = 0

while True:
    # play media one by one
    # noads_flag = 'T'
    ####### READ AdsManagerFile to get the current details for the advertisements
    f = open('/home/pi/Downloads/Schduletest/AdsManager.txt', 'r')
    detectData = eval(f.read())
    f.close()

    ####### READ AdsFile to get the current_mode for the advertisements
    f = open('/home/pi/Downloads/Schduletest/AdsFile.txt', 'r')
    mode = f.read()
    f.close()
    print("Mode from AdsFile:", mode)

    ######  setters for CSV file (Ads logger)

    ageRange = 10
    siteId = detectData['Device_details']['siteId']
    deviceUnitId = detectData['Device_details']['deviceUnitId']

    #### Now set the details based on the Ads Play mode (BS / BSR / ODR)
    if mode == 'BS':
        current_mode = mode
        media_prefix = current_mode + '-'
        #        print("prefix",media_prefix)
        prefix = media_prefix
    if mode == 'BSR':
        current_mode = mode
        weather_prefix1 = open('/home/pi/Downloads/Schduletest/weatherFile.txt', 'r')
        weather_prefix = weather_prefix1.read()
        weather_prefix1.close()
        media_prefix = current_mode + '-' + weather_prefix
        print("prefix", media_prefix)
        prefix = media_prefix
    if mode == 'ODR':
        print("Check for ODR")
        current_mode = mode
        weather_prefix1 = open('/home/pi/Downloads/Schduletest/weatherFile.txt', 'r')
        weather_prefix = weather_prefix1.read()
        weather_prefix1.close()
        media_prefix = current_mode + '-' + weather_prefix
        enable_edgetpu = False
        count = run(str(modelName), str(cameraUrl), int(width), int(height), 1, threshold ,enable_edgetpu)
        print("Count:", count)

        prefix = media_prefix + 'P' + str(count)
        print("*** ODR prefix", prefix)

    if mode == ' ':
        current_mode = mode_default + '-'
    #  print("current_mode:", current_mode)

    #   print('STARTING  playads')
    # update media prefix

    media_files = [os.path.join('/home/pi/Downloads/Schduletest/media', file) for file in
                   sorted(os.listdir('/home/pi/Downloads/Schduletest/media')) if file.startswith(prefix)]
    media_index = 0
    media_size = len(media_files)
    #    print("media_SIZE  :", media_size)

    #    sleep(1)
    if media_files:
        with open("/home/pi/Downloads/Schduletest/DurationFile.txt") as fd:
            d = dict(get_pair(line) for line in fd)
        fd.close()

        #        #print("Duration file #", d)

        f = open('/home/pi/Downloads/Schduletest/AdsFile.txt', 'r')
        #        # e.g., f = open("data2.txt")
        mode = f.read()
        if mode != '':
            current_mode = mode
        f.close()

        #        #print("media file to PLAY #",media_files[media_index],datetime.now())
        for i in media_files:
            # noads_flag = 'F'
            videopath = i
            # play "Download in progress in case of single Advertisements"
            #     print("Download in progress")

            if videopath.split('.')[-1] == 'tmp' and media_size == 1:
                print("Ads is downloading going on")
                """playd = subprocess.Popen(['omxplayer', "/home/pi/Downloads/Schduletest/DoProgress.mp4"],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         close_fds=False)
                playd.stdin.flush()"""
                vlc_cmd = "cvlc --quite"  # or "vlc" if using GUI version
                # video_path = "/path/to/video.mp4"

                # build the subprocess command
                subprocess_cmd = [vlc_cmd, "/home/pi/Downloads/Schduletest/DoProgress.mp4" , "--play-and-exit"]

                # run the subprocess command
                subprocess.call(subprocess_cmd)
                sleep(10)
                print("Ads is downloading---still going on ")
            else:  # if videopath.split('.')[-1] != 'tmp':
                for key, value in d.items():
                    newkey = os.path.join('/home/pi/Downloads/Schduletest/media/' + key)
                    if (newkey == i):
                        print("Ads_played_data =", key, ' : ', datetime.now())
                        sleepx = int(value) + 1
                dtime = str(datetime.now())

                if videopath.split('.')[-1] == 'mp4':
                    adsPlayedTimeStamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                    vid = ''
                    databaseVideoPath = videopath.split('/')[-1]
                    #player = subprocess.Popen(['omxplayer', videopath], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    #                          stderr=subprocess.PIPE, close_fds=False)
                    vlc_cmd = "cvlc"  # or "vlc" if using GUI version
                    #video_path = "/path/to/video.mp4"

                    # build the subprocess command
                    subprocess_cmd = [vlc_cmd, videopath, "--play-and-exit"]

                    # run the subprocess command
                    subprocess.call(subprocess_cmd)
                    #                    #print("playing...!", current_mode)
                    #player.stdin.flush()
                    send(deviceUnitId + '#' + adsPlayedTimeStamp + '#' + databaseVideoPath)
                    sleep(sleepx)

                    # elif videopath.split('.')[-1] == 'jpg':
                    # play = subprocess.Popen(args=["feh", videopath, "-Y", "-B black", "-F", "-Z", "-x"])
                    # sleep(sleepx)
                    # play.terminate()

                    #   Write to CSV file
                    adsCsvData['siteId'].append(str(siteId))
                    adsCsvData['deviceUnitId'].append(str(deviceUnitId))

                    adsCsvData['asset_name'].append(str(databaseVideoPath))
                    adsCsvData['assetDuration'].append(str(sleepx))
                    adsCsvData['adsMode'].append(str(mode))
                    adsCsvData['objectName'].append(str(objectName))
                    adsCsvData['objectCount'].append(str(objectCount))
                    adsCsvData['weatherPrefix'].append(str(weather_prefix))
                    adsCsvData['ageRange'].append(str(ageRange))
                    adsCsvData['gender'].append(str(gender))
                    adsCsvData['adPlayedTimestamp'].append(str(adsPlayedTimeStamp))
                    adsCsvData['remarks'].append(str(remarks))

                    noads_flag = 'F'

        media_index = (media_index + 1) % media_size
        schedule.run_pending()
    else:
        print("essssssssssssssss")
        adsPlayedTimeStamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        #play = subprocess.Popen(['omxplayer', "/home/pi/Downloads/Schduletest/noAds.mp4"], stdin=subprocess.PIPE,
        #                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=False)
        #play.stdin.flush()
        vlc_cmd = "cvlc"  # or "vlc" if using GUI version
        # video_path = "/path/to/video.mp4"

        # build the subprocess command
        subprocess_cmd = [vlc_cmd, "/home/pi/Downloads/Schduletest/noAds.mp4", "--play-and-exit"]

        # run the subprocess command
        subprocess.call(subprocess_cmd)

        send(deviceUnitId + '#' + adsPlayedTimeStamp + '#' + 'noads.mp4')
        sleep(5)

        if noads_flag == 'F':  # and ads_flag == 'T':
            print("noads write to file  :", noads_flag)
            adsCsvData['siteId'].append(siteId)
            adsCsvData['deviceUnitId'].append(deviceUnitId)
            databaseVideoPath = 'noAds.mp4'
            adsCsvData['asset_name'].append(databaseVideoPath)
            adsCsvData['assetDuration'].append(5)
            adsCsvData['adsMode'].append(mode)
            adsCsvData['objectName'].append(objectName)
            adsCsvData['objectCount'].append(objectCount)
            adsCsvData['weatherPrefix'].append(weather_prefix)
            adsCsvData['ageRange'].append(ageRange)
            adsCsvData['gender'].append(gender)
            adsCsvData['adPlayedTimestamp'].append(str(adsPlayedTimeStamp))
            adsCsvData['remarks'].append(remarks)
            noads_flag = 'T'

            print(adsCsvData)
        schedule.run_pending()
        print("Wrote to file   :", noads_flag)

    print('***************** For completed *************')

print('*****************   WHILE LOOP Completed    *************')
