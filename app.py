import json
import os
from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_alternative_viz as dav
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
import altair as alt
from bokeh.embed import json_item
import holoviews as hv
import matplotlib.pyplot as plt
import seaborn as sns
from dash.dependencies import Input, Output

# Tsuyu Data Read
dftsuyu = pd.read_csv(
    "./src/all.csv", index_col=0, parse_dates=["enter", "exit", "g-enter", "g-exit"]
)
df2tsuyu = pd.read_csv(
    "./src/all2.csv", index_col=0, parse_dates=["enter", "exit", "date"]
)

# # US YIELD DATA
# # Data
# start = datetime(2000, 1, 1)
# today = datetime.today()

# dfyield = web.DataReader(
#     [
#         "DFF",
#         "DGS3MO",
#         "DGS2",
#         "DGS5",
#         "DGS10",
#         "DGS30",
#         "TEDRATE",
#         "T10YIE",
#         "T10Y3M",
#         "T10Y2Y",
#         "BAA10Y",
#     ],
#     "fred",
#     start,
#     today,
# )
# dfyield["date"] = dfyield.index
# dfyield.columns = [
#     "ffrate",
#     "3mT",
#     "2yT",
#     "5yT",
#     "10yT",
#     "30yT",
#     "tedspread",
#     "breakeven10Y",
#     "3m10ySpread",
#     "2y10ySpread",
#     "baa10ySpread",
#     "date",
# ]
# dfyield["30yT"] = dfyield["30yT"].fillna(0)

# yieldOnly = dfyield[["date", "ffrate", "3mT", "2yT", "5yT", "10yT", "30yT"]].dropna()
# spreads = dfyield[
#     ["date", "tedspread", "3m10ySpread", "2y10ySpread", "baa10ySpread"]
# ].dropna()

# JP GDP DATA
dfgdp = pd.read_csv("./src/japanese-gdp-19552007.csv")

# # RUSMUSSEN TRUMP INDEX
# trump_data = pd.read_html(
#     "http://www.rasmussenreports.com/public_content/politics/trump_administration/trump_approval_index_history",
#     parse_dates=["Date"],
# )[0]


