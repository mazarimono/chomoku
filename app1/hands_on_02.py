import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


# データセットの読み込み

gapminder = px.data.gapminder()
jp_data = gapminder[gapminder["country"] == "Japan"]
gap_2007 = gapminder[gapminder["year"] == 2007]

# グラフの作成

jp_gdp = px.line(jp_data, x="year", y="gdpPercap")

world_2007 = px.scatter(
    gap_2007,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    log_x=True,
    log_y=True,
    size_max=80,
)

gap_map = px.scatter_geo(
    gapminder,
    locations="iso_alpha",
    size="gdpPercap",
    color="continent",
    animation_frame="year",
)

# レイアウトを渡す
layout = html.Div(
    [
        html.H1(
            "はんなりPython Dash ハンズオン レイアウト編",
            style={
                "textAlign": "center",
                "color": "red",
                "padding": "3%",
                "backgroundColor": "#cff09e",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H2("はんなりPython"),
                        html.Img(src="assets/hannari.png", style={"width": "100%"}),
                    ],
                    style={
                        "width": "48%",
                        "padding": "1%",
                        "display": "inline-block",
                        "backgroundColor": "#FBFFB9",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            style={
                                "borderRadius": "50%",
                                "backgroundColor": "lime",
                                "height": 200,
                                "width": 200,
                                "display": "inline-block",
                            }
                        ),
                        html.Button(
                            "ボタン",
                            style={
                                "borderRadius": "50%",
                                "backgroundColor": "red",
                                "height": 100,
                                "width": 100,
                                "display": "inline-block",
                                "verticalAlign": "center",
                            },
                        ),
                        html.Button(
                            "ボタン",
                            style={
                                "borderRadius": "50%",
                                "backgroundColor": "red",
                                "height": 50,
                                "width": 50,
                                "display": "inline-block",
                                "verticalAlign": "top",
                            },
                        ),
                        dcc.Markdown(
                            """マークダウン     
        マークダウンはdash_core_componentsに含まれる
    """,
                            style={
                                "fontSize": 20,
                                "color": "yellow",
                                "backgroundColor": "black",
                                "padding": "2%",
                            },
                        ),
                        dcc.Slider(
                            min=-20,
                            max=100,
                            value=30,
                            marks={i: f"{i}" for i in range(-20, 101, 20)},
                        ),
                    ],
                    style={
                        "width": "48%",
                        "padding": "1%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "backgroundColor": "#a5dff9",
                    },
                ),
            ]
        ),
        html.Div(
            [
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="label One",
                            value="label One",
                            children=dcc.Graph(figure=jp_gdp),
                        ),
                        dcc.Tab(
                            label="label Two",
                            value="label Two",
                            children=dcc.Graph(figure=world_2007),
                        ),
                        dcc.Tab(
                            label="label Three",
                            value="label Three",
                            children=dcc.Graph(figure=gap_map),
                        ),
                    ],
                    value="label One",
                )
            ]
        ),
    ],
    style={"backgroundColor": "#FFEEE4", "padding": "2%"},
)


