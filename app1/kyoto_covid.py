import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import dash_table
import numpy as np
import pandas as pd
from datetime import datetime 
from requests_html import HTMLSession 
import re 

from dash.dependencies import Input, Output
from app import app

## Make Data

# 日付を作る関数

def _split_reiwa(announce_day):
    # annouce_dayは令和〇年〇月〇日の形を想定
    # 結果は["令和〇"", "〇月〇日"]
    split_date = announce_day.split("年")
    return split_date

def _split_date(split_date):
    # split_dateは〇月〇日を想定
    
    split_date = split_date.split("（")[0]
    split_date = split_date.split("月")
    split_month = int(split_date[0])
    split_day = int(split_date[1].replace("日", ""))
    return split_month, split_day

def _reiwa_seireki(reiwa):
    # 令和を西暦に変換する
    # 令和の年は令和2という感じで年で分割を想定する
    try:
        reiwa_int = int(reiwa.replace("令和", ""))
    except:
        reiwa_int = int(reiwa.replace("零話", ""))
    seireki = 2018 + reiwa_int
    return seireki

def make_date(announce_day):
    first = _split_reiwa(announce_day)
    reiwa = first[0]
    reiwa_date = first[1]
    
    seireki = _reiwa_seireki(reiwa)
    reiwa_month, reiwa_day = _split_date(reiwa_date)
    
    datetime_announce = datetime(seireki, reiwa_month, reiwa_day).date()
    return datetime_announce

def get_data(table_num, p_state):
    df = pd.read_html("https://www.pref.kyoto.jp/kentai/corona/hassei1-50.html")[table_num]
    df = df.rename(columns={"Unnamed: 0": "case_num"})
    df["announce_date"] = df["発表日"].apply(lambda x: make_date(x))
    df["p_state"] = p_state 
    return df   

df_patient = get_data(0, "入院・療養")
df_exit = get_data(1, "退院等")
total_number = int(df_patient.iloc[0, 0].replace('例目', ''))

dff = pd.concat([df_patient, df_exit]) 
dfg = dff.groupby(["announce_date"], as_index=False).count()
dfg["cumsum"] = dfg["発表日"].cumsum()
kyoto_age = df_patient.groupby(["年代", "性別"], as_index=False).count()
kyoto_age["area"] = "京都府"
kyoto_sex = dff.groupby(["性別"], as_index=False).count()
kyoto_announce_sex = dff.groupby(["announce_date", "性別"], as_index=False).count()

update_date = max(dff["announce_date"])

# 死亡者数

session = HTMLSession()
r = session.get("https://www.pref.kyoto.jp/index.html")
table = r.html.find("table", containing="死亡")
text_num = re.search("死亡", table[0].text)
text_start_num = text_num.end()+1
text_end_num = text_start_num + 5
death_num = int(table[0].text[text_start_num:text_end_num].split("（")[0].replace("名", "")) # 死亡者数

# pdf掲載数

session = HTMLSession()
r = session.get('https://www.pref.kyoto.jp/kentai/corona/hassei1-50.html')
target_ul = r.html.find('ul')[6]
split_note = target_ul.text.split('から')
pdf_num = int(split_note[1].split('例目')[0]) 


# 状態各数値
#total_number = dfg.iloc[-1, -1]
today_number = dfg.iloc[-1, 3]
#update_date = dfg.iloc[-1, 1]
nyuin_num = len(df_patient)

out_num = total_number - nyuin_num - death_num 


taiin_number = out_num - death_num 
#today_taiin = len(kyoto_data[kyoto_data.leave_hospital == update_date])
#kaizyo_num = kyoto_data.kaizyo_count.sum()
#today_kaizyo = len(kyoto_data[kyoto_data.kaizyo_date == update_date])
recovery_num = out_num - death_num 
# recovery_today = today_taiin + today_kaizyo


patient_num = len(df_patient)

recent_condition = pd.DataFrame(
    {"状態": ["患者数", "回復者数", "死亡者数"], "人数": [patient_num, recovery_num, death_num]}
)


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
    path=["area","年代", "性別"],
    values="announce_date",
    labels="announce_date",
    title="現在の入院・療養者内訳（年代別、性別）",
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
    names="性別",
    values="発表日",
    hole=0.4,
    title="陽性者男女比",
    template={"layout": {"margin": {"l": 20, "r": 20, "t": 50, "b": 20}}},
)

bar_daily = px.bar(
    kyoto_announce_sex, x="announce_date", y="発表日", color="性別", title="京都府の新規感染者数"
)
dfg['pdf_cumsum'] = dfg['cumsum'] + pdf_num
bar_cumsum = px.area(dfg, x="announce_date", y="pdf_cumsum", title="京都府の累計感染者数")

