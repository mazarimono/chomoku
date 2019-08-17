import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
import plotly_express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime
from datetime import timedelta
import os

# style

external_stylesheets = [
    'https://fonts.googleapis.com/css?family=Source+Sans+Pro&display=swap',
    'https://fonts.googleapis.com/css?family=Noto+Sans+JP&display=swap',
]


# Tsuyu Data Read
dftsuyu = pd.read_csv(
    "./assets/all.csv", index_col=0, parse_dates=["enter", "exit", "g-enter", "g-exit"]
)
df2tsuyu = pd.read_csv(
    "./assets/all2.csv", index_col=0, parse_dates=["enter", "exit", "date"]
)

# US YIELD DATA
# Data
start = datetime(2000, 1, 1)
today = datetime.today()

dfyield = web.DataReader(
    [
        "DFF",
        "DGS3MO",
        "DGS2",
        "DGS5",
        "DGS10",
        "DGS30",
        "TEDRATE",
        "T10YIE",
        "T10Y3M",
        "T10Y2Y",
        "BAA10Y",
    ],
    "fred",
    start,
    today,
)
dfyield["date"] = dfyield.index
dfyield.columns = [
    "ffrate",
    "3mT",
    "2yT",
    "5yT",
    "10yT",
    "30yT",
    "tedspread",
    "breakeven10Y",
    "3m10ySpread",
    "2y10ySpread",
    "baa10ySpread",
    "date",
]
dfyield["30yT"] = dfyield["30yT"].fillna(0)

yieldOnly = dfyield[["date", "ffrate", "3mT",
                     "2yT", "5yT", "10yT", "30yT"]].dropna()
spreads = dfyield[
    ["date", "tedspread", "3m10ySpread", "2y10ySpread", "baa10ySpread"]
].dropna()

# JP GDP DATA
dfgdp = pd.read_csv("./src/japanese-gdp-19552007.csv")

# RUSMUSSEN TRUMP INDEX
trump_data = pd.read_html(
    "http://www.rasmussenreports.com/public_content/politics/trump_administration/trump_approval_index_history",
    parse_dates=["Date"],
)[0]

# JP_STATS_Table
# jp_stats_csv = pd.read_csv(
#     "./src/jp_stat_data.csv", index_col=0, low_memory=False
# ).sort_values("UPDATED_DATE", ascending=False)
#

# KYOTO HOTEL DATA
df_kyoto_hotels = pd.read_csv("assets/kyoto_hotel_comp.csv", index_col=0)

# Kitakyushu
kitakyushu_shelter = pd.read_csv(
    "assets/fukuoka_hinanjo.csv", encoding="shift-jis")

# MAP
mapbox_accesstoken = "pk.eyJ1IjoibWF6YXJpbW9ubyIsImEiOiJjanA5Y3IxaWsxeGtmM3dweDh5bjgydGFxIn0.3vrfsqZ_kGPGhi4_npruGg"

# Back to menu component

bto_menu = html.Div(
    [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
    style={"textAlign": "center", "marginTop": "5%"},
)

# APP
app = dash.Dash(__name__)

server = app.server

app.config.suppress_callback_exceptions = True

# layout
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.H1(
            "CHOMOKU DASHBOARD",
            style={
                "textAlign": "center",
                "color": "#5A9367",
                "fontSize": "2vw",
                "padding": "2%",
                "backgroundColor": "#D7FFF1",
            },
        ),
        html.Div(id="page-content"),
    ]
)

