import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px

kakei = pd.read_csv("src/kakei10_long.csv", index_col=0)

from app import app 

layout = html.Div(
    [
        dcc.Dropdown(
            id="why_drop",
            options=[{"label": i, "value": i} for i in kakei.variable.unique()],
            multi=True,
            value=["消費支出"],
        ),
        dcc.Graph(id="why_graph"),
    ], style={'margin': '5%',}
)


@app.callback(Output("why_graph", "figure"), Input("why_drop", "value"))
def update_graph(selected_values):
    selected = kakei[kakei["variable"].isin(selected_values)]
    return px.line(selected, x="date", y="value", color="variable")

