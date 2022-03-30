import ssl
from urllib.request import urlopen
import json

import pandas as pd
import plotly.express as px


# ----------------------------------------------------------------------------
# Function to LOAD Geoserver data and convert it to dataframe
# ----------------------------------------------------------------------------
def get_geoserver_data(geoserver_url):
    # Hand https certification issue
    context = ssl._create_unverified_context()

    # store the data from the geoserver url call as json object
    response = urlopen(geoserver_url, context=context)
    geoserver_json = json.loads(response.read())

    # Extract data from properties of features and convert to dataframe
    geoserver_data_list = []
    for feature in geoserver_json['features']:
        geoserver_data_list.append(feature['properties'])
    geoserver_data = pd.DataFrame(geoserver_data_list)

    return geoserver_data

# ----------------------------------------------------------------------------
# Function to create choropleth map
# ----------------------------------------------------------------------------

def generate_choropleth(df,df_location_col, geojson, geojson_properties_location, df_map_value_col, color_continuous_scale="Reds",opacity=.75 ):
    featureidkey = "properties." + geojson_properties_location
    fig = px.choropleth_mapbox(df, geojson=geojson, locations=df_location_col,
                               featureidkey=featureidkey,
                               color=df_map_value_col,
                               color_continuous_scale=color_continuous_scale,
                               mapbox_style="carto-positron",
                               zoom=4.8, center = {"lat": 31.3966, "lon": -99.1213},
                               opacity=0.5,
                              )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=900, height=700)
    return fig
