# -*- coding: utf-8 -*-
# emolt2_pd.py this is the Pandas code we use to generate plots for lobstermen
# Written by Yacheng Wang, Jim Manning,
# This is a revision of the old "emolt2.py" which used scikits timeseries

# Note: Beginning in June 2014, this code accesses the ERDDAP server
# so I needed to run merge_emolt_site_sensor.pl after loading the data into NOVA
#
# Note: Beginning in Spring 2017, the Pandas read_csv no longer read ERDDAP urls
# so I manually downloed a csv file using the web interface and called it eMOLT.csv in this directory or the sql directory
#
# Note: In Feb 2020, I added "climatology" to the plot
'''
step0: import modules and hardcodes
step1: read-in data
step2: groupby 'Year'and'Days'
step3: plot figure
'''
#from pydap.client import open_url
from pandas import DataFrame,read_csv,to_datetime,DateOffset
from datetime import datetime as dt, timedelta as td
from matplotlib.dates import num2date
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('xtick', labelsize=14) 
matplotlib.rc('ytick', labelsize=14)
import sys
import matplotlib.dates as dates
#from dateutil import parser
from dateutil.parser import parse
import numpy as np

#from getdata import getemolt_data#####very similar with getemolt_temp
#HARCODES####
site='TS02' # this is the 4-digit eMOLT site code you must know ahead of time
surf_or_bot='bot' #surf, bot, or both


plot_title='Jim Tripp in 115 meters in the Gulf of Maine'
plot_title='Bob Baines in 48 fths off Mid-Coast Maine'
plot_title='Ricky Alley in 16 fths (~29 meters) off Mid-Coast, Maine'
plot_title='Jim Tripp in 62 fths (~114 meters) off Matinicus, Maine'

plot_title='Bruce Fernald in 25 fths (~46 meters) off Little Cranberry Island, Maine'
plot_title='Brian Tarbox in 5 fths (~9 meters) of Casco Bay'
plot_title='Billy Souza in 15 fths (~27 meters) off Cape Cod'
plot_title='Frank Kristy 37 meters (~20fths) in Cape Cod Bay'

plot_title="Ray Joseph @ Jeff Alberts's old site in 14 fths (~25 m) off Cape Cod"
plot_title='Mike Faulkingham in 30 fathoms out of Winter Harbor, Maine'
plot_title='Dave Casoni in 11 fths in Cape Cod Bay'
plot_title='Jon Carter 46 meters (~25fths) off Bar Harbor, Maine'
plot_title='John Drouin in 48 fths off Cutler, Maine'
plot_title='George Sprague  18 meters (~10fths) off Bucks Harbor, Maine'
plot_title="Mark Fernald (at Bruce's old 30 fth site) off Little Cranberry Isle"
plot_title="John Tripp (near Jim's old site JT02) in 59 fths off Matinicus Rock"
plot_title='Bobby Ingalls in 11 fathoms Downeast Maine'
plot_title='Jamie Hallowell in 22 fths off Mid-Coast Maine'
plot_title='Brian Cates in 45 fths off Cutler, Maine'
plot_title='Pete Begley at JS06 in 166 fths (304 meters) Gulf of Maine'
plot_title='Pete Begley at JS02 in 183 fths (334 meters) Gulf of Maine'
plot_title='John Chipman at JC01 in 30 fths off Birch Harbor'
plot_title='Clayton Philbrook in 43 fths (~78 meters) off Matinicus Island, Maine'
plot_title='Mark Fernald at BF01 in 30 fths off Little Cranberry Island, Maine'
plot_title='David Johnson in 23 fths (~42 meters) off South-Coast, Maine'
plot_title='Therese Sauvageau 8 fathoms in Mass Bay'

special='NARR' #sites where only the last decade is plotted to prevent clutter like WHAQ, NARR, etc
newfile='output/CJ01m60422301.dat'# case where we are adding file not yet in the database
newfile='output/BI03m60310903.dat'# case where we are adding file not yet in the database
newfile='output/MF02m60091802.dat'
newfile='output/TH01m49181501.dat'
newfile='output/AG01m60374201.dat'
newfile='output/JS06m49112406.dat'
newfile='output/RA01m39531901.dat'
newfile='output/JT04m56342104.dat'

newfile='output/BT01m91071701.dat'
newfile='output/BF02m87870502.dat'
newfile='output/BS02m91052302.dat'
newfile='output/DK01m60252301.dat'
newfile='output/TS02m91001102.dat'
newfile='output/JA01m91121801.dat'
newfile='output/MF02m60091902.dat'
newfile='output/CJ01m60422401.dat'
newfile='output/AC02m60051402.dat'
newfile='output/OD08m60321308.dat'
newfile='output/GS01m60402001.dat'
newfile='output/BF01m90982001.dat'
newfile='output/JT02m60490202.dat'
newfile='output/BI03m60311003.dat'
newfile='output/AG01m48734301.dat'
newfile2='output/AG01m60374401.dat'
newfile='output/BC02m87861102.dat'
newfile='output/JS06m60482606.dat'
newfile='output/JS02m60472702.dat'
newfile='output/JC01m91062301.dat'
newfile='output/CP01m87881801.dat'
newfile='output/BF01m48662101.dat'
newfile='output/DJ02m91100502.dat'
newfile='output/TS02m39511202.dat'
newfile2=''

