import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import ast

import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table

# import dash_alternative_viz as dav
import dash_daq as daq
import numpy as np
import pandas as pd

import plotly.express as px

import plotly.graph_objs as go

from dash.dependencies import Input, Output, State
from app import app 


td_style = {"width": "33%", "margin": "20px"}
two_style = {"width": "50%", "display": "inline-block"}


tabs_styles = {"height": "44px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "lime",
    "color": "white",
    "padding": "6px",
}


### COVID

df_covid = pd.read_csv("./src/kosei.csv", index_col=0, parse_dates=["date"])

df_date = df_covid.groupby("date", as_index=False).count()
df_date = df_date.iloc[:, :2]
df_date.columns = ["date", "count"]
df_date["cumsum"] = df_date["count"].cumsum()

df_place = df_covid.groupby("居住地", as_index=False).count()
df_place = df_place.iloc[:, :2]
df_place.columns = ["place", "count"]
df_place["count"] = df_place["count"].astype("int")
df_place = df_place.sort_values("count")
df_place = df_place[-15:]

# 男女年代別
df_gender = df_covid.groupby(["年代", "性別"], as_index=False).count()
df_gender = df_gender.iloc[:, :3]
df_gender.columns = ["年代", "性別", "患者数"]

df_cyto_table = df_covid.iloc[:, [0, 2, 5, 9, 10, 11]]

# 世界データ

covid_world_data = pd.read_csv("./src/covid_worlddata.csv", index_col=0, parse_dates=["DateRep"])
covid_jp = covid_world_data[covid_world_data["Countries and territories"] == "Japan"]
covid_jp = covid_jp.sort_values("DateRep")
covid_jp["cumsum"] = covid_jp["Cases"].cumsum()
covid_jp = covid_jp[15:]
last_update = covid_jp.iloc[-1, 0].date()

covid_world_cumsum = covid_world_data.groupby("Countries and territories", as_index=False).sum()
covid_world_cumsum = covid_world_cumsum.sort_values("Cases")
covid_world_cumsum = covid_world_cumsum[-30:]


# 日本地域データ

covid_jp_area = pd.read_csv("./src/area_jp.csv")
covid_jp_area = covid_jp_area.sort_values("累計感染者数")
covid_jp_area = covid_jp_area[covid_jp_area["都道府県"] != "総計"]
covid_jp_area = covid_jp_area[-15:]

covid_el = []

for i in range(len(df_covid)):
    covid_el.append(
        {
            "data": {
                "id": f"No.{df_covid.iloc[i, 0]}",
                "label": f"No.{df_covid.iloc[i, 0]} / {df_covid.iloc[i, 5]}",
            }
        }
    )
    contact_list = []
    for i2 in ast.literal_eval(df_covid.iloc[i, -2]):
        if i2.startswith("No."):
            covid_el.append(
                {"data": {"source": f"No.{df_covid.iloc[i, 0]}", "target": f"{i2}"}}
            )


world = html.Div([
    html.Div([
        html.H4("世界の感染者数データ"),
        
        dcc.RadioItems(id="world_all_data",
            options=[{"label": i, "value": i} for i in ["累計", "1日"]],
            value="累計"
        ),
        dcc.Loading([
        dcc.Graph(id="world_graph")
        ], type="cube", color="red"),
    ]),

    html.Div([

        html.H4("各国感染者数"),

        dcc.RadioItems(id="world_covid_data", 
        options=[{"label": i, "value": i} for i in ["累計", "直近1日", "ヒストリカル"]],
        value="累計"
        ),

        html.Div(id="show_world_data"),

        # legendをオフにする方法
        # 各国の日々のデータの推移が見たい。
        # 各国の累計の日々の推移（動かす？）

        # html.H1(id="selected_country_graph")

    ])
])

@app.callback(Output("world_graph", "figure"), [Input("world_all_data", "value")])
def switch_all_graph(switch_data):
    if switch_data == "1日":
        return px.bar(covid_world_data, x="DateRep", y="Cases", color="Countries and territories", title="世界の新規感染者数", template={"layout":{"showlegend": False, "hovermode": "closest"}})
    else:
        cumsum_all = covid_world_data.groupby("DateRep", as_index=False).sum()
        cumsum_all["cumsum"] = cumsum_all["Cases"].cumsum()
        return px.bar(cumsum_all, x="DateRep", y="cumsum", title="世界の感染者数（累計）")

@app.callback(Output("show_world_data", "children"), [Input("world_covid_data", "value")])
def update_world_data(selected_type):

    if selected_type == "累計":
        return dcc.Graph(id="world_cumsum_graph",
        figure=px.bar(covid_world_cumsum, x="Countries and territories", y="Cases",log_y=True, title="各国の累積感染者数（y軸：ログスケール）", labels={"Countries and territories": "Country"})
        )
    elif selected_type == "ヒストリカル":
        return html.Div([
            dcc.Dropdown(id="world_data_dropdown",
            options=[{"value": i, "label": i} for i in covid_world_data["Countries and territories"].unique()],
            multi=True,
            value=["Japan", "China", "US"]
            ),
            dcc.Graph(id="world_data_multiple_Output")
        ])
    else:
        last_update1 = pd.Timestamp(last_update)
        new_world_data = covid_world_data[covid_world_data["DateRep"] == last_update1]
        return dcc.Graph(figure=px.bar(new_world_data, x="GeoId", y="Cases", hover_data=["Countries and territories"], title=f"各国の新規感染者数（{last_update}）"))

