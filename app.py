# ----------------------------------------------------------------------------
# PYTHON LIBRARIES
# ----------------------------------------------------------------------------
# Data Loading and Cleaning
import ssl
from urllib.request import urlopen
import json

import pandas as pd
import plotly.express as px

# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_daq as daq

# import local python functions
from data_processing import *


# ----------------------------------------------------------------------------
# Geoserver API urls
# ----------------------------------------------------------------------------
# api call to geoserver
disasters_url = "https://geonode.tdis.io/geoserver/SHMP/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=SHMP%3ATotal_Disaster_Declarations&maxFeatures=500&outputFormat=application%2Fjson&PROPERTYNAME=(fid,county,total_disasters,total_flood,total_fire,total_tornado,total_hurricane,total_coastal_storm,total_drought,total_freezing)"


# ----------------------------------------------------------------------------
# LOAD TX COUNTIES GEOMETRIES FROM PLOTLY GEOJSON
# ----------------------------------------------------------------------------
# Get Plotly counties geojson
url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
response = urlopen(url)
counties = json.loads(response.read())

# Extract Texas Counties
tx_counties_features = []
for county in counties['features']:
    if county['properties']['STATE'] == '48':
        tx_counties_features.append(county)
tx_counties = {'type':'FeatureCollection', 'features': tx_counties_features}


# ----------------------------------------------------------------------------
# APP Settings
# ----------------------------------------------------------------------------

external_stylesheets_list = [dbc.themes.SANDSTONE, 'https://codepen.io/chriddyp/pen/bWLwgP.css'] #  set any external stylesheets

app = Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                suppress_callback_exceptions=True
                )

# ----------------------------------------------------------------------------
# DASH APP LAYOUT FUNCTION
# ----------------------------------------------------------------------------

def serve_layout():
    # Get Data
    disasters = get_geoserver_data(disasters_url)
    disasters_map_options = list(disasters.columns)[2:]

    # Create data dictionary for data_store
    data_dictionary = {'disasters': disasters.to_dict('records')}



    # Page Layout
    page_layout =  html.Div([
        # Store data
        dcc.Store(id='store',data=data_dictionary),

        dbc.Row([
            dbc.Col([
                html.H1('SHMP Mapping Visualization')
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                id='dropdown-columns',
                   options=[
                       {'label': i, 'value': i} for i in disasters_map_options
                   ],
                   value = str(disasters_map_options[0])
                ),
            ], width=3)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='div-map'),
            ])
        ]),
    ])

    return page_layout

app.layout = serve_layout


# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------

@app.callback(
    Output('div-map', 'children'),
    Input('dropdown-columns', 'value'),
    State('store','data')
)
def update_map(selected_column, data):
    data_dict = data['disasters']
    data_df = pd.DataFrame(data_dict)
    map_fig = generate_choropleth(data_df,'county', tx_counties, 'NAME', selected_column, color_continuous_scale="Viridis" )
    map_div = html.Div([
        html.H2('Map for ' + selected_column),
        dcc.Graph(figure=map_fig)
    ])
    return map_div


# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