#newfile='output/DK01m60252201.dat'# case where we are adding file not yet in the database
def getclim(lat,lon,datet):# get CLIM
    dflat=read_csv(clim_files_directory+'LatGrid.csv',header=None)
    dflon=read_csv(clim_files_directory+'LonGrid.csv',header=None)
    bt=read_csv(clim_files_directory+'Bottom_Temperature/BT_'+datet.strftime('%j').lstrip('0')+'.csv',header=None) # gets bottom temp for this day of year with leading zero removed
    latall=np.array(dflat[0])   # gets the first col (35 to 45)
    lonall=np.array(dflon.loc[0])# gets the first row (-75 to -65) changed "ix to "loc" in Feb 2020
    idlat = np.abs(latall - lat).argmin()# finds the nearest lat
    idlon = np.abs(lonall - lon).argmin()# finds the nearest lon
    #print('bottom clim =','%.3f' % bt[idlon][idlat])
    return bt[idlon][idlat]

def get_dataset(url):
    """
    Just checks to see if the OPeNDAP URL is working
    """
    try:
        dataset = open_url(url)
        print(url+' is avaliable.')
    except:
        print('Sorry, ' + url + 'is not available')
        sys.exit(0)
    return dataset
 
def c2f(*c):
    """
    convert Celsius to Fahrenheit
    accepts multiple values
    """
    if not c:
        c = input ('Enter Celsius value:')
        f = 1.8 * c + 32
        return f
    else:
        f = [(i * 1.8 + 32) for i in c]
        return f   

def getemolt_latlon(site):
    """
    get lat, lon, and depth for a particular emolt site 
    """
    import numpy as np
    urllatlon = 'http://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT_historic_non-realtime_bottom_temperatures.csvp?latitude,longitude,depth&SITE=%22'+str(site)+'%22&distinct()'
    df=read_csv(urllatlon,skiprows=[1])
    dd=max(df["depth (m)"])
    return df['latitude (degrees_north)'][0], df['longitude (degrees_east)'][0], dd

def getobs_tempsalt(site):
    """
    Function written by Jim Manning to get emolt data from url, return datetime, depth, and temperature.
    
    There was evidently an earlier version where a user could also specify an time range. This "input_time" can either contain two values: start_time & end_time OR one value:interval_days
    and they should be timezone aware.    example: input_time=[dt(2003,1,1,0,0,0,0,pytz.UTC),dt(2009,1,1,0,0,0,0,pytz.UTC)]
    
    Modified Nov 2022 to acceptan ascii dump of entire emolt set
    """
    try:
        url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT_historic_non-realtime_bottom_temperatures.csvp?time,depth,sea_water_temperature&SITE=%22'+str(site)+'%22&orderBy(%22time%22)'
        df=read_csv(url,skiprows=[1])
        df['time']=df['time (UTC)']
        temp=1.8 * df['sea_water_temperature (degree_C)'].values + 32 #converts to degF
        depth=df['depth (m)'].values
        time=[];
        for k in range(len(df)):
            time.append(parse(df.time[k]))
        print('using erddap')            
    except:
        try:
            df=read_csv('../sql/eMOLT.csv',header=None,delimiter='\s+') # use this option when the ERDDAP-read_csv-method didn't work
            # see the top of emolt_notes for instructions, requires time depth temp header
            temp=df[3].values
            depth=df[2].values
            #df['time']=pd.to_datetime(df[0]+" "+df[1])
            #('converting to datetime')
            time=to_datetime(df[0]+" "+df[1])
            print('using csv file previously created for this site ')
        except:
            print('using burton & george dump file')
            df=read_csv('input/emolt_dump_nov2022.csv')
            df=df[df['SITE']==site]
            temp=df['TEMP'].values
            for kk in range(len(temp)):
                temp[kk]=temp[kk]*1.8+32
            depth=df['DEPTH'].values
            time=to_datetime(df['TIME'].values)
    dfnew=DataFrame({'temp':temp,'Depth':depth},index=time)
    return dfnew

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


#tsoall=getemolt_data(site)
#tsoall=getobs_tempsalt(site)
[lat,lon]=getsite_latlon(site)# started using this on 25 May 2023 when NEFSC took away "site" from ERDDAP
tsoall=getobs_tempdepth_latlon(lat,lon)

