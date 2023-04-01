from crontab import CronTab
import requests as req
from datetime import datetime

import socket

deviceName = socket.gethostname()

# Importing OS module
import os

# Python get home directory using os module
dir = '/home/pi/Downloads/Schduletest'
logdir = '/home/pi/Downloads/Schduletest/logs'
print("CWD:", dir)
userName = str(os.path.expanduser("~")).split('/')[-1]
print("userName:", userName)
from datetime import datetime

dtime = str(datetime.now())
wDays =''

# *****************  Remove/Cleanup exisitng Advertisements CronTabs  ************
my_cron = CronTab(user=userName)
for job in my_cron:
    print(job, '  ###  ')
    my_cron.remove(job)
    my_cron.write()

# ****************      get the device Advertisement Details to set the CronTab(s)      ********************

api = 'http://usmgmt.iviscloud.net:777/ProximityAdvertisement/getDeviceAdsInfo_1_0/?deviceName=' + deviceName
# api = 'http://usstaging.ivisecurity.com:777/ProximityAdvertisement/getDeviceAdsInfo_1_0/?deviceName='+deviceName
current_response = req.get(api).json()

print("current_response", current_response)

siteId = current_response['Device_details']['siteId']
deviceId = current_response['Device_details']['deviceId']
deviceMode = current_response['Device_details']['deviceMode']
cameraId = current_response['Device_details']['cameraId']

# @@@  Set Device Call Frequency
# Device Ads Manager API call Interval(in minutes)
if current_response['Device_details']['deviceCallFreq'] == None or current_response['Device_details'][
    'deviceCallFreq'] == '':
    deviceCallFreq = 1
else:
    deviceCallFreq = current_response['Device_details']['deviceCallFreq']

# @@@  Set Ads Hour window
adsHours = current_response['Device_details']['adsHours']

startTime, sep, endTime = adsHours.strip().partition("-")
print("startTime:",startTime)
print("Endtime:",endTime)
print(type(adsHours))

# @@@  Set Advertisements Working Days
if current_response['Device_details']['workingDays'] == None or current_response['Device_details']['workingDays'] == '':
    workingDays = str('1,2,3,4,5')  # Mon - 1; Tue - 2 , ...Fri - 5
else:
    workingDays = current_response['Device_details']['workingDays']
    print("WorkingDays:",workingDays)

# @@@  Weather Details
# Weather API call Interval(in minutes)
if current_response['Device_details']['weather_interval'] == None or current_response['Device_details'][
    'weather_interval'] == '':
    weatherCallFreq = 30
else:
    weatherCallFreq = current_response['Device_details']['weather_interval']
    # Weather API Key

weatherApi = 'http://usmgmt.iviscloud.net:777/common/getValuesListByType_1_0?type=Weather_API_Key'
weatherAPIKey = req.get(weatherApi).json()['List_Shown_By_Type_Given'][0]['value']
# weatherAPIKey =current_response['Device_details']['weatherApiKey']


# ****************       Write to Ads-Manager file for other programs     ********************
with open('/home/pi/Downloads/Schduletest/AdsManager.txt', 'w') as mgrFile:
    mgrFile.write(str(current_response))
    mgrFile.close()
print("Wrote to Ads Device Manager File")

# ****************      Delete log files       ********************

logr = current_response['Device_details']['getlogs']
print("Logs value:", logr)
if logr != 1:
    for f in os.listdir(logdir):
        print("about to delete file:", f)
        os.remove(os.path.join(logdir, f))
        print("deleted file        :", f)

if logr == 1:
    #    req.post('http://usmgmt.iviscloud.net:777/ProximityAdvertisement/sendAdsLogsInfo_1_0/?deviceId='+ str(deviceId), 'Synced')
    print("Logs sent")





# ****************     Schedule Jobs using CRONTAB       ****************


# **** scheduling Adsreader Job --- to download advertisements ****

AdsCommand = '/usr/bin/python3 ' + dir + '/AdsReader.py' + ' ' + str(deviceId) + ' ' + deviceMode
# logfile
dtime = dtime[:10] + '_' + dtime[20:]
logFile = ' >>' + dir + '/logs/AdsGet' + dtime + '.log'

AdsJob = AdsCommand + logFile
print("Ads-Job:", AdsJob)

my_cron = CronTab(user=userName)
job = my_cron.new(command=AdsJob, comment='AdsReaderJob')
job.minute.every(deviceCallFreq)

##### hour schedule
for i in range (int(startTime),int(endTime)+1):
    job.hour.also.on(i)
    print("job will run @ :", i)

#b,sep1,wDays= workingDays.strip().partition(",")

##### day of week
for j in range(0,7):
    b,sep1,workingDays = workingDays.strip().partition(",")
    
    if j==0:
        job.dow.on(b)
        print("job will run on day @@@ :", b)
    else: 
        job.dow.also.on(b)
        print("job will run on day ### :", b) 
    print("WorkingDays:",workingDays)
    
    if workingDays =='':
        break
    #else:
    #j=j+1
       

my_cron.write()

# *********** scheduling Weather Job --- to retrieve weather for supplied interval ****

WeatherCommand = '/usr/bin/python3 ' + dir + '/weather.py'  +' '+str(weatherAPIKey)
logFile = ' >>' + dir + '/logs/Wther' + dtime + '.log'

WeatherJob = WeatherCommand + logFile
print("Weather-job:", WeatherJob)

my_cron = CronTab(user=userName)
job = my_cron.new(command=WeatherJob, comment='WeatherJob')
job.minute.every(weatherCallFreq)
my_cron.write()


#REBOOT every day @ 6 am 
# **** scheduling to reboot @6AM everyday ---  ****

rebootCommand = ' /sbin/shutdown -r now'

print("reboot-job :", rebootCommand )

my_cron = CronTab(user=userName)
job = my_cron.new(command=rebootCommand , comment='RebootJob')
job.minute.on(0)
job.hour.on(6)
my_cron.write()



