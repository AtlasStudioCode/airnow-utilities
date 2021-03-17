# import the ArcGIS API for Python and other modules
import arcpy, os, requests, time
from datetime import datetime, timedelta

def get_current_hour():
    # return formatted date string for the current hour
    now = datetime.now() - timedelta(hours = 1)
    return now.strftime('%Y-%m-%dT%H')

def get_query_url(base_url, params):
    # create a query url for the airnow api request
    query_url = base_url + '?'
    first_pair = True
    for key, value in params.items():
        if first_pair:
            query_url += key + '=' + value
            first_pair = False
        else:
            query_url += '&' + key + '=' + value
    return query_url

def get_request_data(date):
    # get the returned KML data from the airnow api request
    aqi_url = 'http://www.airnowapi.org/aq/kml/Combined/'
    usa_bbox = '-178.217598,18.921786,-66.969271,71.406235'
    srs = 'EPSG:4326'
    api_key = '0D27FF29-A4A9-4B25-A98E-0B00F5C968FF'

    payload = {
        'DATE': date,
        'BBOX': usa_bbox,
        'SRS': srs,
        'API_KEY': api_key
    }

    query_url = get_query_url(aqi_url, payload)
    r = requests.get(query_url)

    if "WebServiceError" in r.text:
        arcpy.AddMessage(r.text)
    else:
        return r

def convert_kml(date, temp_dir):
    # convert kml to feature class and layer file within the temporary directory
    r = get_request_data(date)

    temp_kml = os.path.join(temp_dir, 'temp.kml')
    with open(temp_kml, 'w') as f:
        f.write(r.text)

    arcpy.conversion.KMLToLayer(temp_kml, temp_dir, 'temp')

def get_color_class(temp_dir):
    # return color class dictionary for each feature
    colors = {
        'Y': {'RGB': [255, 255, 0, 100]},
        'O': {'RGB': [255, 126, 0, 100]},
        'R': {'RGB': [255, 0, 0, 100]},
        'P': {'RGB': [153, 0, 76, 100]},
        'M': {'RGB': [126, 0, 35, 100]}
    }

    lyrFile = arcpy.mp.LayerFile(os.path.join(temp_dir, 'temp.lyrx'))
    lyr = lyrFile.listLayers()[1]
    sym = lyr.symbology

    color_class = {}

    for grp in sym.renderer.groups:
        for itm in grp.items:
            rgb = itm.symbol.color['RGB']
            for k, v in colors.items():
                if (rgb[0] == v['RGB'][0]) and (rgb[1] == v['RGB'][1]) and (rgb[2] == v['RGB'][2]) and (rgb[3] == v['RGB'][3]):
                    color_class[itm.label] = k
    
    return color_class, lyr

def set_color_class(color_class, lyr):
    # add color class field and set values for each feature
    fc = lyr.dataSource

    arcpy.AddField_management(fc, 'COLOR_CLASS', 'TEXT')

    cursor = arcpy.UpdateCursor(fc)

    for row in cursor:
        colorValue = color_class[str(row.getValue('SymbolID'))]
        row.setValue('COLOR_CLASS', colorValue)
        cursor.updateRow(row)

    del cursor, row

    return fc

def dissolve(in_fc, out_fc, temp_dir):
    # dissolve input feature class by color class field
    arcpy.Dissolve_management(in_fc, out_fc, 'COLOR_CLASS')

def clip(in_fc, out_fc):
    # clip input features to united states boundary
    arcpy.Clip_analysis(in_fc, 'usa_boundary', out_fc)

def set_datetime(fc, date):
    # add datetime field and set values for each feature
    datetime = date.replace('T', ' ') + ':00:00'

    arcpy.AddField_management(fc, "DATETIME", "DATE")

    cursor = arcpy.UpdateCursor(fc)

    for row in cursor:
        row.setValue("DATETIME", datetime)
        cursor.updateRow(row)

    del cursor, row

def clear(fc):
    # delete all rows in the feature class
    arcpy.DeleteRows_management(fc)

def append(in_fc, out_fc):
    # append rows from the input feature class to the target feature class
    arcpy.Append_management(in_fc, out_fc, 'NO_TEST')