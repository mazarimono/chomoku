import dash  
import os 
import dash_core_components as dcc   
import dash_html_components as html 
import plotly.express as px  
from dash.dependencies import Input, Output 
from dash.exceptions import PreventUpdate 
import pandas as pd  

from app import app 

map_token = os.getenv("MAPBOX_TOKEN")

px.set_mapbox_access_token(map_token)

toyo_cropnavi = pd.read_csv("src/toyohashi_crop_ame.csv", index_col=0)
fire_rain = pd.read_csv("src/toyohashi_2020_01-03_all.csv", index_col=0)
toyo_geo = pd.read_csv("src/toyohashi_geo_data.csv", index_col=0)

fig = px.scatter_mapbox(toyo_geo, lat="lat", lon="lon", hover_data=["名称"], text="名称", height=600, zoom=11, size="size")

d_style = {"width": "75%", "margin": "auto"}
two_side = {"width": "49%", "display": "inline-block"}

def make_daily_data(df):
    df["dt"] = pd.to_datetime(df["dt"])
    data = pd.pivot_table(df, values="value", columns="place", index="dt")
    data = data.resample("D").sum()
    data1 = data.reset_index()
    data1 = data1.melt(id_vars="dt")
    return data, data1 

layout = html.Div([
    html.Div([
        html.H1("クロップナビとアメダスの比較"),
        dcc.Dropdown(
            id="drop1",
            options = [{"value": col, "label": col} for col in toyo_cropnavi.columns],
            value=["気温", "温度1"],
            multi=True,
            style=d_style
        ),
        html.Div([
        dcc.Graph(id="graph1", style=two_side),
        dcc.Graph(id="graph2", style=two_side),
        dcc.Graph(id="graph3", style=two_side),

        ]),
    ]),

    html.Div([
        html.H1("消防署データとアメダスの比較"),
        dcc.RadioItems(
            id="radio",
            options=[{"label": i, "value": i} for i in ["10m", "daily"]],
            value="10m"
        ),
        dcc.Dropdown(
            id="drop2",
            options=[{"value": col, "label": col} for col in fire_rain["place"].unique()],
            value=["中消防署", "アメダス"],
            multi=True,
            style=d_style
        ),
        html.Div([
            dcc.Graph(id="graph4", style=two_side),
            dcc.Graph(id="graph5", style=two_side),
            dcc.Graph(id="graph6", style=two_side)
        ])
    ]),


    html.Div([

        html.H1("各計測の位置"),
        dcc.Graph(figure=fig)

    ])

], style={"margin": "1%"})

@app.callback(
    Output("graph1", "figure"), Output("graph2", "figure"), Output("graph3", "figure"),
    Input("drop1", "value")
)
def update_graph1(selected_values):
    if len(selected_values) > 0:
        fig1 = px.line(toyo_cropnavi, x= toyo_cropnavi.index, y=selected_values) 
        selected_df = toyo_cropnavi[selected_values]
        fig2 = px.scatter_matrix(selected_df)
        fig3 = px.imshow(selected_df.corr(), title="データ間の相関")
        return fig1, fig2, fig3 
    raise PreventUpdate

# 10分とデイリーを分けられるようにする。
# 日付でレンジを決められるようにする
@app.callback(
    Output("graph4", "figure"), Output("graph5", "figure"), Output("graph6", "figure"),
    Input("drop2", "value"), Input("radio", "value")
)
def update_graph2(selected_values, radio_value):
    if len(selected_values) > 0:
        if radio_value == "10m":
            selected_df = fire_rain[fire_rain["place"].isin(selected_values)]
            pivot_df = selected_df.pivot_table(values="value", columns=["place"], index="dt")
            pivot_corr = pivot_df.corr()
            fig3 = px.line(selected_df, x= "dt", y="value", color="place") 
            fig4 = px.scatter_matrix(pivot_df)
            fig5 = px.imshow(pivot_corr)
            return fig3, fig4, fig5
        elif radio_value == "daily":
            data1, data2 = make_daily_data(fire_rain)
            selected_df = data2[data2["place"].isin(selected_values)]
            matrix_data = data1[selected_values]
            fig6 = px.line(selected_df, x="dt", y="value",color="place")
            fig7 = px.scatter_matrix(matrix_data)
            fig8 = px.imshow(matrix_data.corr(), title="データ間の相関")
            return fig6, fig7, fig8  
    raise PreventUpdate

