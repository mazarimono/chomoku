import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table
import numpy as np
import pandas as pd
import requests

from dash.dependencies import Input, Output
from app import app

## READ DATA

kyoto_data = pd.read_csv(
    "./src/kyoto-covid.csv", parse_dates=["announce_date", "leave_hospital", "d_date"]
)

kyoto_age = kyoto_data.groupby(["age", "sex"], as_index=False).count()
kyoto_announce = kyoto_data.groupby(["announce_date"], as_index=False).count()
kyoto_announce["cumsum"] = kyoto_announce["count"].cumsum()
kyoto_announce["cumsum_d"] = kyoto_announce["d_date"].cumsum()
kyoto_announce_sex = kyoto_data.groupby(
    ["announce_date", "sex"], as_index=False
).count()
kyoto_announce_sex["cumsum"] = kyoto_announce_sex["count"].cumsum()
kyoto_d = kyoto_data.groupby("d_date").count()

kyoto_sex = kyoto_data.groupby("sex", as_index=False).sum()
kyoto_area = kyoto_data.groupby("area", as_index=False).sum()
kyoto_area = kyoto_area.sort_values("count", ascending=False)
kyoto_area.columns = ["地域", "感染者数", "退院者数", "解除者数","死亡者数"]
kyoto_area["回復者数"] = kyoto_area["退院者数"] + kyoto_area["解除者数"]
kyoto_area_table = kyoto_area[["地域", "感染者数", "回復者数", "死亡者数"]]
kyoto_table_age = kyoto_data.groupby("age", as_index=False).sum()
kyoto_table_age = kyoto_table_age.sort_values("count", ascending=False)
kyoto_table_age.columns = ["年齢", "感染者数", "退院者数", "解除者数", "死亡者数"]
kyoto_table_age["回復者数"] = kyoto_table_age["退院者数"] + kyoto_table_age["解除者数"]
kyoto_table_age_add = kyoto_table_age[["年齢", "感染者数","回復者数", "死亡者数"]]

# 状態各数値
total_number = kyoto_announce.iloc[-1, -2]
today_number = kyoto_announce.iloc[-1, -3]
update_date = kyoto_announce.iloc[-1, 0]
d_number_cumsum = kyoto_announce.iloc[-1, -1]
d_number_today = kyoto_d.iloc[-1, -1]
taiin_number = kyoto_data.leave_hospital.count()
today_taiin = kyoto_data[
    kyoto_data.leave_hospital == update_date
].leave_hospital.count()
kaizyo_num = kyoto_data.kaizyo_count.sum()
today_kaizyo = kyoto_data[
    kyoto_data.leave_hospital == update_date
].kaizyo_date.count()
recovery_num = taiin_number + kaizyo_num
recovery_today = today_taiin + today_kaizyo



patient_num = total_number - d_number_cumsum - recovery_num 

recent_condition = pd.DataFrame(
    {"状態": ["患者数", "回復者数", "死亡者数"], "人数": [patient_num, recovery_num, d_number_cumsum]}
)

# data from API 

jp_data = requests.get("https://covid19-japan-web-api.now.sh/api/v1/prefectures")
kyoto_pcr = jp_data.json()[25]
kyoto_pcr_num = kyoto_pcr["pcr"]
kyoto_pcr_update = str(kyoto_pcr["last_updated"]["pcr_date"])
pcr_year = str(kyoto_pcr_update)[:4]
pcr_month = str(kyoto_pcr_update)[4:5] # 月が2桁になると問題が起こりそう
pcr_day = str(kyoto_pcr_update)[-2:]


# SET STYLE

box_style = {
    "width": "20%",
    "display": "inline-block",
    "backgroundColor": "aqua",
    "padding": "1%",
    "margin": "2%",
    "borderRadius": 20,
    "verticalAlign": "top",
}

# FIGURES

kyoto_tree = px.treemap(
    kyoto_age,
    path=["age", "sex"],
    values="count",
    labels="count",
    title="陽性者内訳（年代別、性別）",
    template={"layout": {"margin": {"l": 20, "r": 20, "t": 50, "b": 20}}},
)


condition_pie = px.pie(
    recent_condition,
    names="状態",
    values="人数",
    hole=0.4,
    title="感染者の状態",
    template={"layout": {"margin": {"l": 50, "r": 20, "t": 50, "b": 20}}},
)


sex_pie = px.pie(
    kyoto_sex,
    names="sex",
    values="count",
    hole=0.4,
    title="陽性者男女比",
    template={"layout": {"margin": {"l": 20, "r": 20, "t": 50, "b": 20}}},
)

bar_daily = px.bar(
    kyoto_announce_sex, x="announce_date", y="count", color="sex", title="京都府の新規感染者数"
)
bar_cumsum = px.bar(kyoto_announce, x="announce_date", y="cumsum", title="京都府の累計感染者数")

kyoto_table_area = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in kyoto_area_table.columns],
    data=kyoto_area_table.to_dict("records"),
    style_cell={"textAlign": "center", "fontSize": 20},
)

kyoto_table_age_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in kyoto_table_age_add.columns],
    data=kyoto_table_age_add.to_dict("records"),
    style_cell={"textAlign": "center", "fontSize": 20},
)

