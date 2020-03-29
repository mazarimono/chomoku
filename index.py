from app import app 

import dash_html_components as html 
import dash_core_components as dcc 

from dash.dependencies import Input, Output  

from app1 import covid_memo 
from app1 import covid_19 
from app1 import hands_on_02 


server = app.server


app.layout = html.Div([dcc.Location(id="url"), html.Div(id="page-content")])

test = html.H1("TEST")

@app.callback(Output("page-content", "children"), 
        [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/memo":
        return covid_memo.layout
    elif pathname == "/hands-on-02":
        return hands_on_02.layout
    else:
        return covid_19.layout

if __name__ == "__main__":
    app.run_server(debug=True) 
