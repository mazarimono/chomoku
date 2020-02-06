import json
import os
from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html

# import dash_alternative_viz as dav
import dash_daq as daq
import numpy as np
import pandas as pd

import plotly.express as px

import plotly.graph_objs as go

from dash.dependencies import Input, Output

# APP
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Chomoku</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div></div>
    </body>
</html>
"""


server = app.server

app.config.suppress_callback_exceptions = True

# # layout
# app.layout = html.Div(
#     [
#         dcc.Location(id="url", refresh=False),
#         html.H1(
#             "CHOMOKU DASHBOARD",
#             style={
#                 "textAlign": "center",
#                 "color": "#5A9367",
#                 "fontSize": "2vw",
#                 "padding": "2%",
#                 "backgroundColor": "#D7FFF1",
#             },
#         ),
#         html.Div(id="page-content"),
#     ]
# )

# kyoto-bus


fundata_df = pd.read_csv("src/fundata.csv", index_col=0)
index_df = pd.read_csv("src/kyoto-bus-index-long.csv", index_col=0)
keito_df = pd.read_csv("src/kyoto-bus-keito.csv", index_col=0)
bus_detail_df = pd.read_csv("src/bus_detail.csv", index_col=0)
kyoto_spot_df = pd.read_csv("src/kyoto_spot_central.csv", index_col=0)
bottom10_bus = index_df[index_df["variable"] == 2017].sort_values("value")[:10]
bus_index_b10 = index_df[index_df["bus_line"].isin(bottom10_bus["bus_line"])]
bus10_df = keito_df[keito_df["name"].isin(bottom10_bus["bus_line"])]


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


app.layout = html.Div([dcc.Location(id="url"), html.Div(id="page-content")])


kyoto_bus = html.Div(
    [
        html.Div(
            [
                html.Div([html.H1("すごい！京都の市バス経営")], style={"color": "#232323"}),
                html.Div(
                    [
                        dcc.Markdown(
                            """
        京都の市バスは、2002年に累積欠損金が-162億円でした。しかしそこから業績が急回復し、2017年の発表数値では累積欠損金は一掃され、+85.12億円となりました。

        本アプリケーションではオープンデータを用い、業績の回復具合を観察した後、営業係数を用いて各路線の営業状況を観察できます。

        """,
                            style={"fontSize": "2.5rem", "color": "#ff8e3c"},
                        )
                    ]
                ),
                html.Div(
                    [
                        dcc.Tabs(
                            [
                                dcc.Tab(
                                    label="業績情報",
                                    style=tab_style,
                                    selected_style=tab_selected_style,
                                    children=[
                                        html.H2("京都市バスの累積欠損金の推移（1998年～2017年）"),
                                        dcc.Graph(
                                            figure=px.bar(
                                                fundata_df,
                                                x="年度",
                                                y="累積欠損金",
                                                color="累積欠損金",
                                            )
                                        ),
                                        html.P(
                                            "京都市　交通局　交通白書（https://www.city.kyoto.lg.jp/kotsu/page/0000073257.html）"
                                        ),
                                    ],
                                ),
                                dcc.Tab(
                                    label="基礎情報",
                                    style=tab_style,
                                    selected_style=tab_selected_style,
                                    children=[
                                        html.H2("市バス基礎情報（1998年～2017年）"),
                                        html.Table(
                                            [
                                                html.Tr(
                                                    [
                                                        html.Td(
                                                            [
                                                                dcc.Graph(
                                                                    figure=go.Figure(
                                                                        data=[
                                                                            go.Bar(
                                                                                x=fundata_df[
                                                                                    "年度"
                                                                                ],
                                                                                y=fundata_df[
                                                                                    "経常収益"
                                                                                ],
                                                                            )
                                                                        ],
                                                                        layout=go.Layout(
                                                                            title="経常収益"
                                                                        ),
                                                                    )
                                                                )
                                                            ],
                                                            style=td_style,
                                                        ),
                                                        html.Td(
                                                            [
                                                                dcc.Graph(
                                                                    figure=go.Figure(
                                                                        data=[
                                                                            go.Bar(
                                                                                x=fundata_df[
                                                                                    "年度"
                                                                                ],
                                                                                y=fundata_df[
                                                                                    "経常支出"
                                                                                ],
                                                                            )
                                                                        ],
                                                                        layout=go.Layout(
                                                                            title="経常支出"
                                                                        ),
                                                                    )
                                                                )
                                                            ],
                                                            style=td_style,
                                                        ),
                                                        html.Td(
                                                            [
                                                                dcc.Graph(
                                                                    figure=go.Figure(
                                                                        data=[
                                                                            go.Bar(
                                                                                x=fundata_df[
                                                                                    "年度"
                                                                                ],
                                                                                y=fundata_df[
                                                                                    "経常損益"
                                                                                ],
                                                                            )
                                                                        ],
                                                                        layout=go.Layout(
                                                                            title="経常損益"
                                                                        ),
                                                                    )
                                                                )
                                                            ],
                                                            style=td_style,
                                                        ),
                                                    ]
                                                ),
                                                html.Tr(
                                                    [
                                                        html.Td(
                                                            [
                                                                dcc.Graph(
                                                                    figure=go.Figure(
                                                                        data=[
                                                                            go.Bar(
                                                                                x=fundata_df[
                                                                                    "年度"
                                                                                ],
                                                                                y=fundata_df[
                                                                                    "累積欠損金"
                                                                                ],
                                                                            )
                                                                        ],
                                                                        layout=go.Layout(
                                                                            title="累計欠損金"
                                                                        ),
                                                                    )
                                                                )
                                                            ],
                                                            style=td_style,
                                                        ),
                                                        html.Td(
                                                            [
                                                                dcc.Graph(
                                                                    figure=go.Figure(
                                                                        data=[
                                                                            go.Bar(
                                                                                x=fundata_df[
                                                                                    "年度"
                                                                                ],
                                                                                y=fundata_df[
                                                                                    "旅客数"
                                                                                ],
                                                                            )
                                                                        ],
                                                                        layout=go.Layout(
                                                                            title="旅客数（1日当たり）"
                                                                        ),
                                                                    )
                                                                )
                                                            ],
                                                            style=td_style,
                                                        ),
                                                        html.Td(
                                                            [
                                                                dcc.Graph(
                                                                    figure=go.Figure(
                                                                        data=[
                                                                            go.Bar(
                                                                                x=fundata_df[
                                                                                    "年度"
                                                                                ],
                                                                                y=fundata_df[
                                                                                    "職員数"
                                                                                ],
                                                                            )
                                                                        ],
                                                                        layout=go.Layout(
                                                                            title="職員数"
                                                                        ),
                                                                    )
                                                                )
                                                            ],
                                                            style=td_style,
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            style={"width": "100%"},
                                        ),
                                        html.P(
                                            "京都市　交通局　交通白書（https://www.city.kyoto.lg.jp/kotsu/page/0000073257.html）"
                                        ),
                                    ],
                                ),
                                dcc.Tab(
                                    label="詳細情報",
                                    style=tab_style,
                                    selected_style=tab_selected_style,
                                    children=[
                                        html.H2("市バス詳細情報（2010年～2017年）"),
                                        html.Div(
                                            [
                                                dcc.RadioItems(
                                                    id="passenger_select",
                                                    options=[
                                                        {
                                                            "label": "旅客数",
                                                            "value": "旅客数",
                                                        },
                                                        {
                                                            "label": "旅客収入",
                                                            "value": "旅客収入",
                                                        },
                                                    ],
                                                    value="旅客数",
                                                ),
                                                dcc.RadioItems(
                                                    id="busdata_select",
                                                    options=[
                                                        {
                                                            "label": "１車平均旅客収入（1日）",
                                                            "value": "１車平均旅客収入（1日）",
                                                        },
                                                        {
                                                            "label": "走行1キロ当たり旅客収入",
                                                            "value": "走行1キロ当たり旅客収入",
                                                        },
                                                    ],
                                                    value="１車平均旅客収入（1日）",
                                                ),
                                                html.Div(
                                                    [
                                                        dcc.Graph(
                                                            id="pass_graph",
                                                            style=two_style,
                                                        ),
                                                        dcc.Graph(
                                                            id="bus_graph",
                                                            style=two_style,
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        html.P(
                                            "京都市オープンデータポータルサイト　「市バスの運輸成績について」　（https://data.city.kyoto.lg.jp/）"
                                        ),
                                    ],
                                ),
                            ],
                            style=tabs_styles,
                        )
                    ],
                    style={
                        "padding": "3%",
                        "backgroundColor": "white",
                        "borderRadis": 20,
                    },
                ),
                html.Div(
                    [
                        html.H2("路線ごとの現状"),
                        dcc.Markdown(
                            """
            ここでは営業係数を用いて各路線の収益状況を確認できます。営業係数は100を超えるとその路線が赤字であることを示します。

            散布図には、各路線の2017年時点の乗客数と営業係数を示しました。散布図のポイントをシフトを押しながら選択すると（複数選択可）、右の営業係数の線グラフおよび、下の地図にその路線の状態が示されます。

            初期の設定は、収益率が高い路線のトップ10を表示しています。

            注意 / 説明文では、散布図がアニメーションで動いていましたが、アプリケーションが落ちるため、現在はアニメーションをオフにしています。
            """,
                            style={"fontSize": "2.5rem", "color": "#ff8e3c"},
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="bus_index_scatter",
                                    className="shikaku-css",
                                    figure=px.scatter(
                                        index_df,
                                        x="2017_passenger",
                                        y="value",
                                        log_x=True,
                                        log_y=True,
                                        range_y=[30, 330],
                                        hover_data=["bus_line"],
                                        color="bus_line",
                                        height=500,
                                        template={
                                            "layout": {"clickmode": "event+select"}
                                        },
                                        title="各路線の1日乗車数（x軸）と営業係数（y軸）",
                                    ),
                                )
                            ],
                            style={"width": "70%", "display": "inline-block"},
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="bus_single_data",
                                    figure=go.Figure(
                                        data=[
                                            go.Scatter(
                                                x=bus_index_b10[
                                                    bus_index_b10["bus_line"] == i
                                                ]["variable"],
                                                y=bus_index_b10[
                                                    bus_index_b10["bus_line"] == i
                                                ]["value"],
                                                name=i,
                                            )
                                            for i in bus_index_b10["bus_line"].unique()
                                        ],
                                        layout=go.Layout(height=450, title="各路線の営業係数"),
                                    ),
                                )
                            ],
                            style={
                                "width": "30%",
                                "display": "inline-block",
                                "height": 500,
                            },
                        ),
                        daq.ToggleSwitch(
                            id="spot_change",
                            label="観光地の表示",
                            color="#9B51E0",
                            style={"height": 100},
                        ),
                        html.Div([html.Div([dcc.Graph(id="bus_line_map",
                        figure=go.Figure(
        data=[
            go.Scattermapbox(
                mode="lines",
                lon=bus10_df[bus10_df["name"] == i]["lon"],
                lat=bus10_df[bus10_df["name"] == i]["lat"],
                name=i,
                line_width=10,
            )
            for i in bus10_df["name"].unique()
        ],
        layout=go.Layout(mapbox={
            "center": {"lon": keito_df["lon"].mean(), "lat": keito_df["lat"].mean()},
            "style": "carto-positron",
            "pitch": 90,
            "zoom": 12,
        },
        height=800,
        title="選択された路線の経路と京都市近郊の観光地",)
    )
                        )])]),
                        html.P(
                            "京都市オープンデータポータルサイト　「市バスの運輸成績について」　（https://data.city.kyoto.lg.jp/）"
                        ),
                        html.P(
                            "GISホームページ　国土数値情報　バスルート　（http://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N07.html）"
                        ),
                        html.P(
                            "GISホームページ　国土数値情報　観光資源データ　（http://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P12-v2_2.html）"
                        ),
                    ]
                ),
            ],
            style={"padding": "5% 10%"},
        )
    ],
    className="shikaku-css",
)


@app.callback(Output("pass_graph", "figure"), [Input("passenger_select", "value")])
def update_passanger_data_graph(pass_value):
    if pass_value == "旅客数":
        fig = go.Figure(
            data=[
                go.Bar(x=bus_detail_df["年度"], y=bus_detail_df["定期外旅客数"], name="定期外旅客数"),
                go.Bar(x=bus_detail_df["年度"], y=bus_detail_df["定期旅客数"], name="定期旅客数"),
                go.Bar(x=bus_detail_df["年度"], y=bus_detail_df["敬老旅客数"], name="敬老旅客数"),
            ],
            layout=go.Layout(barmode="stack", title="各種旅客数（年間　単位：人）"),
        )
        return fig
    fig = go.Figure(
        data=[
            go.Bar(x=bus_detail_df["年度"], y=bus_detail_df["定期外旅客収入"], name="定期外旅客収入"),
            go.Bar(x=bus_detail_df["年度"], y=bus_detail_df["定期旅客収入"], name="定期旅客収入"),
            go.Bar(x=bus_detail_df["年度"], y=bus_detail_df["敬老など旅客収入"], name="敬老など旅客収入"),
        ],
        layout=go.Layout(barmode="stack", title="各種旅客収入（年間　単位：円）"),
    )
    return fig


@app.callback(Output("bus_graph", "figure"), [Input("busdata_select", "value")])
def update_bus_data_graph(bus_value):
    fig = go.Figure(
        data=[go.Bar(x=bus_detail_df["年度"], y=bus_detail_df[bus_value])],
        layout=go.Layout(title=f"バス{bus_value}（単位：円）"),
    )

    return fig


@app.callback(
    [
        Output("bus_single_data", "figure"),
        Output("bus_line_map", "figure"),
        Output("spot_change", "label"),
    ],
    [Input("bus_index_scatter", "selectedData"), Input("spot_change", "value")],
)
def update_map(selectedData, spot_switch):

    bus_index_b10 = index_df[index_df["bus_line"].isin(bottom10_bus["bus_line"])]
    bus10_df = keito_df[keito_df["name"].isin(bottom10_bus["bus_line"])]

    # 営業係数の線グラフ
    kyoto_bus_line_g = go.Figure(
        data=[
            go.Scatter(
                x=bus_index_b10[bus_index_b10["bus_line"] == i]["variable"],
                y=bus_index_b10[bus_index_b10["bus_line"] == i]["value"],
                name=i,
            )
            for i in bus_index_b10["bus_line"].unique()
        ]
    )

    kyoto_bus_line_g.update_layout(height=450, title="各路線の営業係数")

    # 地図グラフ
    kyoto_spot_map = go.Figure(
        data=[
            go.Scattermapbox(
                mode="lines",
                lon=bus10_df[bus10_df["name"] == i]["lon"],
                lat=bus10_df[bus10_df["name"] == i]["lat"],
                name=i,
                line_width=10,
            )
            for i in bus10_df["name"].unique()
        ]
    )

    kyoto_spot_map.update_layout(
        mapbox={
            "center": {"lon": keito_df["lon"].mean(), "lat": keito_df["lat"].mean()},
            "style": "carto-positron",
            "pitch": 90,
            "zoom": 12,
        },
        height=800,
        title="選択された路線の経路と京都市近郊の観光地",
    )

    # スィッチのタイトル
    switch_title = "観光地の表示（オフ）"

    if selectedData:
        selected_line = []
        for i in range(len(selectedData["points"])):
            selected_line.append(selectedData["points"][i]["customdata"][0])
        selected_bus_index = index_df[index_df["bus_line"].isin(selected_line)]
        selected_line_df = keito_df[keito_df["name"].isin(selected_line)]

        for i in selected_line_df["name"].unique():
            kyoto_spot_map.add_trace(
                go.Scattermapbox(
                    mode="lines",
                    lon=selected_line_df[selected_line_df["name"] == i]["lon"],
                    lat=selected_line_df[selected_line_df["name"] == i]["lat"],
                    name=i,
                    line_width=10,
                )
            )

        for i in selected_line:
            kyoto_bus_line_g.add_trace(
                go.Scatter(
                    x=selected_bus_index[selected_bus_index["bus_line"] == i][
                        "variable"
                    ],
                    y=selected_bus_index[selected_bus_index["bus_line"] == i]["value"],
                    name=i,
                )
            )

    if spot_switch:
        for i in kyoto_spot_df["name"].unique():
            kyoto_spot_map.add_trace(
                go.Scattermapbox(
                    mode="markers",
                    lon=kyoto_spot_df[kyoto_spot_df["name"] == i]["lon"],
                    lat=kyoto_spot_df[kyoto_spot_df["name"] == i]["lat"],
                    name=i,
                    marker={"size": 14},
                )
            )
        switch_title = "観光地の表示（オン）"

    return (kyoto_bus_line_g, kyoto_spot_map, switch_title)


# TOURIST

total_list = ["総数"]
conti_list = ["アフリカ計", "北アメリカ計", "南アメリカ計", "アジア計", "オセアニア計", "ヨーロッパ計"]

tourist_df = pd.read_csv(
    "src/tourist_without_cumsum.csv", index_col=0, parse_dates=["date"]
)
conti_df = tourist_df[tourist_df["国名"].isin(conti_list)]
country_df = tourist_df[~tourist_df["国名"].isin(total_list + conti_list)]

tourist = html.Div(
    [
        html.H1("訪日外国人数"),
        html.Div(
            [
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="訪日外国人数総数",
                            style=tab_style,
                            selected_style=tab_selected_style,
                            children=[
                                dcc.RadioItems(
                                    id="total_checkitem",
                                    options=[
                                        {"value": "月間", "label": "月間"},
                                        {"value": "年間", "label": "年間"},
                                    ],
                                    value="月間",
                                ),
                                html.Div(id="total_number"),
                            ],
                        ),
                        dcc.Tab(
                            label="大陸別訪日外国人数",
                            style=tab_style,
                            selected_style=tab_selected_style,
                            children=[
                                dcc.Dropdown(
                                    id="continent-drop",
                                    options=[
                                        {"value": i, "label": i} for i in conti_list
                                    ],
                                    multi=True,
                                    value=conti_list,
                                ),
                                html.Div(id="continent-number"),
                            ],
                        ),
                        dcc.Tab(
                            label="国別訪日外国人数",
                            style=tab_style,
                            selected_style=tab_selected_style,
                            children=[
                                dcc.Dropdown(
                                    id="country-drop",
                                    options=[
                                        {"value": i, "label": i}
                                        for i in country_df["国名"].unique()
                                    ],
                                    multi=True,
                                    value=["中国", "韓国", "米国", "台湾", "香港"],
                                ),
                                html.Div(id="country-number"),
                            ],
                        ),
                    ]
                ),
                html.P("日本政府観光局: 月別年別統計データ（訪日外国人）: https://www.jnto.go.jp/jpn/statistics/visitor_trends/")
            ],
            style={"width": "90%", "margin": "auto", "padding": "5% 0"},
        ),
    ],
    style={"backgroundColor": "#FBE251", "padding": "5%", "borderRadius": "5%"},
)


@app.callback(Output("total_number", "children"), [Input("total_checkitem", "value")])
def update_total_graph(selected_value):
    total = tourist_df[tourist_df["data_name"] == "tourist_num"]
    total = total[total["国名"].isin(total_list)]
    if selected_value == "年間":
        total_year = total.groupby(pd.Grouper(key="date", freq="Y")).sum().reset_index()
        return dcc.Graph(
            figure=px.bar(
                total_year,
                x="date",
                y="value",
                color="value",
                title="訪日外国人数（総数: 年間）",
                log_y=True,
            )
        )

    return dcc.Graph(
        figure=px.bar(
            total,
            x="date",
            y="value",
            color="value",
            title="訪日外国人数（総数: 月間）",
            log_y=True,
        )
    )


@app.callback(
    Output("continent-number", "children"), [Input("continent-drop", "value")]
)
def update_conti_graph(selected_conti):
    conti_dff = conti_df[conti_df["data_name"] == "tourist_num"]
    conti_dff = conti_dff[conti_dff["国名"].isin(selected_conti)]
    return dcc.Graph(figure=px.line(conti_dff, x="date", y="value", color="国名"))


@app.callback(Output("country-number", "children"), [Input("country-drop", "value")])
def update_country_graph(selected_country):
    country_dff = country_df[country_df["data_name"] == "tourist_num"]
    country_dff = country_dff[country_dff["国名"].isin(selected_country)]
    return dcc.Graph(figure=px.line(country_dff, x="date", y="value", color="国名"))


# Page-Router
@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/foreign-tourist":
        return tourist
    else:
        return kyoto_bus


if __name__ == "__main__":
    app.run_server(debug=True)