# index_page
index_page = html.Div(
    [
        html.Title("CHOMOKU DASHBOARD"),
        html.Div(
            [
                html.P(
                    "20190607:  ",
                    style={"display": "inline-block",
                           "marginRight": "1%", "fontSize": 40},
                ),
                dcc.Link(
                    "Japanese rainy season dashboard",
                    href="/tsuyu-dash",
                    style={"fontSize": 40, "textDecoration": "none"},
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.P(
                    "20190614:  ",
                    style={"display": "inline-block",
                           "marginRight": "1%", "fontSize": 40},
                ),
                dcc.Link("US Yield Watch", href="/us-yield",
                         style={"fontSize": 40, "textDecoration": "none"}),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.P(
                    "20190625:  ",
                    style={"display": "inline-block",
                           "marginRight": "1%", "fontSize": 40},
                ),
                dcc.Link(
                    "Japanese GDP(YoY %)", href="/japanese-gdp", style={"fontSize": 40, "textDecoration": "none"}
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.P(
                    "20190701:  ",
                    style={"display": "inline-block",
                           "marginRight": "1%", "fontSize": 40},
                ),
                dcc.Link(
                    "Trump Administration Approval Index Data from Rasmussen Report",
                    href="/trump-index",
                    style={"fontSize": 40, "textDecoration": "none"},
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.P(
                    "20190816:  ",
                    style={"display": "inline-block",
                           "marginRight": "1%", "fontSize": 40},
                ),
                dcc.Link(
                    "Kyoto HOTEL Data",
                    href="/kyoto-hotels",
                    style={"fontSize": 40, "textDecoration": "none"},
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.P(
                    "20190816:  ",
                    style={"display": "inline-block",
                           "marginRight": "1%", "fontSize": 40},
                ),
                dcc.Link(
                    "Kitakyushu-Shelter-Map",
                    href="/kitakyushu-shelter",
                    style={"fontSize": 40, "textDecoration": "none"},
                ),
            ],
            style={"textAlign": "center"},
        ),
    ]
)

# Contents Tsuyu_page
tsuyu_page = html.Div(
    [
        html.H1(
            "HOW ABOUT JAPANESE RAINY SEASON？",
            style={"textAlign": "center", "fontSize": "1.5vw"},
        ),
        html.Div(
            [
                html.H2(id="sub-title", style={"textAlign": "center"}),
                html.H2(
                    "x-axis: begine date ; y-axis: end date, bubble-size: precipitation",
                    style={"textAlign": "center"},
                ),
                dcc.RadioItems(
                    id="area-select-dropdown",
                    options=[
                        {"label": i, "value": i} for i in dftsuyu["area"].unique()
                    ],
                    value="okinawa",
                    style={"width": "50%", "margin": "1% auto 1%",
                           "fontSize": "1.2vw"},
                ),
                html.Div(
                    [
                        dcc.RangeSlider(
                            id="area-range-slider",
                            min=dftsuyu["year"].min(),
                            max=dftsuyu["year"].max(),
                            value=[dftsuyu["year"].min(), dftsuyu["year"].max()],
                            marks={
                                i: "{}".format(i)
                                for i in range(
                                    dftsuyu["year"].min(
                                    ), dftsuyu["year"].max()
                                )
                                if i % 10 == 0
                            },
                        )
                    ],
                    style={
                        "textAlign": "center",
                        "width": "60%",
                        "margin": "1% auto 3%",
                    },
                ),
                dcc.Graph(
                    id="area-chart", style={"width": "75%", "margin": "0 auto 0"}
                ),
                html.P(
                    "selection-area ; kyusyu-s: Kyusyu-South, kyusyu-n: Kyusyu-North, tohoku-n: Tohoku-North,tohoku-s: Tohoku-South",
                    style={"width": "60%", "margin": "1% auto",
                           "fontSize": "1vw"},
                ),
            ]
        ),
        html.Div(
            [
                html.H2(
                    id="gantt-title",
                    style={
                        "width": "70%",
                        "textAlign": "center",
                        "fontSize": "1.5vw",
                        "margin": "0 auto",
                    },
                ),
                dcc.Graph(
                    id="area-gantt", style={"width": "75%", "margin": "0 auto 0"}
                ),
                html.H2(
                    id="scatter-title",
                    style={
                        "width": "70%",
                        "textAlign": "center",
                        "fontSize": "1.5vw",
                        "margin": "0 auto",
                    },
                ),
                dcc.Graph(
                    id="scatter-rain", style={"width": "75%", "margin": "0 auto 0"}
                ),
                html.Div(
                    [
                        html.P("Please choose the year!"),
                        dcc.Dropdown(
                            id="polar-dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in dftsuyu["year"].unique()
                            ],
                            value=1951,
                            style={
                                "width": "50%",
                                "float": "left",
                                "display": "inline-block",
                            },
                        ),
                        dcc.Graph(
                            id="bar-polar",
                            style={
                                "width": "75%",
                                "margin": "0 auto 0",
                                "display": "inline-block",
                            },
                        ),
                    ],
                    style={"width": "75%", "margin": "0 auto 0"},
                ),
            ]
        ), bto_menu
    ])


@app.callback(
    [Output("area-chart", "figure"), Output("sub-title", "children")],
    [Input("area-select-dropdown", "value"),
     Input("area-range-slider", "value")],
)
def area_chart_figure(areaName, slider_val):
    slider_num_small = slider_val[0]
    slider_num_big = slider_val[1]
    dfftsuyu = dftsuyu[dftsuyu["area"] == areaName]
    dfftsuyu = dfftsuyu[dfftsuyu["year"] >= slider_num_small]
    dfftsuyu = dfftsuyu[dfftsuyu["year"] <= slider_num_big]

    d = timedelta(10)

    return (
        px.scatter(
            dfftsuyu,
            x="g-enter",
            y="g-exit",
            size="p-amount",
            color="year",
            marginal_x="violin",
            marginal_y="violin",
            range_x=[dftsuyu["g-enter"].min() - d,
                     dftsuyu["g-enter"].max() + d],
            range_y=[dftsuyu["g-exit"].min() - d,
                     dftsuyu["g-exit"].max() + d],
            height=600,
        ),
        "Rainy season in {} from {} to {}".format(
            areaName, slider_num_small, slider_num_big
        ),
    )


@app.callback(
    [
        Output("area-gantt", "figure"),
        Output("gantt-title", "children"),
        Output("scatter-rain", "figure"),
        Output("bar-polar", "figure"),
        Output("scatter-title", "children"),
    ],
    [
        Input("area-select-dropdown", "value"),
        Input("area-range-slider", "value"),
        Input("polar-dropdown", "value"),
    ],
)
def gantt(areaName, slider_val, selected_year):
    slider_num_small = slider_val[0]
    slider_num_big = slider_val[1]
    df1tsuyu = dftsuyu[dftsuyu["area"] == areaName]
    df1tsuyu = df1tsuyu[df1tsuyu["year"] >= slider_num_small]
    df1tsuyu = df1tsuyu[df1tsuyu["year"] <= slider_num_big]
    dfftsuyu = df2tsuyu[df2tsuyu["area"] == areaName]
    dfftsuyu = dfftsuyu[dfftsuyu["year"] >= slider_num_small]
    dfftsuyu = dfftsuyu[dfftsuyu["year"] <= slider_num_big]
    dff2suyu = dfftsuyu[dfftsuyu["variable"] == "g-enter"]
    d = timedelta(10)
    df_gannt = dftsuyu[dftsuyu["year"] == selected_year]

    gannt_data = list()

    for i in range(len(df_gannt)):
        gannt_data.append(
            dict(
                Task=df_gannt.iloc[i, 2],
                Start=df_gannt.iloc[i, 3],
                Finish=df_gannt.iloc[i, 4],
            )
        )

    return (
        px.box(
            dfftsuyu,
            x="year",
            y="date",
            range_y=[dftsuyu["g-enter"].min() - d, dftsuyu["g-exit"].max() + d],
        ),
        "Historical tsuyu enter-data and exit-date Chart: {} ".format(
            areaName),
        {
            "data": [
                go.Scatter(
                    x=df1tsuyu[df1tsuyu["year"] == i]["days"],
                    y=dff2suyu[dff2suyu["year"] == i]["p-amount"],
                    mode="markers",
                    marker={"size": 15},
                    text=str(i),
                    name=str(i),
                )
                for i in df1tsuyu["year"].unique()
            ],
            "layout": go.Layout(
                xaxis={"title": "days"},
                yaxis={"title": "precipatation amount"},
                height=600,
                hovermode="closest",
            ),
        },
        ff.create_gantt(
            gannt_data, title="Difference of Area; Year {}".format(
                selected_year)
        ),
        "Scatter plot: {} xaxis: length of rainy season, yaxis: precipitational amount(average value: 100)".format(
            areaName
        ),
    )


# Contents US YIELD CURVE

us_yield = html.Div(
    [
        html.Div(
            [
                html.H1("US Yield Data", style={"textAlign": "center"}),
                dcc.DatePickerRange(
                    id="date-picker",
                    minimum_nights=5,
                    clearable=True,
                    start_date=datetime(2000, 1, 1),
                    style={"display": "block"},
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="historical-left",
                            hoverData={"points": [{"x": "2008-09-09"}]},
                        ),
                        # html.H3('見たい範囲を上の日付ピッカー、もしくはマウスのドラッグで選択できます', style={'textAlign': 'center'}),
                    ],
                    style={"width": "49%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        html.H1(id="test"),
                        dcc.Graph(id="yield-curve-right"),
                        # html.H3('左の米国の主要金利のグラフでマウスホバーした地点のイールドカーブが表示できます。', style={'textAlign': 'center'}),
                    ],
                    style={"width": "49%", "display": "inline-block"},
                ),
            ],
            style={"height": "1000", "margin": "2%"},
        ),
        html.Div(
            [
                html.Div(
                    [html.H1("Major Yeild Spreads")], style={"textAlign": "center"}
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="spread-dropdown",
                            options=[
                                {"label": i, "value": i} for i in spreads.columns[1:]
                            ],
                            value="tedspread",
                        )
                    ],
                    style={"width": "30%", "margin": "2% auto 2%"},
                ),
                html.Div(
                    [dcc.Graph(id="spreadGraph")],
                    style={"width": "60%", "margin": "0 auto 0"},
                ),
            ]
        ),
        bto_menu
    ])


