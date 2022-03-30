# ----------------------------------------------------------------------------
# PYTHON LIBRARIES
# ----------------------------------------------------------------------------
# Data Loading and Cleaning
import ssl
from urllib.request import urlopen
import json
import os # Operating system library
import pathlib # file paths

import pandas as pd
import plotly.express as px

# Dash Framework
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import dash_daq as daq
from flask import request
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL, MATCH

# import local python functions
from data_processing import *

# ----------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent.joinpath("data")
IDRT_COLORSCALE = ['#ffffff', '#e1ebeb', '#c9d5d5', '#b6bfbe', '#a6a8a6', '#99918e', '#8d7b76', '#81645e', '#764e47', '#6a3730', '#5d1f1b', '#500000']
# ----------------------------------------------------------------------------
# Geoserver API urls
# ----------------------------------------------------------------------------
# api call to geoserver
disasters_url = "https://geonode.tdis.io/geoserver/SHMP/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=SHMP%3ATotal_Disaster_Declarations&maxFeatures=500&outputFormat=application%2Fjson&PROPERTYNAME=(fid,county,total_disasters,total_flood,total_fire,total_tornado,total_hurricane,total_coastal_storm,total_drought,total_freezing)"

# ----------------------------------------------------------------------------
# LOAD LOCAL DATA FILE
# ----------------------------------------------------------------------------
disasters = pd.read_csv(os.path.join(DATA_PATH, 'disasters.csv'))

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

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                suppress_callback_exceptions=True
                )

# ----------------------------------------------------------------------------
# DASH APP LAYOUT FUNCTION
# ----------------------------------------------------------------------------

def serve_layout():
    # # Get Data
    # disasters = get_geoserver_data(disasters_url)
    disasters_map_options = list(disasters.columns)[2:]
    #
    # # Create data dictionary for data_store
    # data_dictionary = {'disasters': disasters.to_dict('records')}
    #
    #

    # Page Layout
    page_layout =  html.Div([
        # Store data
        # dcc.Store(id='store',data=data_dictionary),

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
    Input('dropdown-columns', 'value')
    )
def update_map(selected_column):
    map_fig = generate_choropleth(disasters,'county', tx_counties, 'NAME', selected_column )
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