# heatmap_age_day = go.Figure(
#     data=go.Heatmap(
#         z=kyoto_announce_date["count"],
#         y=kyoto_announce_date["age"],
#         x=kyoto_announce_date["announce_date"],
#         colorscale=[
#             [0, "rgb(166,206,227)"],
#             [0.25, "rgb(31,120,180)"],
#             [0.45, "rgb(178,223,138)"],
#             [0.65, "rgb(51,160,44)"],
#             [0.85, "rgb(251,154,153)"],
#             [1, "rgb(227,26,28)"],
#         ],
#     )
# )
# heatmap_age_day = heatmap_age_day.update_layout(title="年齢別新規感染者数")

# kyoto_table_area = dash_table.DataTable(
#     columns=[{"name": i, "id": i} for i in dff.columns],
#     data=dff.to_dict("records"),
#     style_cell={"textAlign": "center", "fontSize": 20},
# )

# kyoto_table_age_table = dash_table.DataTable(
#     columns=[{"name": i, "id": i} for i in kyoto_table_age_add.columns],
#     data=kyoto_table_age_add.to_dict("records"),
#     style_cell={"textAlign": "center", "fontSize": 20},
# )
update_date_str = f"{update_date.year}/ {update_date.month}/ {update_date.day}"

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
                    f"最終更新日 {update_date_str}",
                    style={"display": "inline-block"},
                    className="update_date",
                ),
                html.H4('本アプリケーションは集計の都合で再感染者も総感染者に含んでおります'),
                html.A(
                    "データ出所: 京都府ウェブページ",
                    href="https://www.pref.kyoto.jp/kentai/corona/hassei1-50.html",
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
                        html.H6("新規感染者数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{today_number}名",
                            style={"textAlign": "center", "padding": 0},
                            className="total_num",
                        ),
                        html.H4(
                            f"{update_date_str}",
                            style={"textAlign": "center"},
                            className="total_num_dod",
                        ),
                    ],
                    className="kyoto_box",
                ),
                html.Div(
                    [
                        html.H6("総感染者数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{total_number}名",
                            style={"textAlign": "center", "padding": 0},
                            className="total_num",
                        ),
                        # html.H4(
                        #     f"前日比 +{today_number}",
                        #     style={"textAlign": "center"},
                        #     className="total_num_dod",
                        # ),
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
                        # html.H4(
                        #     f"前日比 +{recovery_today}",
                        #     style={"textAlign": "center"},
                        #     className="leave_hosp_num_dod",
                        # ),
                    ],
                    className="kyoto_box",
                ),
                html.Div(
                    [
                        html.H6("死亡者数", style={"textAlign": "center", "padding": 0}),
                        html.H1(
                            f"{death_num}名",
                            style={"textAlign": "center", "padding": 0},
                            className="death_num",
                        ),
                        # html.H4(
                        #     f"前日比 +{d_number_today}",
                        #     style={"textAlign": "center", "padding": 0},
                        #     className="death_num_dod",
                        # ),
                    ],
                    className="kyoto_box",
                ),
                # html.Div(
                #     [
                #         html.H6("PCR検査数", style={"textAlign": "center", "padding": 0}),
                #         html.H1(
                #             f"{kyoto_pcr_num}件",
                #             style={"textAlign": "center", "padding": 0},
                #             className="death_num",
                #         ),
                #         html.H4(
                #             f"{pcr_year}/{pcr_month}/{pcr_day}",
                #             style={"textAlign": "center", "padding": 0},
                #             className="death_num_dod",
                #         ),
                #     ],
                #     className="kyoto_box",
                # ),
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
                            options=[
                                {"label": i, "value": i}
                                for i in ["新規感染数", "累計"]
                            ],
                            value="新規感染数",
                        ),
                        dcc.Graph(id="kyoto_bar_graph"),
                    ],
                    className="kyoto_sep kyoto_chart",
                ),
                # html.Div(
                #     [
                #         dcc.RadioItems(
                #             id="kyoto_table_radio",
                #             options=[
                #                 {"label": i, "value": i} for i in ["年代別感染者数", "地域別感染者数"]
                #             ],
                #             value="年代別感染者数",
                #         ),
                #         html.Div(id="kyoto_table_show"),
                #     ],
                #     className="kyoto_sep kyoto_table",
                #     style={"verticalAlign": "top"},
                # ),
                html.Div(
                    [
                        html.H4("利用データ"),
                        html.P("EXPORTボタンを押すと、データがCSVでダウンロードできます"),
                        dash_table.DataTable(
                            columns=[{"id": i, "name": i} for i in dff.columns],
                            data=dff.to_dict("records"),
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
    # elif kyoto_radio_value == "年齢別新規感染者数":
    #     return heatmap_age_day
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