@app.callback(
    dash.dependencies.Output("historical-left", "figure"),
    [
        dash.dependencies.Input("date-picker", "start_date"),
        dash.dependencies.Input("date-picker", "end_date"),
    ],
)
def makeYieldHist(start_date, end_date):
    histdf = yieldOnly[start_date:end_date]
    histdf = pd.melt(
        histdf,
        id_vars="date",
        value_vars=["ffrate", "3mT", "2yT", "5yT", "10yT", "30yT"],
    )
    return {
        "data": [
            go.Scatter(
                x=histdf[histdf["variable"] == i]["date"],
                y=histdf[histdf["variable"] == i]["value"],
                name=i,
            )
            for i in histdf["variable"].unique()
        ],
        "layout": {"title": "US Yeild"},
    }


@app.callback(
    dash.dependencies.Output("yield-curve-right", "figure"),
    [dash.dependencies.Input("historical-left", "hoverData")],
)
def makeYieldCurve(hoverData):

    try:
        selectedDate = hoverData["points"][0]["x"]
    except:
        selectedDate = datetime(2008, 9, 9)

    selecteddf = yieldOnly[yieldOnly["date"] == selectedDate]
    return {
        "data": [
            go.Parcoords(
                line=dict(color="blue"),
                dimensions=list(
                    [
                        dict(
                            range=[0, 7], label="FF Rate", values=selecteddf["ffrate"]
                        ),
                        dict(
                            range=[0, 7], label="3M Treasury", values=selecteddf["3mT"]
                        ),
                        dict(
                            range=[0, 7], label="2Y Treasury", values=selecteddf["2yT"]
                        ),
                        dict(
                            range=[0, 7], label="5Y Treasury", values=selecteddf["5yT"]
                        ),
                        dict(
                            range=[0, 7],
                            label="10Y Treasury",
                            values=selecteddf["10yT"],
                        ),
                        dict(
                            range=[0, 7],
                            label="30Y Treasury",
                            values=selecteddf["30yT"],
                        ),
                    ]
                ),
            )
        ],
        "layout": {"title": "Yield Curve Date: {}".format(selectedDate)},
    }


