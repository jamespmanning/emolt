# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:28:34 2013
Making annual mean temperature plot
working with the output from "getemolt"
@author: jmanning

Modified in Oct 2014 to work with ERDDAP data
"""
import numpy as np
import matplotlib
from dateutil.parser import parse
#from pydap.client import open_url
from pandas import DataFrame,read_csv,to_datetime,concat
from matplotlib.dates import num2date
from matplotlib import pyplot as plt
from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.dates as dates
import sys
#sys.path.append('mygit/modules')
from conversions import c2f,fth2m
from dateutil import tz
import pytz

###### HARDCODES #########
maxnumyr=2 # maximum number of years needed to include (ie don't bother otherwise)
lincol=['red','blue','green','black','yellow','cyan','magenta','gray']
#depmean=[183,10,28,63,22,20,31]
#sites=['JS02','BD01','MC02','JT04','AG01','BN01','WD01']

#depmean=[25,22,63]
#sites=['CJ01','AG01','JT04']


#depmean=[48,11,52,44,16,30,26,6]#,11]
#sites=['OD08','BI03','DJ01','TH01','RA01','BF01','OM01','BT01']#,'AC02']

#depmean=[48,11,44,16,30,26,6,11]
#sites=['OD08','BI03','TH01','RA01','BF01','OM01','BT01','AC02']

depmean=[43]


sites=['BS02']
sites=['MF02']
sites=['DJ02']
sites=['DK01']
sites=['CJ01']
sites=['BT01']
sites=['BF02']
sites=['AC02']
sites=['TS02']
sites=['JA01']
sites=['OD08']
sites=['GS01']
sites=['BF01']
sites=['BI03']
sites=['AG01']
sites=['BC02']
sites=['JS02','JS06']
sites=['JC01']
sites=['CP01']
newfile='output/JA01m60271701.dat'
newfile='output/BS02m60332202.dat'
newfile='output/MF02m60091902.dat'
newfile='output/DJ02m49139902.dat'
newfile='output/DK01m60252301.dat'
newfile='output/CJ01m60422401.dat'
newfile='output/BT01m91071701.dat'
newfile='output/BF02m87870502.dat'
newfile='output/AC02m60051402.dat'
newfile='output/TS02m91001102.dat'
newfile='output/JA01m91121801.dat'
newfile='output/OD08m60321308.dat'
newfile='output/GS01m60402001.dat'
newfile='output/BF01m90982001.dat'
newfile='output/BI03m60311003.dat'
newfile='output/AG01m60374401.dat'
newfile='output/BC02m87861102.dat'
newfile='output/JS06m60482606.dat'
newfile='output/JC01m91062301.dat'
newfile='output/CP01m87881801.dat'
sitelabel="".join(sites)
#leg=['Sprague Downeast','Alley Mid-Coast','Brown Mass Bay']
#leg=['Carter','Gamage','Tripp']
leg=['']
####################################
depmin,depmax=[],[] # this defines a range of acceptable depths for this site
for k in range(len(depmean)):
  depmin.append(int(fth2m(depmean[k])-0.10*fth2m(depmean[k]))) #meters
  depmax.append(int(fth2m(depmean[k])+0.10*fth2m(depmean[k]))) #meters
  if depmin[k]==depmax[k]:
     depmin[k]=depmin[k]-2
     depmax[k]=depmax[k]+2

def getsite_latlon(site):
    df=read_csv('emolt_site.csv')
    df1=df[df['SITE']==site]
    return df1['LAT_DDMM'].values[0],df1['LON_DDMM'].values[0]

def getobs_tempdepth_latlon(lat,lon):
    """
    Function written by Jim Manning to get emolt data from url, return datetime, depth, and temperature.
    this version needed in early 2023 when "site" was no longer served via ERDDAP
    """
    url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&latitude='+str(lat)+'&longitude='+str(lon)+'+&orderBy(%22time%22)'
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


def getemolt_by_site_depth(site,depthw):
    """
    Function written by Jim Manning
    borrowed from Huanxin's functions in "getemolt" package
    site: is the 4-digit string like "BD01"
    depth: includes bottom depth and surface depth,like: [80,0].
    Modified Feb 2020 to accept eMOLT.csv file as extracted earlier when ERDDAP is down.
    """
    try:
        url='https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&SITE=%22'+str(site)+'%22&orderBy(%22time%22)'
        #url='eMOLT.csv'
        #print url
        df=read_csv(url,skiprows=[1])
        df=df[(df['depth (m)']>=depthw[0]) & (df['depth (m)']<=depthw[1])]# gets only those depths requested
        time,temp=[],[]
        tempc=df['sea_water_temperature (degree_C)'].values
        for k in range(len(df)):
          #print df['time (UTC)'][k]
          time.append(parse(df['time (UTC)'].values[k])) # added ".values" feb 5, 2018
          #temp.append(c2f(df.sea_water_temperature[k])) # needed to convert to degF comply with old code below
          temp.append(c2f(tempc[k])) # needed to convert to degF comply with old code below
    except: # case of ERDDAP being down
        df=read_csv('../sql/eMOLT.csv',header=None,delimiter='\s+') # use this option when the ERDDAP-read_csv-method didn't work
        temp=df[3].values
        #print 'converting to datetime'
        time=to_datetime(df[0]+" "+df[1])
    tso=DataFrame(temp,index=time) 
    #tso.sort_index(inplace=True)
    return tso

fig=plt.figure()
#matplotlib.rcParams.update({'font.size': 18})
matplotlib.rc('xtick', labelsize=10)
matplotlib.rc('ytick', labelsize=10)
ax=fig.add_subplot(111)
for j in range(len(sites)):
  #tso=getemolt_by_site_depth(sites[j],[depmin[j],depmax[j]])
  [lat,lon]=getsite_latlon(sites[j])# started using this on 25 May 2023 when NEFSC took away "site" from ERDDAP
  tso=getobs_tempdepth_latlon(lat,lon)
  # Here's where we add extra year(s) that are not yet in the database
  dfnow=read_csv(newfile,header=None)
  dfnow.columns=['SITE','SN','PS','TIME','YD','temp','SALT','Depth']
  del dfnow['SITE'];del dfnow['SN'];del dfnow['PS'];del dfnow['YD'];del dfnow['SALT'];
  dfnow['TIME']=to_datetime(dfnow['TIME']).dt.tz_localize(tz.tzutc())#,utc=True)
  dfnow.set_index('TIME',inplace=True)
  #dfnow22=dfnow[dfnow.index<np.datetime64(dt(2023,1,1,0,0,0,pytz.UTC))]
  timezone = pytz.timezone('UTC')
  dfnow22=dfnow[dfnow.index<timezone.localize(to_datetime('01-01-2024'))]#.dt.tz_localize(tz.tzutc())]
  tso = concat([tso,dfnow22])
  #tso = tso.append(dfnow22)  
  yr,day=[],[]
  for k in range(len(tso)):
      yr.append(tso.index[k].year)
      day.append(tso.index[k].dayofyear)
  tso['Year']=yr
  tso['Day']=day    
  tso1=tso.groupby(['Day','Year']).mean().unstack()
  ts=0
  te=366
  if len(list(set(tso['Year'].values)))>maxnumyr:
    for k in list(np.sort(list(set(tso['Year'].values)))):
      tso12=tso1['temp'][k].dropna() # series for this year
      print(str(k),min(tso12.index),max(tso12.index))
      tmi=min(tso12.index) #minimum yearday for this year
      if tmi<te:
        if tmi>ts:
          ts_temp=tmi  #new start yearday
      t=max(tso12.index) #maximum yearday of this year
      if t>ts:
        if t<=te:
          te_temp=t #new max yearday
      if te_temp-ts_temp>60: #if greater than 2 months include it
        ts=ts_temp
        te=te_temp
    #tso2=tso[tso.index.dayofyear>ts]
    #tso3=tso2[tso2.index.dayofyear<te]
    tso2=tso[tso.index.to_series().apply(lambda x: x.dayofyear)>ts]
    tso3=tso2[tso2.index.to_series().apply(lambda x: x.dayofyear)<te]
    #tso3.index.tz=None
    tso3=tso3.astype('float64')
    #tso_a=tso3['temp'].resample('A',how=['count','mean','median','min','max','std'])#,loffset=td(days=-365))# assumes the mean is at the end of the year so I had to fix the x-axis date
    tso_a=tso3['temp'].resample('A').mean()#.ohlc_dict()
    tso_ac=tso3['temp'].resample('A').count()
    tso_a=tso_a[tso_ac.values!=0]
    # note: decided in Dec 2017 that the "loffset" wasn't working so I just subtracted 182 days in the plot statement below instead    
    #tso_a=tso_a.ix[tso_a['count']>np.mean(tso_a['count'])*0.75] # make sure we only include years when at least 75% of this time of year is covered
    #ax.plot(tso_a.index,tso_a['mean'].values,color=lincol[j],linewidth=3,label=sites[j]+' (yeardays '+str(ts)+' through '+str(te)+')')
    #ax.plot(tso_a.index,tso_a['mean'].values,color=lincol[j],linewidth=3,label=leg[j])
    #ax.plot(tso_a.index-td(days=182),tso_a['mean'].values,color=lincol[j],linewidth=3,label=sites[j]+' ('+num2date(ts).replace(year=2000).strftime("%b")+' through '+num2date(te).replace(year=2000).strftime("%b")+')')
    ax.plot(tso_a.index-td(days=182),tso_a.values,color=lincol[j],linewidth=3,label=sites[j]+' ('+num2date(ts).replace(year=2000).strftime("%b")+' through '+num2date(te).replace(year=2000).strftime("%b")+')')
    #tso_a[0]['mean'].plot(linewidth=3,label=sites[j]+' (yeardays '+str(ts)+' through '+str(te)+')')
ax.legend(loc=2,fontsize=14)# upper left
plt.ylabel('Annual Mean Temperature (degF)',fontsize=18)
ax2=ax.twinx()
ax2.set_ylabel('celsius',fontsize=14)
#ax2.set_ylim((np.nanmin(tso_a['mean'].values)-32)/1.8,(np.nanmax(tso_a['mean'].values)+-32)/1.8)
degFrange=ax.get_ylim()  
ax2.set_ylim((degFrange[0]-32)/1.8,(degFrange[1]-32)/1.8)  
ax2.set_xlabel('Year',fontsize=18)
ax.xaxis.set_major_locator(dates.YearLocator(2))
ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))  
plt.ylabel('Annual Mean Temperature (degC)',fontsize=18)
plt.xlabel('Year',fontsize=18)

if depmin!=0:
    plt.title('For instrument depths ='+"%0.0f" % fth2m(depmean[0])+' meters')#rounds to nearest integer depth

    #plt.title('Environmental Monitors on Lobster Traps (eMOLT) examples',fontsize=18)

plt.show()
plt.savefig('./output/'+sitelabel+'_annual.png')
