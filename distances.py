### we need json and urllib to unpack the telematics data
import sys
import json
import urllib.request as ul

#import geopy.distance as geop


### the input URL with telematics data
#target_url = 'https://sdcimages.s3.yandex.net/test_task/data'

target_url = sys.argv[1]


### define function to calculate distances
def hdistance(point1,point2):
    from math import sin, cos, sqrt, atan2, radians
    R = 6373.0

    lat1 = radians(point1[0])
    lon1 = radians(point1[1])
    lat2 = radians(point2[0])
    lon2 = radians(point2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


### define lists to segment data from file 
pilot_ts = []
pilot_switch= []
geo_ts = []
geo_lon = []
geo_lat = []

### read all data to 'lines' 
try: 
  data = ul.urlopen(target_url)
except ul.HTTPError as exception:
  print(exception)  
  print("Wrong URL")  
  exit()
lines = data.readlines()

### the segmentation of lines on 'control_switch' info vs geo info   
for line in lines:
    
 js1 = json.loads(line) 
 ts = int(js1['ts']/1e9)   

 if 'geo' not in js1:
  pilot_ts.append(ts)
  pilot_switch.append(js1['control_switch_on']) 

 else:   
  geo_ts.append(ts)
  geo_lat.append(js1['geo']['lat'])
  geo_lon.append(js1['geo']['lon'])

### we can round timestamps to '1 sec' precision 
### and get unique values of the 'control_switch' status and geo info, that correspond to ts

### unique timestamps with 1 sec precision
ts_uniq = list(dict.fromkeys(pilot_ts))  
ts_uniq.sort()

switch_uniq = []
lat = []
lon = []

for i in ts_uniq:   
 for t in range(len(pilot_ts)):
  if i == pilot_ts[t]:
   switch_uniq.append(pilot_switch[t])    
   break  
 for g in range(len(geo_ts)):
  if i == geo_ts[g]:     
   lat.append(geo_lat[g]) 
   lon.append(geo_lon[g])
   break

# calculate distance for 'control_switch' on and off
dist_on = 0
dist_off = 0

for d in range(len(ts_uniq)-1):
 co_1 = (lat[d], lon[d])
 co_2 = (lat[d+1], lon[d+1])
 if switch_uniq[d+1]==True:   
#   dist_on = dist_on + geop.distance(co_1,co_2).km
  dist_on = dist_on + hdistance(co_1,co_2)  
 else:   
  dist_off = dist_off + hdistance(co_1,co_2)

if ((dist_on!=0) and (dist_off!=0)): 
 print(dist_on)
 print(dist_off)
else:
 print("Unnable to define distances") 
