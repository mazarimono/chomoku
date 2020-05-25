from datetime import datetime 

import dash  
import dash_core_components as dcc  
import dash_html_components as html 
import plotly.express as px 

import pandas_datareader.data as web  

from app import app 
from dash.dependencies import Input, Output

st_stress = web.DataReader("STLFSI2", "fred", start=datetime(1994,1,1))
high_yeild = web.DataReader("BAMLH0A0HYM2", "fred", start=datetime(1996,12,1))
st_stress["Date"] = st_stress.index 
high_yeild["Date"] = high_yeild.index 

layout = html.Div([
    dcc.RadioItems(id="stress_selector", 
    options=[{"label": "サンフランシスコ連銀ストレス指数", "value": "st_stress"},
            {"label": "ハイイールドスプレッド", "value": "high_yeild"}
    ],
    value="st_stress"
    ),
    dcc.Graph(id="stress_graph")
])

@app.callback(Output("stress_graph", "figure"),
            [Input("stress_selector", "value")])
def update_stress_graph(selected_value):
    if selected_value == "st_stress":
        fig = px.line(st_stress, x="Date", y="STLFSI2")
        fig.update_xaxes(rangeslider_visible=True)
        return fig
    else:
        fig = px.line(high_yeild, x="Date", y="BAMLH0A0HYM2")
        fig.update_xaxes(rangeslider_visible=True)
        return fig 