#################add some keys for tso#########################
tsoall['Year']=tsoall.index.year
tsoall['Day']=tsoall.index.dayofyear
tsoall=tsoall.drop(tsoall[tsoall['Day']==366].index)
if (surf_or_bot=='surf') | (surf_or_bot=='both'):
  tso=tsoall[tsoall['Depth']<np.mean(tsoall['Depth'])]# this grabs surface only
elif surf_or_bot=='bot':
  tso=tsoall[tsoall['Depth']>=0.5*np.nanmean(tsoall['Depth'])]# this 80% grabs
del tso['Depth']  # we do not need depth anymore
if site==special:
  tso=tso[tso['Year']>2000] # since we do not want the plot to be too cluttered
tso1=tso.groupby(['Day','Year']).mean().unstack()

#################create the datetime index#################################
date=[]
for i in range(len(tso1.index)-1):
    date.append(parse(num2date(tso1.index[i]).replace(year=2000).isoformat(" ")))
date.append(parse(num2date(tso1.index[len(tso1.index)-2]).replace(year=2000).isoformat(" ")))
'''
to explain the previous few lines.... 
because tso1.index contain(1-366) so when we convert days to datetime format,366 will become 2000/jan/1,
so we delete the last index 366 and copy the last second record.
'''
############### finally, plot the time series ##############################################################
fig=plt.figure(figsize=(10,8))
ax=fig.add_subplot(111)
ax.plot(date,tso1.values)
ax.set_ylabel('fahrenheit',fontsize=16)
ax.set_ylim(np.nanmin(tso1.values),np.nanmax(tso1.values))
#save these values for later incase we need to add other sets
mint=np.nanmin(tso1.values)
maxt=np.nanmax(tso1.values)
for i in range(len(ax.lines)):#plot in different ways
    if i<int(len(ax.lines)/2):# and i<>(len(ax.lines)-1):
        ax.lines[i].set_linestyle('--')
        ax.lines[i].set_linewidth(2)
    elif i>=int(len(ax.lines)/2) and i<(len(ax.lines)-1):
        ax.lines[i].set_linestyle('-')
        ax.lines[i].set_linewidth(2)
    else:
        print(str(i)+' years of data')
        ax.lines[-1].set_linewidth(3)
        ax.lines[-1].set_color('black')
       
years=np.sort(list(set(tso['Year'].values)))# years in the database
# Here's where we need to add the current year in cases when it is not yet in the database
if len(newfile)>0:
    print('adding year not yet in database')
    dfnow=read_csv(newfile,header=None)
    dfnow.columns=['SITE','SN','PS','TIME','YD','TEMP_F','SALT','DEPTH']
    del dfnow['SITE'];del dfnow['SN'];del dfnow['PS'];del dfnow['YD'];del dfnow['SALT'];del dfnow['DEPTH'];
    dfnow['TIME']=to_datetime(dfnow['TIME'])
    dfnow.set_index('TIME',inplace=True)
    #dfnow22=dfnow[dfnow.index<dt(2022,1,1,0,0,0)]# special case of BF01
    dfnow22=dfnow[dfnow.index>=dt(2022,1,1,0,0,0)]
    dfnow22.index=dfnow22.index+DateOffset(years=-22)# special case of BF01
    #dfnow23.index=dfnow23.index+DateOffset(years=-23)
    dfnow221=dfnow22.rolling(window=24).mean() # special case
    #dfnow231=dfnow23.rolling(window=24).mean()
    ax.plot(dfnow221.index,dfnow221['TEMP_F'],linewidth=5,color='black')
    #ax.plot(dfnow231.index,dfnow231['TEMP_F'],linewidth=5,color='black')
    mintnow=np.min(dfnow221['TEMP_F'])# special case
    maxtnow=np.max(dfnow221['TEMP_F'])# special case
    #mintnow=np.min(dfnow231['TEMP_F'])
    #maxtnow=np.max(dfnow231['TEMP_F'])
    years=np.append(years,2022)
    #years=np.append(years,2023)
if ax.get_lines()[-2].get_c()=='black': # we do not want the last two years to be both black
    ax.lines[-2].set_color('red')     



#ax.legend(set(tso['Year'].values),loc='center left', bbox_to_anchor=(.1, .6))
#ax.legend(np.sort(list(set(tso['Year'].values))),loc='best')
# Shrink current axis by 20%
box = ax.get_position()
#ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
#ax.legend(years,loc='center left',fontsize=10,bbox_to_anchor=(0.01, 0.62))#, borderaxespad=0.4)
#ax.legend(years,loc='center left',fontsize=10,bbox_to_anchor=(0.15, 0.6))
ax.legend(years,fontsize=9,bbox_to_anchor=(.15, 0.35))
#ax.legend(np.sort(list(set(tso['Year'].values))),loc='best',fontsize=8)#,bbox_to_anchor=(1.1, 0.5))#, borderaxespad=0.4)
#kk=map(str,list(set(tso['Year'].values)))
#kk.append('clim')
#ax.legend(kk,loc='best',fontsize=12)
#ax.legend(map(str,list(set(tso['Year'].values))).append('clim'),loc='best',fontsize=12)

