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
covid_jp = covid_world_data[covid_world_data["CountryExp"] == "Japan"]
covid_jp = covid_jp.sort_values("DateRep")
covid_jp["cumsum"] = covid_jp["NewConfCases"].cumsum()
covid_jp = covid_jp[15:]
last_update = covid_jp.iloc[-1, 0].date()

covid_world_cumsum = covid_world_data.groupby("CountryExp", as_index=False).sum()
covid_world_cumsum = covid_world_cumsum.sort_values("NewConfCases")
covid_world_cumsum = covid_world_cumsum[-30:]


# 日本地域データ

covid_jp_area = pd.read_csv("./src/area_jp.csv")
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
        # dcc.RadioItems(id="world_covid_data", 
        # options=[{"label": i, "value": i} for i in ["棒グラフ", "線グラフ"]],
        # value="棒グラフ"
        # ),
        dcc.Graph(id="world_graph",
        figure=px.bar(covid_world_data, x="DateRep", y="NewConfCases", color="CountryExp", title="世界の新規感染者数", template={"layout":{"showlegend": False, "hovermode": "closest"}})
        ),

        # legendをオフにする方法
        # 各国の日々のデータの推移が見たい。
        # 各国の累計の日々の推移（動かす？）

        dcc.Graph(id="world_cumsum_graph",
        figure=px.bar(covid_world_cumsum, x="CountryExp", y="NewConfCases",log_y=True, title="各国の累積感染者数（y軸：ログスケール）", labels={"CountryExp": "Country"})
        ),

        # html.H1(id="selected_country_graph")

    ])
])


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
                                x="人数（名）",
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
                        html.H6(f"最終更新日 {last_update}")
                        
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
        y="NewConfCases",
        title=f"日本の感染者数推移（新規）",
        labels={"DateRep": "日付", "NewConfCases": "新規感染者数"},
    )
