# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 10:14:06 2011
This program was written after an request from Bill Adler, then president of the Mass Lobstermen, where he wanted to see temperatures in relation to historical records of each lobstermen.
@author: jmanning

IMPORTANT: Originally assumed you have previously run an old perl routine called "getts_adler_1site.plx" which outputs ALL the data for that site
but, in Dec 2024, I finally got rid of that by extracting via ERDDAP

Modifications made March 2020 to add shipboard climatology as blue line.
"""
from pandas import read_csv,DataFrame,to_datetime,DateOffset
import numpy as np
import matplotlib.mlab as ml
import matplotlib.pyplot as plt
from matplotlib.dates import num2date,MonthLocator, WeekdayLocator, DateFormatter,MONDAY
import datetime as dt
#from ocean_JiM import *
from conversions import f2c
import os
from dateutil.parser import parse

#HARDCODE  define a few variables to annotate figure
site='BN01'
relyear=[0,1,2,3,4] #set to zero for max year, [1] for previous year, or [0,1,2,3,4] for previous five
newfile='output/BN01m60462101.dat' # recent year data
#FUNCTIONS
def getsite_latlon(site):
    df=read_csv('emolt_site.csv')
    df1=df[df['SITE']==site]
    return df1['LAT_DDMM'].values[0],df1['LON_DDMM'].values[0]

def getobs_tempdepth_latlon(lat,lon):
    """
    Function written by Jim Manning to get emolt data from url, return datetime, depth, and temperature.
    this version needed in early 2023 when "site" was no longer served via ERDDAP
    Modified 9/27/24 to accept data within 0.03 degrees (~1/2 mile) of site as:
        https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT_historic_non-realtime_bottom_temperatures.csvp?time%2Clatitude%2Clongitude%2Cdepth%2Csea_water_temperature&latitude%3E=42.48&latitude%3C=42.54&longitude%3E=-70.83&longitude%3C=-70.77
    """
    #url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&latitude='+str(lat)+'&longitude='+str(lon)+'+&orderBy(%22time%22)'
    url='https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT_historic_non-realtime_bottom_temperatures.csvp?time%2Clatitude%2Clongitude%2Cdepth%2Csea_water_temperature&latitude%3E'+str(lat-0.03)+'&latitude%3C'+str(lat+0.03)+'&longitude%3E'+str(lon-0.03)+'&longitude%3C'+str(lon+0.03)+'+&orderBy(%22time%22)'
    df=read_csv(url,skiprows=[1])
    df['time']=df['time (UTC)']
    temp=1.8 * df['sea_water_temperature (degree_C)'].values + 32 #converts to degF
    depth=df['depth (m)'].values
    time=[];
    for k in range(len(df)):
            time.append(parse(df.time[k]))
    print('using erddap')            
    dfnew=DataFrame({'temp':temp,'Depth':depth},index=time)
    return dfnew

# MAIN CODE 
#Basemap years
fig=plt.figure(1)
ax1 = fig.add_subplot(111)
[lat,lon]=getsite_latlon(site)# started using this on 25 May 2023 when NEFSC took away "site" from ERDDAP
t=getobs_tempdepth_latlon(lat,lon)
numyears=str(len(set(t.index.year))) # years at least partially covered
tsy=t.copy() #same year
tsy.index = tsy.index.map(lambda x: x.replace(year=2012))
tsy.sort_index(ascending=True,inplace=True)# sorts by days
tsy['temp'].plot(ax=ax1,label='range over '+numyears+' years')
tda=t.copy() # daily averages
tda=tsy.groupby([tsy.index.month, tsy.index.day]).transform('mean')
tda['temp'].plot(ax=ax1,label='mean over '+numyears+' years',zorder=10,linewidth=4)
# Recent years
maxy=max(t.index.year)
for k in range(len(relyear)):
    toy=t[t.index.year==maxy-relyear[k]]
    toy.index = toy.index.map(lambda x: x.replace(year=2012))
    toy['temp'].plot(ax=ax1,label=str(maxy-relyear[k]))

# Here's where we need to add the current year in cases when it is not yet in the database
if len(newfile)>0:
    print('adding year not yet in database')
    dfnow=read_csv(newfile,header=None)
    dfnow.columns=['SITE','SN','PS','TIME','YD','temp','SALT','DEPTH']
    del dfnow['SITE'];del dfnow['SN'];del dfnow['PS'];del dfnow['YD'];del dfnow['SALT'];del dfnow['DEPTH'];
    dfnow['TIME']=to_datetime(dfnow['TIME'])
    dfnow.set_index('TIME',inplace=True)
    maxyrnow=max(dfnow.index.year)
    dfnow=dfnow[dfnow.index>=dt.datetime(maxyrnow,1,1,0,0,0)]
    dfnow.index = dfnow.index.map(lambda x: x.replace(year=2012))
    #dfnow24.index=dfnow24.index+DateOffset(years=-24)# special case of BF01
    dfnow1=dfnow.rolling(window=24).mean() # special case
    ax1.plot(dfnow1.index,dfnow1['temp'],linewidth=4,color='black',label=str(maxyrnow))
    mintnow=np.min(dfnow1['temp'])# special case
    maxtnow=np.max(dfnow1['temp'])# special case
    #years=np.append(years,2024)
ax1.legend()
plt.savefig('output/'+site+'_ba.png')