@app.callback(
    dash.dependencies.Output("spreadGraph", "figure"),
    [dash.dependencies.Input("spread-dropdown", "value")],
)
def spreadGraph(selectedvalue):
    dfspread = spreads[["date", selectedvalue]]
    return {
        "data": [
            go.Scatter(
                x=dfspread["date"], y=dfspread[selectedvalue], name=selectedvalue
            )
        ]
    }


japanese_gdp = html.Div(
    [
        html.H1("日本の実質GDP成長率（前年比%）", style={"textAlign": "center"}),
        html.Div(
            [
                dcc.Graph(
                    figure={
                        "data": [go.Bar(x=dfgdp["暦年"], y=dfgdp["GDP実質前年比（％）"])]}
                )
            ]
        ),
        html.Div(
            [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
            style={"textAlign": "center"},
        ),
    ]
)

# TRUMP INDEX
t_index = html.Div(
    [
        html.Div(
            [
                html.H1("Trump Administration Approval Index"),
                html.H1("Data from RASMUSSEN REPORTS"),
                html.Div(
                    [
                        "URL : ",
                        html.A(
                            "http://www.rasmussenreports.com/public_content/politics/trump_administration/trump_approval_index_history"
                        ),
                    ]
                ),
                html.H3(
                    children=["Update: {}".format(
                        str(trump_data["Date"].max())[:10])]
                ),
                html.H3("Latest Approval Index: {}".format(
                    trump_data.iloc[0, 1])),
            ],
            style={"textAlign": "center"},
        ),
        html.Div(
            [
                dcc.Graph(
                    figure=px.line(
                        trump_data,
                        x="Date",
                        y="Approval Index",
                        title="Trump Administration Approval Index(Rasmssen)",
                    )
                )
            ],
            style={"width": "60%", "height": 500, "margin": "5% auto 5%"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            figure=px.line(
                                trump_data,
                                x="Date",
                                y="Strongly Approve",
                                title="Strongly Approve",
                            )
                        )
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Graph(
                            figure=px.line(
                                trump_data,
                                x="Date",
                                y="Strongly Disapprove",
                                title="Strongly Disapprove",
                            )
                        )
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
            ],
            style={"width": "90%", "height": 500, "margin": "auto"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            figure=px.line(
                                trump_data,
                                x="Date",
                                y="Strongly Approve",
                                title="Total Approve",
                            )
                        )
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Graph(
                            figure=px.line(
                                trump_data,
                                x="Date",
                                y="Strongly Approve",
                                title="Total Disapprove",
                            )
                        )
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
            ],
            style={"width": "90%", "height": 500, "margin": "auto"},
        ),
        bto_menu
    ])


