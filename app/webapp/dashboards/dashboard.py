import dash
import dash_table
import pandas as pd

# TODO Add data

def create_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
            'https://fonts.googleapis.com/css?family=Lato'
        ]
    )

    # TODO Add Dash layout
    dash_app.layout = None

    return dash_app.server