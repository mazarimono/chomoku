import dash   
import dash_core_components as dcc   
import dash_html_components as html  
import pandas as pd  
import plotly.express as px  

from dash.dependencies import Input, Output

from app import app 

data = pd.read_csv('./src/covid_daily.csv', parse_dates=['dateRep'])


layout =html.Div([
                      dcc.Dropdown(id='drop1',options=[{'label':i, 'value':i} for i in data.columns[2:].values], value='cases'),
                      dcc.Dropdown(id='drop2', options=[{'label': i, 'value': i} for i in data.countriesAndTerritories.unique()], value=['Japan'], multi=True),
                      dcc.RadioItems(id='radio', options=[{'value':i, 'label': i} for i in ['num', 'log']], value='num'),
                      dcc.Graph(id='graph')
])

@app.callback(Output('graph', 'figure'), Input('drop1', 'value'), Input('drop2', 'value'), Input('radio', 'value'))
def update_graph(selected_column, selected_countries, radio_value):
    selected_data = data[data['countriesAndTerritories'].isin(selected_countries)]
    if radio_value == 'log':
        return px.line(selected_data, x='dateRep', y=selected_column, color='countriesAndTerritories', log_y=True)
    else:
        return px.line(selected_data, x='dateRep', y=selected_column, color='countriesAndTerritories')

