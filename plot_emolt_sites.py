#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 11:53:58 2023

@author: JiM
plots site location for particular eMOLT participant using Cartopy_example.py code on github
"""

import matplotlib.pyplot as plt
#import shapely.geometry as sgeom
import cartopy
import cartopy.crs as ccrs
import pandas as pd

fisher='RW' 
url='https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?SITE%2Ctime%2Clatitude%2Clongitude%2Cdepth%2Csea_water_temperature&SITE%3E=%22'+fisher+'01%22&SITE%3C=%22'+fisher+'99%22'
df=pd.read_csv(url)
listsites=list(set(df['SITE'].values))
lats,lons=[],[]
for k in listsites:
    df1=df[df['SITE']==k]        
    lats.append(df1['latitude (degrees_north)'].values[0])
    lons.append(df1['longitude (degrees_east)'].values[0])

plt.figure(figsize=(8,6))
ax = plt.axes(projection=cartopy.crs.PlateCarree())

ax.add_feature(cartopy.feature.LAND)
ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.COASTLINE)
ax.add_feature(cartopy.feature.BORDERS, linestyle=':')
ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
ax.add_feature(cartopy.feature.RIVERS)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
#ax.set_extent([-20, 60, -40, 40])

ax.set_xlim([int(min(lons)-1.), int(max(lons)+1.)])
ax.set_ylim([int(min(lats)-1.), int(max(lats)+1.)])
#ax.set_xlim([-88., -86.])
#ax.set_ylim([44., 46.])

plt.title('Sites of '+fisher)

plt.scatter(
    x=lons,
    y=lats,
    color="red",
    s=6,
    alpha=1,
    transform=ccrs.PlateCarree()
)

plt.show()