# e-Stats
# estats = html.Div(
#     [
#         html.Div([html.H1("e-Statsデータテーブル検索テーブル", style={"textAlign": "center"})]),
#         html.Div(
#             [
#                 DataTable(
#                     id="table",
#                     columns=[{"name": i, "id": i} for i in jp_stats_csv.columns],
#                     data=jp_stats_csv.to_dict("records"),
#                     sort_action="native",
#                     filter_action="native",
#                     fixed_rows={"headers": True, "data": 0},
#                     page_size=150000,
#                     virtualization=True,
#                     style_cell={
#                         "minWidth": "0px",
#                         "maxWidth": "180px",
#                         "whiteSpace": "no-wrap",
#                         "textOverflow": "ellipsis",
#                     },
#                     style_table={"height": "900px"},
#                 )
#             ],
#             style={"height": "1200px", "width": "90%", "margin": "auto"},
#         ),
#     ]
# )

# KYOTO HOTEL MAP
kyoto_hotels = html.Div([
    html.P(id="kyoto-title",
           style={"fontSize": 30, "display": "inline-block"}),
    html.Button(id="kyoto-button", children="Push Me!", n_clicks=1, style={
        "display": "inline-block", "marginLeft": "3%"}),
    html.P("PUSH ME ボタンを押すと1930年代からのホテルの増加状況が分かります", style={"fontSize": 30}),
    dcc.Graph(id="kyoto-map"),
    dcc.Interval(id="interval-comp",
                 interval=1*150, n_intervals=0, max_intervals=82),
    html.Div([
        dcc.Link("データは京都市オープンデータポータルサイトより(2018年12月まで)",
                 href="https://data.city.kyoto.lg.jp/node/14909")], style={"textAlign": "right", "marginRight": "3%"}),
    bto_menu
], style={"width": "90%", "margin": "auto"})


@app.callback([Output("kyoto-map", "figure"),
               Output("kyoto-title", "children")],
              [Input("interval-comp", "n_intervals"),
               Input("kyoto-button", "n_clicks")])
