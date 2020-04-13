import dash_core_components as dcc 
import dash_html_components as html
import plotly.express as px 
from dash.dependencies import Input, Output, State 
import json  

from app import app 

gapminder = px.data.gapminder()
gap_jp = gapminder[gapminder["country"] == "Japan"]

handson1 = html.Div([dcc.Textarea(id="textarea"), html.H1(id="text_output")], style={"margin": "5%"})

@app.callback(Output("text_output", "children"), [Input("textarea", "value")])
def update_text1(textarea_value):
    return textarea_value

handson2 = html.Div(
    [
        dcc.Textarea(id="textarea2", style={"height": 300, "width": 800}),
        html.Button(id="my_button2", n_clicks=0, children="おす"),
        html.H1(id="text_output2"),
    ], style={"margin": "5%"}
)

@app.callback(
    Output("text_output2", "children"),
    [Input("my_button2", "n_clicks")],
    [State("textarea2", "value")],
)
def update_text2(n_clicks, textarea_value):
    return textarea_value

handson3 = html.Div(
    [
        dcc.Dropdown(
            id="drop3",
            options=[{"label": i, "value": i} for i in gapminder.columns[3:6]],
            value="lifeExp",
        ),
        dcc.Graph(id="my_graph3"),
    ], style={"margin": "5%"}
)

@app.callback(Output("my_graph3", "figure"), [Input("drop3", "value")])
def update_graph3(selected_value):
    return px.line(gap_jp, x="year", y=selected_value, title=f"日本の{selected_value}")

handson4 = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    id="select_country4",
                    options=[
                        {"value": i, "label": i} for i in gapminder.country.unique()
                    ],
                    value="Japan",
                )
            ],
            style={"width": "50%", "display": "inline-block"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="drop4",
                    options=[{"label": i, "value": i} for i in gapminder.columns[3:6]],
                    value="lifeExp",
                )
            ],
            style={"width": "50%", "display": "inline-block"},
        ),
        dcc.Graph(id="my_graph4"),
    ], style={"margin": "5%"}
)

@app.callback(
    Output("my_graph4", "figure"),
    [Input("select_country4", "value"), Input("drop4", "value")],
)
def update_graph4(selected_country, selected_value):
    dff = gapminder[gapminder.country == selected_country]
    return px.line(
        dff, x="year", y=selected_value, title=f"{selected_country}の{selected_value}"
    )

handson5 = html.Div(
    [
        dcc.Graph(
            id="my_graph5",
            figure=px.scatter(
                gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                animation_frame="year",
                log_x=True,
                range_y=[20, 90],
                color="continent",
                size_max=70,
                hover_data=["country"],
                template={"layout": {"dragmode": "select"}},
            ),
        ),
        html.H1(id="show_text5"),
    ], style={"margin": "5%"}
)

@app.callback(Output("show_text5", "children"), [Input("my_graph5", "selectedData")])
def update_content5(hoverData):
    return json.dumps(hoverData)

handson6 = html.Div(
    [
        dcc.Graph(
            id="my_graph6",
            figure=px.scatter(
                gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                animation_frame="year",
                log_x=True,
                range_y=[20, 90],
                color="continent",
                size_max=70,
                hover_data=["country"],
            ),
        ),
        dcc.Graph(id="show_figure1", style={"width": "33%", "display": "inline-block"}),
        dcc.Graph(id="show_figure2", style={"width": "33%", "display": "inline-block"}),
        dcc.Graph(id="show_figure3", style={"width": "33%", "display": "inline-block"}),
    ], style={"margin": "5%"}
)



@app.callback(
    [
        Output("show_figure1", "figure"),
        Output("show_figure2", "figure"),
        Output("show_figure3", "figure"),
    ],
    [Input("my_graph6", "hoverData")],
)
def update_content6(hoverData):
    if hoverData is None:
        raise dash.exceptions.PreventUpdate
    country = hoverData["points"][0]["customdata"][0]
    sele_data = gapminder[gapminder.country == country]
    return (px.line(sele_data, x="year", y="pop", title=f"{country}の人口データ"),
    px.line(sele_data, x="year", y="gdpPercap", title=f"{country}の1人当たりGDPデータ"),
    px.line(sele_data, x="year", y="lifeExp", title=f"{country}の平均余命データ"))

layout = html.Div([
    html.H1("APP1"),
    handson1,
    html.H1("APP2"),
    handson2,
    html.H1("APP3"),
    handson3,
    html.H1("APP4"),
    handson4,
    html.H1("APP5"),
    handson5,
    html.H1("APP6"),
    handson6
], style={"margin": "5%"})
