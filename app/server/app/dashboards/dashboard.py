import pandas as pd
import pickle
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

with open('app/data/data.p', 'rb') as f:
    df = pickle.load(f)

def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
            'https://fonts.googleapis.com/css?family=Lato'
        ]
    )

    dash_app.layout = html.Div([
        html.H6("US Representatives")
    ])

    return dash_app.server