def update_graph(n_intervals, n_clicks):
    if n_clicks % 2 == 0:
        cnt = n_intervals % 83
        dff = df_kyoto_hotels[df_kyoto_hotels['year']
                              <= df_kyoto_hotels['year'].min() + cnt]
        return {"data": [
            go.Scattermapbox(
                lat=dff["ido"],
                lon=dff["keido"],
                mode="markers",
                marker=dict(size=9),
                # name=dff["hotel_name"]
            )],
            "layout": go.Layout(
            autosize=True,
            hovermode="closest",
            mapbox=dict(
                accesstoken=mapbox_accesstoken,
                center=dict(lat=np.mean(df_kyoto_hotels["ido"]),
                            lon=np.mean(df_kyoto_hotels["keido"])),
                pitch=90,
                zoom=12),
            height=899
        )
        }, "{}年の京都宿泊所状況".format(df_kyoto_hotels['year'].min() + cnt)

    else:
        return {"data": [
            go.Scattermapbox(
                lat=df_kyoto_hotels[df_kyoto_hotels["age"] == i]["ido"],
                lon=df_kyoto_hotels[df_kyoto_hotels["age"] == i]["keido"],
                mode="markers",
                marker=dict(size=9),
                text=df_kyoto_hotels[df_kyoto_hotels["age"]
                                     == i]["hotel_name"],
                name=str(i)
            ) for i in df_kyoto_hotels["age"].unique()],
            "layout": go.Layout(
            autosize=True,
            hovermode="closest",
            mapbox=dict(
                accesstoken=mapbox_accesstoken,
                center=dict(lat=np.mean(df_kyoto_hotels["ido"]),
                            lon=np.mean(df_kyoto_hotels["keido"])),
                pitch=90,
                zoom=12),
            height=899
        )
        }, "{}年の京都宿泊所状況".format(df_kyoto_hotels['year'].max())

@app.callback(Output("interval-comp", "n_intervals"),
              [Input("kyoto-button", "n_clicks")])
def count_zero(n_clicks):
    return 0

# KITAKYUSYU-SHELTER


kitakyushu = html.Div(
    [
        html.Div(
            [
                html.H1("北九州避難所マップ", style={
                        "textAlign": "center", "fontSize": 40}),
                DataTable(
                    id="fukuoka-datatable",
                    style_cell={
                        "textAlign": "center",
                        "maxWidth": "80px",
                        "whiteSpace": "normal",
                        "minWidth": "80px",
                    },
                    fixed_rows={"headers": True, "data": 0},
                    style_table={"maxHeight": 800, "maxWidth": "100%"},
                    filter_action="native",
                    row_selectable="multi",
                    sort_action="native",
                    sort_mode="multi",
                    page_size=700,
                    virtualization=True,
                    columns=[
                        {"name": i, "id": i, "deletable": True} for i in kitakyushu_shelter.columns
                    ],
                    data=kitakyushu_shelter.to_dict("records"),
                ),
                bto_menu
            ],
            # データテーブルにスタイルを与え、サイズを小さくする
            style={"height": 400, "width": "80%", "margin": "2% auto 5%"},
        ),
        # mapboxのアクセストークンを読み込む
        px.set_mapbox_access_token(
            "pk.eyJ1IjoibWF6YXJpbW9ubyIsImEiOiJjanA5Y3IxaWsxeGtmM3dweDh5bjgydGFxIn0.3vrfsqZ_kGPGhi4_npruGg"
        ),
        # mapのコールバック先のGraphクラス
        dcc.Graph(id="fukuoka-map"),
        bto_menu,
    ]
)

# コールバックの作成


@app.callback(
    # 出力先はGraphクラス
    Output("fukuoka-map", "figure"),
    [
        # 入力元はデータテーブル
        Input("fukuoka-datatable", "columns"),
        Input("fukuoka-datatable", "derived_virtual_data"),
    ],
)
def update_map(columns, rows):
    # ソートした後のデータでデータテーブルを作成する
    dff = pd.DataFrame(rows, columns=[c["name"] for c in columns])
    # そのデータを地図に示す
    return px.scatter_mapbox(
        dff,
        lat="緯度",
        lon="経度",
        zoom=10,
        hover_data=["名称", "名称かな表記", "住所表記"],
        labels={"fontSize": 20},
    )


# Page-Router
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/tsuyu-dash":
        return tsuyu_page
    elif pathname == "/us-yield":
        return us_yield
    elif pathname == "/japanese-gdp":
        return japanese_gdp
    elif pathname == "/trump-index":
        return t_index
    elif pathname == "/kyoto-hotels":
        return kyoto_hotels
    elif pathname == "/kitakyushu-shelter":
        return kitakyushu
    else:
        return index_page


if __name__ == "__main__":
    app.run_server(debug=True)
