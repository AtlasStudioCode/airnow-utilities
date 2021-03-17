# AIRNOW-UTILITIES
 
## airnow_defs.py

A collection of helper functions to send API requests, format returned data, format spatial data for web display, and update hosted web feature layers on ArcGIS Online.

## airnow_update.py

Send an API request to AirNow to retrieve contours of the current hourly air quality index across the United States. Then, use the ArcGIS API for Python to format a local feature class with color class and time attributes before pushing this spatial data to a hosted web feature layer on ArcGIS Online for display in a web map application.

## Results

The web map application display of the results of this code can be found at the following link:
[Atlas Studio - United States Wildfire and Air Quality Map](https://www.atlasstud.io/usa-wildfire-air-quality)