@app.callback(Output("world_data_multiple_Output", "figure"), [Input("world_data_dropdown", "value")])
def update_countries_graph(selected_countries):
    covid_world_data_selected = covid_world_data[covid_world_data["Countries and territories"].isin(selected_countries)]
    return px.line(covid_world_data_selected, x="DateRep", y="Cases", color="Countries and territories", title="各国の新規感染者数（ヒストリカル）")

network = html.Div(
    [
        html.Div(
            [
                html.H4("周囲の患者発生のネットワーク図"),
                cyto.Cytoscape(
                    id="covid_cyto",
                    layout={"name": "cose"},
                    elements=covid_el,
                    style={
                        "width": "100%",
                        "height": "80vh",
                        "backgroundColor": "white",
                        "borderRadius": "10px",
                    },
                ),
            ],
            className="eight columns",
        ),
        html.Div(
            [
                html.H4("感染関係データテーブル"),
                dash_table.DataTable(
                    columns=[
                        {"name": i, "id": i, "deletable": True}
                        for i in df_cyto_table.columns
                    ],
                    data=df_cyto_table.to_dict("records"),
                    fixed_rows={"headers": True},
                    fixed_columns={"headers": True, "data": 1},
                    style_cell={"minWidth": "30px", "textAlign": "left"},
                    page_size=1000,
                ),
            ],
            className="four columns",
            style={"height": "100vh"},
        ),
    ],
    style={"margin": "2%"},
)

graphs = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        daq.ToggleSwitch(
                            id="total_graph_toggle",
                            label=["新規", "累計"],
                            value=False,
                            style={
                                "width": "250px",
                                "backgroundColor": "lime",
                                "margin": "auto",
                                "color": "white",
                            },
                            color="red",
                        ),
                        dcc.Graph(id="total_covid_graph"),
                    ],
                    className="six columns",
                    style={"height": "55vh"},
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="todofuken",
                            figure=px.bar(
                                covid_jp_area,
                                x="累計感染者数",
                                y="都道府県",
                                orientation="h",
                                title="都道府県別感染者数",
                            ),
                        )
                    ],
                    className="six columns",
                    style={"height": "55vh", "marginTop": "2%"},
                ),
            ],
            style={"marginBottom": "2%"},
        )
    ]
)


table = html.Div(
    [
        dash_table.DataTable(
            id="covid_table",
            columns=[{"name": i, "id": i, "deletable": True} for i in covid_world_data.columns],
            data=covid_world_data.to_dict("records"),
            fixed_rows={"headers": True, "data": 0},
            editable=True,
            style_cell={"maxWidth": 150, "minWidth": 150,"textAlign": "left"},
            style_header={"fontWeight":"bold"},
            filter_action="native",
            row_deletable=True,
            sort_action="native",
            export_format="csv",
            fill_width=False,
            virtualization=True,
            page_size=5000,
        ),
        html.Img(src="assets/cc.png"),
    ]
)


layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H4("新型コロナウィルス 感染状況"),
                        html.H6(f"最終更新日 {last_update}"),
                        html.H6("日本の都道府県別データは一日遅れ"),
                        
                    ],
                    style={
                        "width": "80%",
                        "margin": "auto",
                        "backgroundColor": "#FFFFFA",
                        "padding": "2%",
                        "borderRadius": "10px",
                        "marginBottom": "30px",
                    },
                )
            ]
        ),

        dcc.Tabs(
            value="world",
            children=[
                
                dcc.Tab(
                    label="感染者数グラフ（世界）",
                    value="world",
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=world,
                ),

                dcc.Tab(
                    label="感染者数グラフ（日本）",
                    value="graph",
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=graphs,
                ),
                dcc.Tab(
                    label="ネットワーク図",
                    value="network",
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=network,
                ),
                # dcc.Tab(
                #     label="世界の状況",
                #     value="world",
                #     style=tab_style,
                #     selected_style=tab_selected_style,
                #     children=world,
                # ),
                dcc.Tab(
                    label="データ",
                    value="table",
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=table,
                ),
            ],
            style=tabs_styles,
        ),
        dcc.Markdown(
            """
            データ元 :      
            [厚生労働省](https://www.mhlw.go.jp/stf/houdou/index.html)      
                       [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/geographical-distribution-2019-ncov-cases)

            [データ源メモ](https://chomoku.herokuapp.com/covid-memo)
            """
        ),
    ],
    style={"backgroundColor": "#E0E3DA", "padding": "5%"},
)


@app.callback(
    Output("total_covid_graph", "figure"), [Input("total_graph_toggle", "value")]
)
def update_total(selected_value_total):
    if selected_value_total:
        return px.bar(
            covid_jp,
            x="DateRep",
            y="cumsum",
            title=f"日本の感染者数推移（累計）",
        )
    return px.bar(
        covid_jp,
        x="DateRep",
        y="Cases",
        title=f"日本の感染者数推移（新規）",
        labels={"DateRep": "日付", "Cases": "新規感染者数"},
    )