# For case of "both" surface and bottom, we now plot the bottom case
if surf_or_bot=='both':
  tso=tsoall[tsoall['Depth']>=0.8*np.mean(tsoall['Depth'])]# this 80% grabs
  del tso['Depth']  # we do not need depth anymore
  tso1=tso.groupby(['Day','Year']).mean().unstack()
  date=[]
  for i in range(len(tso1.index)-1):
     date.append(parse(num2date(tso1.index[i]).replace(year=2000).isoformat(" ")))
  date.append(parse(num2date(tso1.index[len(tso1.index)-2]).replace(year=2000).isoformat(" ")))
  #ax3=fig.add_subplot(111)
  #ax3.plot(date,tso1.values,linewidth=1)
  ax.plot(date,tso1.values,linewidth=1)
  for k in range(len(set(tso['Year'].values))):
#     ax3.lines[-k-1].set_linewidth(3) 
#  ax3.lines[-1].set_linewidth(5)
#  ax3.lines[-1].set_color('black')
     ax.lines[-k-1].set_linewidth(2) 
  #ax.lines[-1].set_linewidth(5)
  #ax.lines[-1].set_color('black')
  print('adding year at bottom not yet in database')
  dfnow=read_csv(newfile2,header=None)
  dfnow.columns=['SITE','SN','PS','TIME','YD','TEMP_F','SALT','DEPTH']
  del dfnow['SITE'];del dfnow['SN'];del dfnow['PS'];del dfnow['YD'];del dfnow['SALT'];del dfnow['DEPTH'];
  dfnow['TIME']=to_datetime(dfnow['TIME'])
  dfnow['TIME']=dfnow["TIME"].apply(lambda x: x.replace(year=2000))
  dfnow.set_index('TIME',inplace=True)
  dfnow1=dfnow.rolling(window=24).mean() 
  ax.plot(dfnow1.index,dfnow1['TEMP_F'],linewidth=5,color='black')
  years=np.append(years,2022)
  years=np.append(years,2023)
  if ax.get_lines()[-2].get_c()=='black': # we do not want the last two years to be both black
      ax.lines[-2].set_color('purple') 
  ax.text(dt(2000,7,5,0,0,0),61.5,'Surface',color='white',fontsize=20)
  ax.text(dt(2000,9,25,0,0,0),50.5,'Bottom',color='white',fontsize=20)
ax4=ax.twinx()
#ax4.set_title(site)
#ax4.set_ylabel('celsius')
ax4.set_ylabel('celsius',fontsize=18)
#ax4.set_ylim((np.nanmin(tso1.values)-32)/1.8,(np.nanmax(tso1.values)-32)/1.8)
mint=np.nanmin([mint,mintnow])
maxt=np.nanmax([maxt,maxtnow])
ax4.set_ylim((mint-32)/1.8,(maxt-32)/1.8)
ax.set_ylim(mint,maxt)
# here we add the climatology curve by getting a value each month
'''
print('adding climatology ...')
clim_files_directory='/net/data5/jmanning/clim/'
climt,datett=[],[]
[lat1,lon1,dep]=getemolt_latlon(site)
for k in range(12):
    datett.append(dt(2000,k+1,1,0,0,0))# note that it assumes year 2000
    climt.append(getclim(lat1,lon1,dt(2000,k+1,1,0,0,0)))
datett.append(dt(2001,1,1,0,0,0)) # adds one more point to close out the year
climt.append(climt[0])
ax4.plot(datett,climt,linewidth=4)
'''
'''
below is to format the x-axis
'''
ax.set_xlabel('Month')
#ax.title(site)
#ax.set_title(site+' in 25 fathoms off Bar Harbor')
ax.set_title(plot_title,fontsize=20)
ax.xaxis.set_minor_locator(dates.MonthLocator(bymonth=None, bymonthday=1, interval=1, tz=None))
ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
ax.xaxis.set_major_locator(dates.YearLocator())
ax.xaxis.set_major_formatter(dates.DateFormatter(' '))
patches,labels=ax.get_legend_handles_labels()

#plt.show()
if surf_or_bot=='bot':
  #plt.savefig(site+'.png') 
  #plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'.png')
  plt.savefig('output/'+site+'.png')

  #plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'.ps')
else:
  plt.savefig('output/'+site+'_'+surf_or_bot+'.png')
  #plt.savefig('/net/pubweb_html/epd/ocean/MainPage/lob/'+site+'_'+surf_or_bot+'.ps')