## レイアウト

layout = html.Div(
    [
        html.Div(
            [
                html.H3(
                    "京都府の新型コロナ感染者推移",
                    style={"display": "inline-block", "marginRight": 40},
                ),
                html.P(
                    f"最終更新日 {update_date.date()}",
                    style={"display": "inline-block"},
                    className="update_date",
                ),
                html.A(
                    "データ出所: 京都府ウェブページ",
                    href="https://www.pref.kyoto.jp/kentai/news/novelcoronavirus.html#F",
                    style={"display": "block"},
                ),
            ],
            style={"backgroundColor": "aqua", "borderRadius": 20, "padding": "2%"},
        ),
        html.Div(
            [
                #        html.Div([
                #            html.P(f"{update_date}の感染発表数"),
                #            html.H1(f"{today_number}名", style={"textAlign": "center"})
                #        ], style=box_style),
                html.Div(
                    [
                        html.H6("総感染者数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{total_number}名",
                            style={"textAlign": "center", "padding": 0},
                            className="total_num",
                        ),
                        html.H4(
                            f"前日比 +{today_number}",
                            style={"textAlign": "center"},
                            className="total_num_dod",
                        ),
                    ],
                    className="kyoto_box",
                ),
                html.Div(
                    [
                        html.H6("回復者数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{recovery_num}名",
                            style={"textAlign": "center"},
                            className="leave_hosp_num",
                        ),
                        html.H4(
                            f"前日比 +{recovery_today}",
                            style={"textAlign": "center"},
                            className="leave_hosp_num_dod",
                        ),
                    ],
                    className="kyoto_box",
                ),
                html.Div(
                    [
                        html.H6("死亡者数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{d_number_cumsum}名",
                            style={"textAlign": "center", "padding": 0},
                            className="death_num",
                        ),
                        html.H4(
                            f"前日比 +{d_number_today}",
                            style={"textAlign": "center", "padding": 0},
                            className="death_num_dod",
                        ),
                    ],
                    className="kyoto_box",
                ),
                html.Div(
                    [
                        html.H6("PCR検査数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{kyoto_pcr_num}件",
                            style={"textAlign": "center", "padding": 0},
                            className="death_num",
                        ),
                        html.H4(
                            f"{pcr_year}/{pcr_month}/{pcr_day}",
                            style={"textAlign": "center", "padding": 0},
                            className="death_num_dod",
                        ),
                    ],
                    className="kyoto_box",
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id="pie_selector",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in ["感染者状況", "陽性者男女比"]
                                    ],
                                    value="感染者状況",
                                ),
                                dcc.Graph(id="pie_area"),
                            ],
                            className="kyoto_sep kyoto_table",
                            style={"verticalAlign": "top"},
                        ),
                        dcc.Graph(figure=kyoto_tree, className="kyoto_sep kyoto_chart"),
                    ]
                ),
                html.Div(
                    [
                        dcc.RadioItems(
                            id="kyoto_bar_radio",
                            options=[{"label": i, "value": i} for i in ["新規感染数", "累計"]],
                            value="新規感染数",
                        ),
                        dcc.Graph(id="kyoto_bar_graph"),
                    ],
                    className="kyoto_sep kyoto_chart",
                ),
                html.Div(
                    [
                        dcc.RadioItems(
                            id="kyoto_table_radio",
                            options=[
                                {"label": i, "value": i} for i in ["年代別感染者数", "地域別感染者数"]
                            ],
                            value="年代別感染者数",
                        ),
                        html.Div(id="kyoto_table_show"),
                    ],
                    className="kyoto_sep kyoto_table",
                ),
                html.Div(
                    [
                        html.H4("利用データ"),
                        html.P("EXPORTボタンを押すと、データがCSVでダウンロードできます"),
                        dash_table.DataTable(
                            columns=[{"id": i, "name": i} for i in kyoto_data.columns],
                            data=kyoto_data.to_dict("records"),
                            style_cell={"textAlign": "center"},
                            style_as_list_view=True,
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgb(248, 248, 248)",
                                }
                            ],
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            fixed_rows={"headers": True},
                            export_format="csv",
                            virtualization=True,
                        ),
                    ],
                    style={"margin": "2%", "padding": "1%"},
                    className="kyoto_sep",
                ),
            ]
        ),
    ],
    style={"padding": "1%"},
)


@app.callback(Output("kyoto_bar_graph", "figure"), [Input("kyoto_bar_radio", "value")])
def kyoto_bar_update(kyoto_radio_value):
    if kyoto_radio_value == "累計":
        return bar_cumsum
    else:
        return bar_daily


@app.callback(Output("pie_area", "figure"), [Input("pie_selector", "value")])
def update_pie_chart(pie_value):
    if pie_value == "陽性者男女比":
        return sex_pie
    return condition_pie


@app.callback(
    Output("kyoto_table_show", "children"), [Input("kyoto_table_radio", "value")]
)
def kyoto_table_update(kyoto_table_switch):
    if kyoto_table_switch == "年代別感染者数":
        return kyoto_table_age_table
    else:
        return kyoto_table_area
