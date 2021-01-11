import os 

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from app import app 

from dash.dependencies import Input, Output, State

sousu = pd.read_csv("src/sousu.csv")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
style_half = {"width": "50%", "display": "inline-block"}


# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app.config.suppress_callback_exceptions = True

# server = app.server 

layout = html.Div(
    [
        html.Div(
            [
        html.H1('日本の地域別将来推計人口観察'),
        
                html.H5("表示地域選択"),
                dcc.RadioItems(
                    id="jinko_radio_select",
                    options=[{"label": i, "value": i} for i in ["都道府県", "市/区", "町村"]],
                    value="都道府県",
                ),
                html.Div(id="selected_area_data"),
            ], style={'backgroundColor': '#C5E99B', 'padding': '2%'}
        ),
        html.Div([
        html.P('上のラジオボタンで観察する地域を選びます。'),
        html.P('都道府県を選ぶと都道府県、市区、町村を選択するとそれぞれの人口データが確認できます'),
        html.P('左のグラフの気になる地域をクリックすると、右にその人口ピラミッドが表示されます。'),
        html.P('さらに再生ボタンを押すと、その2045年までの推移が確認できます。'),
        html.P('データは国立社会保障・人口問題研究所の日本の地域別将来推計人口を用いました。'),
        html.A('リンク', href='http://www.ipss.go.jp/pp-shicyoson/j/shicyoson18/t-page.asp')
        ], style={'textAlign': 'center', 'padding': '2%'}),
    ],
    style={"padding": "5%", 'backgroundColor': '#67D5B5'},
)


def layout_double_drop(df):
    layout = html.Div(
        [
            html.Div(
                [
                    dcc.Dropdown(
                        id="todou_dropdown2",
                        options=[{"label": i, "value": i} for i in df["都道府県"].unique()],
                        value=["北海道"],
                        multi=True,
                        clearable=False,
                    ),
                    dcc.Dropdown(id="sicho_dropdown", multi=True, clearable=False),
                ]
            ),
            html.Div(
                [
                    dcc.Graph(id="shicho_multiple", style=style_half),
                    dcc.Graph(id="shicho_selected", style=style_half),
                ]
            ),
        ]
    )
    return layout


@app.callback(
    Output("selected_area_data", "children"), Input("jinko_radio_select", "value")
)
def update_jinko_layout(selected_value):
    if selected_value == "都道府県":

        todou_layout = html.Div(
            [
                dcc.Dropdown(
                    id="todou_dropdown",
                    options=[{"label": i, "value": i} for i in sousu["都道府県"].unique()],
                    value=["京都府"],
                    multi=True,
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="todou_graph_multi",
                            style={"width": "50%", "display": "inline-block"},
                        ),
                    
                        dcc.Graph(
                            id="todou_graph_selected",
                            style={"width": "50%", "display": "inline-block"}
                        ),
                    ]
                ),
            ]
        )
        return todou_layout
    elif selected_value == "市/区":
        selected_df = sousu[sousu["市などの別"].isin(["0", "1", "2"])]
        siku_layout = layout_double_drop(selected_df)
        return siku_layout
    else:
        selected_df = sousu[sousu["市などの別"].isin(["3"])]
        cho_layout = layout_double_drop(selected_df)
        return cho_layout


@app.callback(
    Output("sicho_dropdown", "options"),
    Output("sicho_dropdown", "value"),
    Input("todou_dropdown2", "value"),
    Input("jinko_radio_select", "value"),
)
def update_local_drop(selected_areas, radio_select):
    if selected_areas is []:
        dash.exceptions.PreventUpdate
    else:
        if radio_select == "市/区":
            selected_df = sousu[sousu["市などの別"].isin(["0", "1", "2"])]
            selected_df = selected_df[selected_df["都道府県"].isin(selected_areas)]
            selected_areas = selected_df["市区町村"].unique()
            selected_options = [{"label": i, "value": i} for i in selected_areas]
            first_value = selected_areas[0]
            return selected_options, [first_value]
        elif radio_select == "町村":
            selected_df = sousu[sousu["市などの別"].isin(["3"])]
            selected_df = selected_df[selected_df["都道府県"].isin(selected_areas)]
            selected_areas = selected_df["市区町村"].unique()
            selected_options = [{"label": i, "value": i} for i in selected_areas]
            first_value = selected_areas[0]
            return selected_options, [first_value]
        else:
            raise dash.exceptions.PreventUpdate

