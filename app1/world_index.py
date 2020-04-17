import pandas_datareader.data as web
from datetime import datetime
import pandas as pd
import plotly.express as px

import dash_html_components as html 
import dash_core_components as dcc 
from dash.dependencies import Input, Output 

from app import app 

spx = web.DataReader("^GSPC", "yahoo")
hsi = web.DataReader("^HSI", "yahoo")
nikkei = web.DataReader("^N225", "yahoo")
kospi = web.DataReader("^KS11", "yahoo")
aug = web.DataReader("^AXJO", "yahoo")
brazil = web.DataReader("^BVSP", "yahoo")
indo = web.DataReader("^BSESN", "yahoo")
china = web.DataReader("000001.SS", "yahoo")
index_list = ["SPX", "HSI", "NIKKEI", "KOSPI", "AUG", "BRAZIL", "INDIA", "CHINA"]

world_dff = pd.concat([spx["Close"], hsi["Close"], nikkei["Close"], kospi["Close"], aug["Close"], brazil["Close"], indo["Close"], china["Close"]], axis=1)
world_dff.columns=index_list
world_dff = world_dff["2020"]

world_dff = world_dff.dropna().copy()
world_dff = world_dff / world_dff.iloc[0, :] * 100

world_dff["date"] = world_dff.index
world_dff["count"] = range(len(world_dff))
world_dff.index = range(len(world_dff))
world_dff = world_dff.melt(id_vars=["date", "count"])

layout = html.Div([

    html.H1("世界のインデックス比較"),

    dcc.Dropdown(id="world_index_dropdown",
        options=[{"label": i, "value": i} for i in world_dff.variable.unique()],
        value=["NIKKEI", "SPX", "HSI"],
        multi=True
    ),

    dcc.RadioItems(
        id="world_index_radio",
        options=[{"label": i, "value": i} for i in ["日付", "日数"]],
        value="日付"
    ),
    dcc.Graph(id="world_index_graph")
], style={"padding": "3%"})

@app.callback(Output("world_index_graph", "figure"),
        [
            Input("world_index_dropdown", "value"),
            Input("world_index_radio", "value")])
def update_world_graph(world_drop_value,world_radio_value):
    dff = world_dff[world_dff["variable"].isin(world_drop_value)]

    if world_radio_value == "日付":
        return px.line(dff, x="date", y="value", color="variable")
    else:
        return px.line(dff, x="count", y="value", color="variable")