# APP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
                html.H1(
                    "20190607:  ",
                    style={"display": "inline-block", "marginRight": "1%"},
                ),
                dcc.Link(
                    "Japanese rainy season dashboard",
                    href="/tsuyu-dash",
                    style={"fontSize": 40},
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        # html.Div(
        #     [
        #         html.H1(
        #             "20190614:  ",
        #             style={"display": "inline-block", "marginRight": "1%"},
        #         ),
        #         dcc.Link("US Yield Watch", href="/us-yield", style={"fontSize": 40}),
        #     ],
        #     style={"textAlign": "center"},
        # ),
        # html.Br(),
        html.Div(
            [
                html.H1(
                    "20190625:  ",
                    style={"display": "inline-block", "marginRight": "1%"},
                ),
                dcc.Link(
                    "Japanese GDP(YoY %)", href="/japanese-gdp", style={"fontSize": 40}
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        # html.Div(
        #     [
        #         html.H1(
        #             "20190625:  ",
        #             style={"display": "inline-block", "marginRight": "1%"},
        #         ),
        #         dcc.Link(
        #             "Trump Administration Approval Index Data from Rasmussen Report",
        #             href="/trump-index",
        #             style={"fontSize": 40},
        #         ),
        #     ],
        #     style={"textAlign": "center"},
        # ),
        html.Div(
            [
                html.H1(
                    "20191118: ", style={"display": "inline-block", "marginRight": "1%"}
                ),
                dcc.Link(
                    "Foreigner Tourist Number in Japan",
                    href="/tourist-number",
                    style={"fontSize": 40},
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.H1(
                    "20200110: ", style={"display": "inline-block", "marginRight": "1%"}
                ),
                dcc.Link(
                    "Olympic Medals",
                    href="/medal",
                    style={"fontSize": 40},
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
                    style={"width": "50%", "margin": "1% auto 1%", "fontSize": "1.2vw",},
                    labelStyle={"display": "inline-block"}
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
                                    dftsuyu["year"].min(), dftsuyu["year"].max()
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
                    style={"width": "60%", "margin": "1% auto", "fontSize": "1vw"},
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
        ),
        html.Div(
            [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
            style={"textAlign": "center"},
        ),
    ]
)


@app.callback(
    [Output("area-chart", "figure"), Output("sub-title", "children")],
    [Input("area-select-dropdown", "value"), Input("area-range-slider", "value")],
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
            range_x=[dftsuyu["g-enter"].min() - d, dftsuyu["g-enter"].max() + d],
            range_y=[dftsuyu["g-exit"].min() - d, dftsuyu["g-exit"].max() + d],
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
        "Historical tsuyu enter-data and exit-date Chart: {} ".format(areaName),
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
            gannt_data, title="Difference of Area; Year {}".format(selected_year)
        ),
        "Scatter plot: {} xaxis: length of rainy season, yaxis: precipitational amount(average value: 100)".format(
            areaName
        ),
    )


# ## Contents US YIELD CURVE

# us_yield = html.Div(
#     [
#         html.Div(
#             [
#                 html.H1("US Yield Data", style={"textAlign": "center"}),
#                 dcc.DatePickerRange(
#                     id="date-picker",
#                     minimum_nights=5,
#                     clearable=True,
#                     start_date=datetime(2000, 1, 1),
#                     style={"display": "block"},
#                 ),
#                 html.Div(
#                     [
#                         dcc.Graph(
#                             id="historical-left",
#                             hoverData={"points": [{"x": "2008-09-09"}]},
#                         ),
#                         # html.H3('見たい範囲を上の日付ピッカー、もしくはマウスのドラッグで選択できます', style={'textAlign': 'center'}),
#                     ],
#                     style={"width": "49%", "display": "inline-block"},
#                 ),
#                 html.Div(
#                     [
#                         html.H1(id="test"),
#                         dcc.Graph(id="yield-curve-right"),
#                         # html.H3('左の米国の主要金利のグラフでマウスホバーした地点のイールドカーブが表示できます。', style={'textAlign': 'center'}),
#                     ],
#                     style={"width": "49%", "display": "inline-block"},
#                 ),
#             ],
#             style={"height": "1000", "margin": "2%"},
#         ),
#         html.Div(
#             [
#                 html.Div(
#                     [html.H1("Major Yeild Spreads")], style={"textAlign": "center"}
#                 ),
#                 html.Div(
#                     [
#                         dcc.Dropdown(
#                             id="spread-dropdown",
#                             options=[
#                                 {"label": i, "value": i} for i in spreads.columns[1:]
#                             ],
#                             value="tedspread",
#                         )
#                     ],
#                     style={"width": "30%", "margin": "2% auto 2%"},
#                 ),
#                 html.Div(
#                     [dcc.Graph(id="spreadGraph")],
#                     style={"width": "60%", "margin": "0 auto 0"},
#                 ),
#             ]
#         ),
#         html.Div(
#             [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
#             style={"textAlign": "center"},
#         ),
#     ]
# )


# @app.callback(
#     dash.dependencies.Output("historical-left", "figure"),
#     [
#         dash.dependencies.Input("date-picker", "start_date"),
#         dash.dependencies.Input("date-picker", "end_date"),
#     ],
# )
# def makeYieldHist(start_date, end_date):
#     histdf = yieldOnly[start_date:end_date]
#     histdf = pd.melt(
#         histdf,
#         id_vars="date",
#         value_vars=["ffrate", "3mT", "2yT", "5yT", "10yT", "30yT"],
#     )
#     return {
#         "data": [
#             go.Scatter(
#                 x=histdf[histdf["variable"] == i]["date"],
#                 y=histdf[histdf["variable"] == i]["value"],
#                 name=i,
#             )
#             for i in histdf["variable"].unique()
#         ],
#         "layout": {"title": "US Yeild"},
#     }


# @app.callback(
#     dash.dependencies.Output("yield-curve-right", "figure"),
#     [dash.dependencies.Input("historical-left", "hoverData")],
# )
# def makeYieldCurve(hoverData):

#     try:
#         selectedDate = hoverData["points"][0]["x"]
#     except:
#         selectedDate = datetime(2008, 9, 9)

#     selecteddf = yieldOnly[yieldOnly["date"] == selectedDate]
#     return {
#         "data": [
#             go.Parcoords(
#                 line=dict(color="blue"),
#                 dimensions=list(
#                     [
#                         dict(
#                             range=[0, 7], label="FF Rate", values=selecteddf["ffrate"]
#                         ),
#                         dict(
#                             range=[0, 7], label="3M Treasury", values=selecteddf["3mT"]
#                         ),
#                         dict(
#                             range=[0, 7], label="2Y Treasury", values=selecteddf["2yT"]
#                         ),
#                         dict(
#                             range=[0, 7], label="5Y Treasury", values=selecteddf["5yT"]
#                         ),
#                         dict(
#                             range=[0, 7],
#                             label="10Y Treasury",
#                             values=selecteddf["10yT"],
#                         ),
#                         dict(
#                             range=[0, 7],
#                             label="30Y Treasury",
#                             values=selecteddf["30yT"],
#                         ),
#                     ]
#                 ),
#             )
#         ],
#         "layout": {"title": "Yield Curve Date: {}".format(selectedDate)},
#     }


# @app.callback(
#     dash.dependencies.Output("spreadGraph", "figure"),
#     [dash.dependencies.Input("spread-dropdown", "value")],
# )
# def spreadGraph(selectedvalue):
#     dfspread = spreads[["date", selectedvalue]]
#     return {
#         "data": [
#             go.Scatter(
#                 x=dfspread["date"], y=dfspread[selectedvalue], name=selectedvalue
#             )
#         ]
#     }


japanese_gdp = html.Div(
    [
        html.H1("日本の実質GDP成長率（前年比%）", style={"textAlign": "center"}),
        html.Div(
            [
                dcc.Graph(
                    figure={"data": [go.Bar(x=dfgdp["暦年"], y=dfgdp["GDP実質前年比（％）"])]}
                )
            ]
        ),
        html.Div(
            [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
            style={"textAlign": "center"},
        ),
    ]
)

# # TRUMP INDEX
# t_index = html.Div(
#     [
#         html.Div(
#             [
#                 html.H1("Trump Administration Approval Index"),
#                 html.H1("Data from RASMUSSEN REPORTS"),
#                 html.Div(
#                     [
#                         "URL : ",
#                         html.A(
#                             "http://www.rasmussenreports.com/public_content/politics/trump_administration/trump_approval_index_history"
#                         ),
#                     ]
#                 ),
#                 html.H3(
#                     children=["Update: {}".format(str(trump_data["Date"].max())[:10])]
#                 ),
#                 html.H3("Latest Approval Index: {}".format(trump_data.iloc[0, 1])),
#             ],
#             style={"textAlign": "center"},
#         ),
#         html.Div(
#             [
#                 dcc.Graph(
#                     figure=px.line(
#                         trump_data,
#                         x="Date",
#                         y="Approval Index",
#                         title="Trump Administration Approval Index(Rasmssen)",
#                     )
#                 )
#             ],
#             style={"width": "60%", "height": 500, "margin": "5% auto 5%"},
#         ),
#         html.Div(
#             [
#                 html.Div(
#                     [
#                         dcc.Graph(
#                             figure=px.line(
#                                 trump_data,
#                                 x="Date",
#                                 y="Strongly Approve",
#                                 title="Strongly Approve",
#                             )
#                         )
#                     ],
#                     style={"width": "50%", "display": "inline-block"},
#                 ),
#                 html.Div(
#                     [
#                         dcc.Graph(
#                             figure=px.line(
#                                 trump_data,
#                                 x="Date",
#                                 y="Strongly Disapprove",
#                                 title="Strongly Disapprove",
#                             )
#                         )
#                     ],
#                     style={"width": "50%", "display": "inline-block"},
#                 ),
#             ],
#             style={"width": "90%", "height": 500, "margin": "auto"},
#         ),
#         html.Div(
#             [
#                 html.Div(
#                     [
#                         dcc.Graph(
#                             figure=px.line(
#                                 trump_data,
#                                 x="Date",
#                                 y="Strongly Approve",
#                                 title="Total Approve",
#                             )
#                         )
#                     ],
#                     style={"width": "50%", "display": "inline-block"},
#                 ),
#                 html.Div(
#                     [
#                         dcc.Graph(
#                             figure=px.line(
#                                 trump_data,
#                                 x="Date",
#                                 y="Strongly Approve",
#                                 title="Total Disapprove",
#                             )
#                         )
#                     ],
#                     style={"width": "50%", "display": "inline-block"},
#                 ),
#             ],
#             style={"width": "90%", "height": 500, "margin": "auto"},
#         ),
#         html.Div(
#             [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
#             style={"textAlign": "center", "marginTop": 100},
#         ),
#     ]
# )


# tourist in japan

df = pd.read_csv(
    "./src/tourist.csv",
    index_col=0, parse_dates=["date"]
)
df = df.sort_values("date")
delist = ["総数", "アジア計", "ヨーロッパ計", "アフリカ計", "北アメリカ計", "南アメリカ計", "オセアニア計"]
df = df[~df["country"].isin(delist)]
df_number = df[df["type"] == "actual_number"]
df_number = df_number.dropna()
df_percent = df[df["type"] == "percentage"]
df_percent = df_percent.dropna()

tourist_date = list(df_number["date"].unique())
tourist_date.sort()

tourist_n = html.Div(
    [
        html.H1("訪日外国人動向", style={"textAlign": "center"}),
        html.Div(
            [
                dcc.Graph(
                    id="tourist_bar",
                    figure=px.bar(df_number, x="date", y="number", color="country"),
                    hoverData = {"points": [{"x": np.datetime64(tourist_date[-1], "D")}]}
                ),
                html.Div(
                    [
                        dcc.RangeSlider(
                            id="tourist_rangeslider",
                            max=len(tourist_date),
                            min=0,
                            value=[0, len(tourist_date)],
                            marks={
                                i: "{}".format(np.datetime64(tourist_date[i], "M"))
                                for i in range(0, len(tourist_date), 12)
                            },
                            pushable=12
                        )
                    ],
                    style={"width": "90%", "margin": "auto"},
                ),
            ],
            style={"width": "65%", "float": "left"},
        ),
        html.Div([
            dcc.Graph(id="pie-graph"),
        ], style={"width": "35%", "display": "inline-block"}),
        html.Br(),
        html.Div([
        html.A("Data From / 日本政府観光局　訪日外国人", href="https://www.jnto.go.jp/jpn/statistics/visitor_trends/",
        target="_blank")], style={"margin":"5% auto", "textAlign":"center"}),
        html.Div(
            [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
            style={"textAlign": "center"},
        ),
    ]
)


@app.callback(Output("tourist_bar", "figure"), [Input("tourist_rangeslider", "value")])
def update_graph(values):
    min_d = values[0]
    min_date = tourist_date[min_d]
    min_date_d = np.datetime64(min_date, "M")
    max_d = values[1]
    max_date = tourist_date[max_d-1]
    max_date_d = np.datetime64(max_date, "M")
    dff = df_number[df_number["date"] >= min_date]
    dff = dff[dff["date"] <= max_date]
    return px.bar(dff, x="date", y="number", color="country", title=f"{min_date_d}から{max_date_d}の訪日外国人数（月別）")

@app.callback(Output("pie-graph", "figure"), [Input("tourist_bar", "hoverData")])
def update_pie(hoverData):
    hoverdate = hoverData["points"][0]["x"]
    select_d = np.datetime64(hoverdate, "M")
    dff = df_number[df_number["date"] == hoverdate]
    pie_graph = go.Pie(labels=dff["country"], values=dff["number"])
    return {"data": [pie_graph], "layout": go.Layout(height=600, title=f"{select_d}の国別比率")}

# qiita

hv.extension("bokeh")
gapminder = px.data.gapminder()


td_style = {"width": "50%", "margin": "20px"}

alt_viz1 = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(id="year",
                options=[{"label": i, "value": i} for i in gapminder.country.unique()],
                value=["Japan", "China", "United States"],
                multi=True),
                
            ],
            style={
                "width": "600px",
                "padding-bottom": "30px",
                "margin": "5% auto"
            },
        ),
        html.Table(
            [
                html.Tr(
                    [
                        html.Td([dcc.Graph(id="px")], style=td_style),
                        html.Td([dav.Svg(id="seaborn")], style=td_style),
                    ]
                ),
                html.Tr(
                    [
                        html.Td([dav.VegaLite(id="vega")], style=td_style),
                        html.Td([dav.BokehJSON(id="bokeh")], style=td_style),
                    ]
                ),
            ],
            style={"width": "1000px", "margin": "0 auto"},
        ),
    ]
)


@app.callback(Output("px", "figure"), [Input("year", "value")])
def plotly_fig(selected_countries):
    df = gapminder[gapminder.country.isin(selected_countries)]
    return px.scatter(
        df,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=30,
        color="continent",
        log_x=True,
        height=400,
        width=600,
        title="Plotly Express",
        hover_name="country",
        hover_data=df.columns,
    ).for_each_trace(lambda t: t.update(name=t.name.replace("continent=", "")))



@app.callback(Output("vega", "spec"), [Input("year", "value")])
def altair_fig(selected_countries):
    df = gapminder[gapminder.country.isin(selected_countries)]
    return (
        alt.Chart(df, height=250, width=500)
        .mark_circle()
        .encode(
            alt.X("gdpPercap:Q", scale=alt.Scale(type="log")),
            alt.Y("lifeExp:Q", scale=alt.Scale(zero=False)),
            size="pop:Q",
            color="continent:N",
            tooltip=list(df.columns),
        )
        .interactive()
        .properties(title="Altair / Vega-Lite")
        .to_dict()
    )


@app.callback(Output("bokeh", "json"), [Input("year", "value")])
def bokeh_fig(selected_countries):
    df = gapminder[gapminder.country.isin(selected_countries)]
    return json_item(
        hv.render(
            hv.Points(df, kdims=["gdpPercap", "lifeExp"]).opts(
                color="continent",
                size=hv.dim("pop") ** (0.5) / 800,
                logx=True,
                height=330,
                width=530,
                cmap="Category10",
                legend_position="bottom_right",
                title="HoloViews / Bokeh",
                tools=["hover"],
            )
        )
    )


@app.callback(Output("seaborn", "contents"), [Input("year", "value")])
def seaborn_fig(selected_countries):
    df = gapminder[gapminder.country.isin(selected_countries)]
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=df,
        ax=ax,
        x="gdpPercap",
        y="lifeExp",
        hue="continent",
        size="pop",
        sizes=(0, 800),
    )
    ax.set_xscale("log")
    ax.set_title("Seaborn / matplotlib")
    fig.set_size_inches(5.5, 3.5)
    fig.tight_layout()

    from io import BytesIO

    b_io = BytesIO()
    fig.savefig(b_io, format="svg")
    return b_io.getvalue().decode("utf-8")


alt_viz2 = html.Div(
    [
        html.Div(
            [
                dcc.Slider(
                    id="year1",
                    min=1952,
                    max=2007,
                    step=5,
                    marks={x: str(x) for x in range(1952, 2008, 5)},
                )
            ],
            style={
                "width": "600px",
                "padding-bottom": "30px",
                "margin": "0 auto"
            },
        ),
        html.Table(
            [
                html.Tr(
                    [
                        html.Td([dcc.Graph(id="px1")], style=td_style),
                        html.Td([dav.Svg(id="seaborn1")], style=td_style),
                    ]
                ),
                html.Tr(
                    [
                        html.Td([dav.VegaLite(id="vega1")], style=td_style),
                        html.Td([dav.BokehJSON(id="bokeh1")], style=td_style),
                    ]
                ),
            ],
            style={"width": "1000px", "margin": "0 auto"},
        ),
    ]
)


@app.callback(Output("px1", "figure"), [Input("year1", "value")])
def plotly_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    return px.scatter(
        df,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=30,
        color="continent",
        log_x=True,
        height=400,
        width=600,
        title="Plotly Express",
        hover_name="country",
        hover_data=df.columns,
    ).for_each_trace(lambda t: t.update(name=t.name.replace("continent=", "")))


@app.callback(Output("vega1", "spec"), [Input("year1", "value")])
def altair_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    return (
        alt.Chart(df, height=250, width=400)
        .mark_circle()
        .encode(
            alt.X("gdpPercap:Q", scale=alt.Scale(type="log")),
            alt.Y("lifeExp:Q", scale=alt.Scale(zero=False)),
            size="pop:Q",
            color="continent:N",
            tooltip=list(df.columns),
        )
        .interactive()
        .properties(title="Altair / Vega-Lite")
        .to_dict()
    )


@app.callback(Output("bokeh1", "json"), [Input("year1", "value")])
def bokeh_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    return json_item(
        hv.render(
            hv.Points(df, kdims=["gdpPercap", "lifeExp"]).opts(
                color="continent",
                size=hv.dim("pop") ** (0.5) / 800,
                logx=True,
                height=330,
                width=530,
                cmap="Category10",
                legend_position="bottom_right",
                title="HoloViews / Bokeh",
                tools=["hover"],
            )
        )
    )


@app.callback(Output("seaborn1", "contents"), [Input("year1", "value")])
def seaborn_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=df,
        ax=ax,
        x="gdpPercap",
        y="lifeExp",
        hue="continent",
        size="pop",
        sizes=(0, 800),
    )
    ax.set_xscale("log")
    ax.set_title("Seaborn / matplotlib")
    fig.set_size_inches(5.5, 3.5)
    fig.tight_layout()

    from io import BytesIO

    b_io = BytesIO()
    fig.savefig(b_io, format="svg")
    return b_io.getvalue().decode("utf-8")


source = pd.DataFrame([
      {'country': 'Great Britain', 'animal': 'gold'},
      {'country': 'Great Britain', 'animal': 'gold'},
      {'country': 'Great Britain', 'animal': 'gold'},
      {'country': 'Great Britain', 'animal': 'silver'},
      {'country': 'Great Britain', 'animal': 'silver'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'Great Britain', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'gold'},
      {'country': 'United States', 'animal': 'silver'},
      {'country': 'United States', 'animal': 'silver'},
      {'country': 'United States', 'animal': 'silver'},
      {'country': 'United States', 'animal': 'silver'},
      {'country': 'United States', 'animal': 'silver'},
      {'country': 'United States', 'animal': 'silver'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'United States', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'gold'},
      {'country': 'Germany', 'animal': 'gold'},
      {'country': 'Germany', 'animal': 'gold'},
      {'country': 'Germany', 'animal': 'gold'},
      {'country': 'Germany', 'animal': 'silver'},
      {'country': 'Germany', 'animal': 'silver'},
      {'country': 'Germany', 'animal': 'silver'},
      {'country': 'Germany', 'animal': 'silver'},
      {'country': 'Germany', 'animal': 'silver'},
      {'country': 'Germany', 'animal': 'silver'},
      {'country': 'Germany', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'bronze'},
      {'country': 'Germany', 'animal': 'bronze'}
    ])

emoji = html.Div([
    html.H1("各国のメダル獲得数"),
    dav.VegaLite(spec=alt.Chart(source).mark_text(size=45, baseline='middle').encode(
    alt.X('x:O', axis=None),
    alt.Y('animal:O', axis=None),
    alt.Row('country:N', header=alt.Header(title='')),
    alt.Text('emoji:N')
).transform_calculate(
    emoji="{'gold': '🥇', 'silver': '🥈', 'bronze': '🥉'}[datum.animal]"
).transform_window(
    x='rank()',
    groupby=['country', 'animal']
).properties(width=700, height=200).to_dict())
])


# Olympic Medal Data

medal_data = pd.read_csv("src/olympic_summer_medalist.csv", index_col=0)
term_min = medal_data["Year"].min()
term_max = medal_data["Year"].max()

olym_medal = html.Div([

    html.H1(id="olymedal-title"),

    html.Div([
        
        html.H3("表示グラフ選択"),
        dcc.Dropdown(id="olymedal-graph-type",
            options=[{"value": i, "label": i} for i in ["treemap", "line"]],
            value="treemap",
            style={"width":"80%", "textAlign":"center", "margin":"auto", "color":"black"}
        ),

        html.H3("メダル種類選択"),
        dcc.Dropdown(id="medal-type",
            options=[{"value": i, "label": i} for i in ["gold", "silver", "bronze", "sum"]],
            value="sum",
            style={"width":"80%", "textAlign":"center", "margin":"auto", "color":"black"}
        ),
        dcc.Markdown(
            """
            メダル種類選択の「sum」は金、銀、銅メダルの合計数です。スライダで表示年を選択できます。
            """,
            style={"fontSize": "2rem", "width":"80%","margin":"5% auto", "textAlign":"left"}
        )

    ], style={"width":"30%", "display":"inline-block", "verticalAlign":"top", "backgroundColor":"#FF9349","borderRadius":50}),

    html.Div([
    dcc.Graph(id="olymedal-graph",
    style={"width":"90%", "height": 500, "margin":"auto"}),

    ], style={"height":550, "width":"70%", "display":"inline-block", "borderRaddius":50}),

    html.Div([
        dcc.RangeSlider(
            id="olympic-year-range",
            min = term_min,
            max = term_max,
            value= [term_min, term_max],
            marks= {i: f"{i}" for i in range(term_min, term_max) if i % 20 == 0}
        )
    ], style={"width":"80%", "margin":"2% auto"}),


    html.Div([
        html.H3("表示国選択"),
        dcc.Dropdown(
        id="medalcountry-select",
        options=[{"value": c, "label": c} for c in medal_data.Country.unique()],
        multi=True,
        value=medal_data.Country.unique()
        )
    ], style={"width":"80%", "margin":"5% auto", "backgroundColor":"#FF9349", "padding":"3%",
            "borderRadius":50}),
    html.Div([
        dcc.Markdown("""
        
            本アプリケーションは[kaggleのオリンピックデータ](https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results/data#)を用い、夏のオリンピックのメダル獲得数を可視化しました。

        """,
        style={"fontSize": "2rem", "width":"80%","margin":"5% auto", "textAlign":"left"}
        )
    ], style={"width":"80%", "margin":"5% auto", "backgroundColor":"#FF9349", "padding":"3%",
            "borderRadius":50}),
    html.Div(
            [dcc.Link("Back to Menu", href="/", style={"fontSize": 40})],
            style={"textAlign": "center"},
        ),

], style={"textAlign": "center", "padding":"2%", "backgroundColor":"#ff7315", "color":"white",
        "borderRadius":30})

@app.callback(
    [Output("olymedal-graph", "figure"),
    Output("olymedal-title", "children")],
    [Input("olymedal-graph-type", "value"), 
    Input("medal-type", "value"),
    Input("olympic-year-range", "value"),
    Input("medalcountry-select", "value"),
    ])
def update_graph(graph_type, medal_type, year_range, selected_country):
    min_year = min(year_range)
    max_year = max(year_range)

    title_show = f"夏のオリンピックメダルデータ（{min_year}年～{max_year}年）"

    dff = medal_data[medal_data["Year"] >= min_year]
    dff = dff[dff["Year"] <= max_year]
    dff = dff[dff["Country"].isin(selected_country)]
    coun_gold = dff[dff["Medal"]=="Gold"]
    coun_gold = coun_gold.groupby("Country").count()
    coun_silver = dff[dff["Medal"]=="Silver"]
    coun_silver = coun_silver.groupby("Country").count()
    coun_bronze = dff[dff["Medal"]=="Bronze"]
    coun_bronze = coun_bronze.groupby("Country").count()
    cont_medal = pd.concat([coun_gold["ID"], coun_silver["ID"], coun_bronze["ID"]], axis=1, sort=True)
    cont_medal.columns = ["gold", "silver", "bronze"]
    cont_medal["sum"] = cont_medal.sum(axis=1)
    cont_medal["parents"] = ""
    cont_medal["index"] = cont_medal.index 
    cont_medal.sort_values(medal_type)
    if graph_type == "treemap":
        return px.treemap(cont_medal, values=medal_type, parents="parents", names="index"), title_show

    return px.bar(cont_medal, x="index", y=medal_type),title_show




# Page-Router
@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/tsuyu-dash":
        return tsuyu_page
    elif pathname == "/japanese-gdp":
        return japanese_gdp
    elif pathname == "/tourist-number":
        return tourist_n
    elif pathname == "/alt-viz1":
        return alt_viz1
    elif pathname == "/alt-viz2":
        return alt_viz2
    elif pathname == "/emoji":
        return emoji
    elif pathname == "/medal":
        return olym_medal
    else:
        return index_page


if __name__ == "__main__":
    app.run_server(debug=True)
