import logging
import os
import requests
import time
import re
import cv2
import sys

lookupDirectory = "C:/Users/Andrea Castillejos/Documents/Python_WeatherPractice/"
lookupURL="https://www.msn.com/de-de/wetter/vorhersage/in-Sindelfingen,Baden-W%C3%BCrttemberg?loc=eyJsIjoiU2luZGVsZmluZ2VuIiwiciI6IkJhZGVuLVfDvHJ0dGVtYmVyZyIsImMiOiJEZXV0c2NobGFuZCIsImkiOiJERSIsImciOiJkZS1kZSIsIngiOiI4Ljk4NDAxNzM3MjEzMTM0OCIsInkiOiI0OC43MDczMzI2MTEwODM5ODQifQ%3D%3D&weadegreetype=C&ocid=winp1taskbar&cvid=4746f21034da4eefc3976cf2c7543768"

sky_to_pictureDescription={
    'bewölkt':'cloudy',
    'regen':'cloudy',
    'schnee':'snow',
    'sonnig':'sunny'}

special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}

def findString(searchString,searchableText):
    try:
        #findall?find
        return re.search(searchString,searchableText,re.IGNORECASE).group(0)
    except:
        return re.search(searchString,searchableText,re.IGNORECASE)

def findSeason():
    currentMonth=int(time.strftime("%m"))

    season_to_month={"spring":range(3,6),
                     "summer":range(6,9),
                     "autumn":range(9,12),
                     "winter":[12,1,2]}
    month_to_season={}

    for k,v in season_to_month.items():
        for individualMonth in v:
            month_to_season.update({individualMonth:k})
            
    return month_to_season[currentMonth]

def getCurrentWeather():
    _r = requests.get(lookupURL).text
    _precip=findString('(?<=isRaining\W{2})(false|true)',_r)    
    _thermal=findString('(?<=currentTemperature\W{3}).*?(?=\")',_r)
    _sky=findString('(?<=skycode\W{4}children\W{3}).*?(?=\")',_r)
    _sky=findString('bewölkt|sonnig|regen|schnee',_sky)
    _shortSummary =findString('(?<=shortSummary\W{3}).*?(?=\"\,\")',_r)
    if(type(_shortSummary)is str):
        _shortSummary=_shortSummary.translate(special_char_map)
    else:
        _shortSummary="Missing description"
        
    if _thermal is None:
        _thermal=findString('(?<=emperature\W{3}).*?(?=\")',_r)
    if _thermal is None:
        _thermal=findString('(?<=\=\")-*?\d+(?=\°C\")',_r)
        
    return float(_thermal), bool(_precip),_sky.lower(),str(_shortSummary)
        
def howCold(_thermal,_season):
    season_to_WarmTempThreshold = {
        "spring":15,
        "summer":25,
        "autumn":15,
        "winter":10
        }

    season_to_ColdTempThreshold = {
        "spring":5,
        "summer":15,
        "autumn":5,
        "winter":0
        }
    if(_thermal > season_to_WarmTempThreshold[_season]):
        return "warm"
    elif(season_to_WarmTempThreshold[_season] > _thermal > season_to_ColdTempThreshold[_season]):
        return "normal"
    elif(_thermal < season_to_ColdTempThreshold[_season]):
        return "cold"
    else:
        print("no thermal found")
        
def howRainy(_precip,_thermal):
    if _precip and _thermal<0:
        return "snow"
    elif _precip and _thermal>0:
        return "rain"
    else:
        return "dry"
        
class currentWeatherDescription:
    def __init__(self):
        self.season=findSeason()
        _thermal,_precip,_sky,_summary= getCurrentWeather()
        self.sky=sky_to_pictureDescription.get(_sky,'sky_is_undefined')
        self.precip=howRainy(_precip,_thermal)    
        self.thermal=howCold(_thermal,self.season)
        self.summary=_summary
        self.imgPath=lookupDirectory+self.season.title()+"/"+self.thermal+"_"+self.precip+"_"+self.sky+".jpg"

        self.img=cv2.imread(self.imgPath, cv2.IMREAD_ANYCOLOR)
        #self.img= cv2.resize(_img, dsize=(300,300), interpolation=cv2.INTER_AREA)
        
def main():
    countdown=10
    minWaited=5
    while countdown>0:
        t1=currentWeatherDescription()
        cv2.imshow(t1.summary, t1.img)
        cv2.waitKey(minWaited*60*1000)
        t2=currentWeatherDescription()
        if(t1.imgPath!=t2.imgPath):
            cv2.imshow(t2.summary, t2.img)
        cv2.waitKey(minWaited*60*1000)
        countdown-=1
        print(str(countdown)+"...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    sys.exit()
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