@app.callback(
    Output("todou_graph_multi", "figure"),
    Input("jinko_radio_select", "value"),
    Input("todou_dropdown", "value"),
)
def update_area_line(area_radio, selected_pref):
    if area_radio == "都道府県":
        selected_df = sousu[sousu["市などの別"] == "a"]
        selected_df = selected_df[selected_df["都道府県"].isin(selected_pref)]
        return px.line(selected_df, x="年", y="総数", color="都道府県", hover_name='都道府県')
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output('todou_graph_selected', 'figure'),
    Input('todou_graph_multi', 'clickData'),
    Input("todou_dropdown", "value"),
)
def update_pop_pyramid(clickData, pref_value):
    if clickData is None:
        clickData = {'points': [{'hovertext': f'{pref_value[0]}'}]}

    selected_area = clickData['points'][0]['hovertext']
    selected_df = sousu[sousu["市などの別"] == "a"]
    selected_df = selected_df[selected_df["都道府県"].isin([selected_area])]
    selected_df = selected_df.iloc[:, 4:].drop('総数', axis=1)
    melted_df = selected_df.melt(id_vars='年')
    return px.bar(melted_df, x='value', y='variable', orientation='h', animation_frame='年', title=f'年齢別人口分布（{selected_area}）')

@app.callback(Output('shicho_multiple', 'figure'),
    Input('jinko_radio_select', 'value'),
    Input('todou_dropdown2', 'value'),
    Input('sicho_dropdown', 'value')
)
def update_city_graph(radio_value, pref_value, city_value):
    if radio_value == "都道府県":
        raise dash.exceptions.PreventUpdate
    elif radio_value == '市/区':
        selected_df = sousu[sousu['市などの別'].isin(['0','1','2'])]
        selected_df = selected_df[selected_df['都道府県'].isin(pref_value)]
        selected_df = selected_df[selected_df['市区町村'].isin(city_value)]
        return px.line(selected_df, x='年', y='総数', color='市区町村', hover_name='市区町村')
    else:
        selected_df = sousu[sousu['市などの別'].isin(['3'])]
        selected_df = selected_df[selected_df['都道府県'].isin(pref_value)]
        selected_df = selected_df[selected_df['市区町村'].isin(city_value)]
        return px.line(selected_df, x='年', y='総数', color='市区町村', hover_name='市区町村') 

# この市区町村の部分を、右側のデータを最初に出るようにして記事を書く。

@app.callback(Output('shicho_selected', 'figure'), Input('jinko_radio_select', 'value'), Input('shicho_multiple', 'clickData'))
def update_city_pop_pyramid(radio_select, clickData):
    if clickData is None:
        raise dash.exceptions.PreventUpdate
    else:
        if radio_select == '市/区':
            selected_area = clickData['points'][0]['hovertext']
            selected_df = sousu[sousu["市などの別"].isin(['0', '1', '2'])]
            selected_df = selected_df[selected_df["市区町村"].isin([selected_area])]
            selected_df = selected_df.iloc[:, 4:].drop('総数', axis=1)
            melted_df = selected_df.melt(id_vars='年')
            return px.bar(melted_df, x='value', y='variable', orientation='h', animation_frame='年', title=f'年齢別人口分布（{selected_area}）')
        elif radio_select == '町村':
            selected_area = clickData['points'][0]['hovertext']
            selected_df = sousu[sousu["市などの別"].isin(['3'])]
            selected_df = selected_df[selected_df["市区町村"].isin([selected_area])]
            selected_df = selected_df.iloc[:, 4:].drop('総数', axis=1)
            melted_df = selected_df.melt(id_vars='年')
            return px.bar(melted_df, x='value', y='variable', orientation='h', animation_frame='年', title=f'年齢別人口分布（{selected_area}）')            


if __name__ == "__main__":
    app.run_server()