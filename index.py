from app import app

import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output

from app1 import toyo 
from app1 import covid_memo
from app1 import hands_on_02
from app1 import hands_on_03
from app1 import why_interactive 
# from app1 import kyoto_covid
# from app1 import world_index
# from app1 import stress_check


server = app.server


app.layout = html.Div([dcc.Location(id="url"), html.Div(id="page-content")])

test = html.H1("TEST")


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/memo":
        return covid_memo.layout
    elif pathname == "/hands-on-02":
        return hands_on_02.layout
    elif pathname == "/hands-on-03":
        return hands_on_03.layout
    #elif pathname == "/kyoto-covid":
    #    return kyoto_covid.layout
    elif pathname == "/toyo":
        return toyo.layout 
    elif pathname == '/qiita-20201212':
        return why_interactive.layout 

    # elif pathname == "/world-index":
    #     return world_index.layout
    # elif pathname == "/stress-check":
    #     return stress_check.layout
    else:
        return covid_memo.layout


if __name__ == "__main__":
    app.run_server()
