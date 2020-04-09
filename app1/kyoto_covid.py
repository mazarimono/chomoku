import dash_core_components as dcc  
import dash_html_components as html 
import plotly.express as px 
import dash_table
import numpy as np  
import pandas as pd  

from dash.dependencies import Input, Output 
from app import app

## READ DATA

kyoto_data = pd.read_csv("./src/kyoto-covid.csv",  parse_dates=["announce_date", "leave_hospital"], na_values=np.nan)
kyoto_data["count"] = 1
kyoto_age = kyoto_data.groupby(["age", "sex"], as_index=False).count()
kyoto_announce = kyoto_data.groupby(["announce_date"], as_index=False).count()
kyoto_announce["cumsum"] = kyoto_announce["count"].cumsum()
kyoto_announce_sex = kyoto_data.groupby(["announce_date", "sex"], as_index=False).count()
kyoto_announce_sex["cumsum"] = kyoto_announce_sex["count"].cumsum()
kyoto_sex = kyoto_data.groupby("sex", as_index=False).sum()
kyoto_area = kyoto_data.groupby("area", as_index=False).sum()
kyoto_area = kyoto_area.sort_values("count", ascending=False)

total_number = kyoto_announce.iloc[-1, -1]
today_number = kyoto_announce.iloc[-1, -2]
update_date = kyoto_announce.iloc[-1, 0]
taiin_number = kyoto_data.leave_hospital.count()
today_taiin = kyoto_data[kyoto_data.leave_hospital == update_date].leave_hospital.count()


# SET STYLE

box_style = {"width": "20%", "display": "inline-block", "backgroundColor": "aqua", "padding": "1%","margin": "2%", "borderRadius": 20, "verticalAlign": "top"}

# FIGURES

kyoto_tree = px.treemap(kyoto_age, path=["age", "sex"], values="count", labels="count", title="陽性者内訳（年代別、性別）")
sex_pie = px.pie(kyoto_sex, names="sex", values="count", hole=.4)

bar_daily = px.bar(kyoto_announce_sex, x="announce_date", y="count", color="sex", title="京都府の新規感染者数")
bar_cumsum = px.bar(kyoto_announce, x="announce_date", y="cumsum", title="京都府の累計感染者数")

kyoto_table = dash_table.DataTable(columns=[{"name": i, "id": i} for i in kyoto_area.columns], data=kyoto_area.to_dict("records"), style_cell={"textAlign": "center", "fontSize": 20})

## レイアウト

layout = html.Div([

    html.Div([
    html.H3("京都府の新型コロナ感染者推移", style={"display":"inline-block", "marginRight": 40}),
    html.P(f"最終更新日 {update_date.date()}", style={"display":"inline-block"}),
    ], style={"backgroundColor": "aqua", "borderRadius": 20, "padding": "2%"}),
    html.Div([
#        html.Div([
#            html.P(f"{update_date}の感染発表数"),
#            html.H1(f"{today_number}名", style={"textAlign": "center"})
#        ], style=box_style),
        html.Div([
            html.P("総感染者数"),
            html.H1(f"{total_number}名", style={"textAlign": "center", "padding": 0}),
            html.H4(f"前日比 +{today_number}", style={"textAlign": "center"}),
        ], style=box_style),
        html.Div([
            html.P("退院者数"),
            html.H1(f"{taiin_number}名", style={"textAlign": "center"}),
            html.H4(f"前日比 +{today_taiin}", style={"textAlign": "center"}),
        ], style=box_style)
    ]),

    html.Div([

        html.Div([

        dcc.Graph(figure=kyoto_tree, style={"width": "56%", "display": "inline-block","backgroundColor": "aqua", "borderRadius": 20, "padding": "2%"}, className="kyoto_sep"),
        dcc.Graph(figure=sex_pie, style={"width": "36%", "display": "inline-block","backgroundColor": "aqua", "borderRadius": 20, "padding": "2%"})

        ]),


        html.Div([
            dcc.RadioItems(
                id="kyoto_bar_radio",
                options=[{"label": i, "value": i} for i in ["新規感染数", "累計"]],
                value="新規感染数"
            ),
            dcc.Graph(id="kyoto_bar_graph")
        ], style={"width": "56%","backgroundColor": "aqua", "borderRadius": 20, "padding": "2%", "display": "inline-block"}),
        html.Div([
        html.H4("地域別感染者数"),
        kyoto_table
        ], style={"width": "34%", "margin": "2%", "display": "inline-block", "backgroundColor": "aqua", "padding": "1%", "borderRadius": 20,}),

        html.Div([
            html.H4("利用データ"),
            html.P("EXPORTボタンを押すと、データがCSVでダウンロードできます"),
            dash_table.DataTable(
                columns=[{"id": i, "name": i} for i in kyoto_data.columns], data=kyoto_data.to_dict("records"),
                style_cell={"textAlign":"center"},
                style_as_list_view=True,
                style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    export_format="csv",
    virtualization=True
                ),
        ], style={"margin": "2%", "padding": "1%"})    
    ]),





], style={"padding": "1%"})

@app.callback(Output("kyoto_bar_graph", "figure"), [Input("kyoto_bar_radio", "value")])
def kyoto_bar_update(kyoto_radio_value):
    if kyoto_radio_value == "累計":
        return bar_cumsum
    else:
        return bar_daily