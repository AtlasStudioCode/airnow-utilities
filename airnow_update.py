# import the ArcGIS API for Python and the helper functions module
import arcpy
from airnow_defs import *

# set workspace for ArcGIS
arcpy.env.workspace = r'C:/Users/Danny/Documents/ArcGIS/Projects/WildfireAirQuality/WildfireAirQuality.gdb'
# allow output to overwrite existing files
arcpy.env.overwriteOutput = True

# define global variables for the temporary directory, the current datetime, and the hosted web feature layer for the air quality index contours
temp_dir = r'C:/Users/Danny/Documents/ArcGIS/Projects/WildfireAirQuality/Temp'
date = get_current_hour()
aqi_fc = r'https://services5.arcgis.com/HsPYt5e9Y4Fx5sP3/arcgis/rest/services/AirQuality/FeatureServer/0'

# request the current air quality index contours from AirNow and convert the returned KML file to a file geodatabase feature class
arcpy.AddMessage("CONVERT KML")
convert_kml(date, temp_dir)

# get the color class for each feature
arcpy.AddMessage("GET COLORS")
color_class, lyr = get_color_class(temp_dir)

# set the color class attribute for each feature
arcpy.AddMessage("SET COLORS")
fc = set_color_class(color_class, lyr)

# dissolve features with the same color class into one
arcpy.AddMessage("DISSOLVE")
dissolve(fc, 'dissolve_fc', temp_dir)

# clip the feature class to the boundaries of the United States
arcpy.AddMessage("CLIP")
clip('dissolve_fc', 'clip_fc')

# set the datetime attribute for all features
arcpy.AddMessage("SET DATETIME")
set_datetime('clip_fc', date)

# clear the hosted web feature layer of all previous features
arcpy.AddMessage("CLEAR")
clear(aqi_fc)

# append the formatted local feature class to the hosted web feature layer
arcpy.AddMessage("APPEND")
append('clip_fc', aqi_fc)

arcpy.AddMessage("SUCCESS")