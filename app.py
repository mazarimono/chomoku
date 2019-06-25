import dash  
import dash_core_components as dcc  
import dash_html_components as html  
from dash.dependencies import Input, Output 
import plotly_express as px 
import plotly.graph_objs as go  
import plotly.figure_factory as ff 
import pandas as pd 
import pandas_datareader.data as web 
from datetime import datetime 
from datetime import timedelta
import os 


# Tsuyu Data Read
dftsuyu = pd.read_csv('./src/all.csv', index_col = 0, parse_dates = ['enter', 'exit', 'g-enter', 'g-exit'])
df2tsuyu = pd.read_csv('./src/all2.csv', index_col = 0, parse_dates = ['enter', 'exit', 'date'])

# US YIELD DATA
# Data 
start = datetime(2000, 1, 1)
today = datetime.today()

dfyield = web.DataReader(['DFF', 'DGS3MO', 'DGS2', 'DGS5', 'DGS10', 'DGS30', 'TEDRATE', 'T10YIE', 'T10Y3M', 'T10Y2Y', 'BAA10Y'], 'fred', start, today)
dfyield['date'] = dfyield.index
dfyield.columns =['ffrate', '3mT', '2yT', '5yT', '10yT', '30yT', 'tedspread', 'breakeven10Y', '3m10ySpread', '2y10ySpread', 'baa10ySpread', 'date']
dfyield['30yT'] = dfyield['30yT'].fillna(0)

yieldOnly = dfyield[['date', 'ffrate', '3mT', '2yT', '5yT', '10yT', '30yT']].dropna()
spreads = dfyield[['date', 'tedspread', '3m10ySpread', '2y10ySpread', 'baa10ySpread']].dropna()

# JP GDP DATA
dfgdp = pd.read_csv('./src/japanese-gdp-19552007.csv')

## APP 
app = dash.Dash(__name__)

server = app.server

app.config.suppress_callback_exceptions = True

# layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1('CHOMOKU DASHBOARD', style = {'textAlign': 'center', 'color': '#5A9367', 'fontSize': '2vw', 'padding': '2%', 'backgroundColor': '#D7FFF1'}),
    html.Div(id = 'page-content')
])

# index_page
index_page = html.Div([
    html.Title('CHOMOKU DASHBOARD'),
    html.Div([
    html.H1('20190607:  ', style = {'display': 'inline-block','marginRight': '1%'}),
    dcc.Link('Japanese rainy season dashboard', href = '/tsuyu-dash', style = {'fontSize': 40})], style={'textAlign': 'center'}),
    html.Br(),
    html.Div([
    html.H1('20190614:  ', style = {'display': 'inline-block','marginRight': '1%'}),
    dcc.Link('US Yield Watch', href = '/us-yield', style = {'fontSize': 40})], style={'textAlign': 'center'}),
    html.Br(),
    html.Div([
    html.H1('20190625:  ', style = {'display': 'inline-block','marginRight': '1%'}),
    dcc.Link('Japanese GDP(YoY %)', href = '/japanese-gdp', style = {'fontSize': 40})], style={'textAlign': 'center'})
    
])

# Contents Tsuyu_page
tsuyu_page = html.Div([
    html.H1('HOW ABOUT JAPANESE RAINY SEASON？', style={'textAlign': 'center', 'fontSize': '1.5vw', }),
    html.Div([
        html.H2(id = 'sub-title', style={'textAlign': 'center'}),
        html.H2('x-axis: begine date ; y-axis: end date, bubble-size: precipitation', style={'textAlign': 'center'}),


        dcc.RadioItems(id = 'area-select-dropdown',
        options = [{'label': i, 'value': i} for i in dftsuyu['area'].unique()],
        value = 'okinawa',
        style={'width': '50%', 'margin': '1% auto 1%', 'fontSize': '1.2vw'}),

        html.Div([
        dcc.RangeSlider(id = 'area-range-slider',
        min = dftsuyu['year'].min(), max = dftsuyu['year'].max(), value = [dftsuyu['year'].min(), dftsuyu['year'].max()],
        marks = {i: '{}'.format(i) for i in range(dftsuyu['year'].min(), dftsuyu['year'].max()) if i % 10 == 0},
        )], style={'textAlign': 'center', 'width': '60%', 'margin': '1% auto 3%'}
        ),
        dcc.Graph(id = 'area-chart', style={'width': '75%', 'margin': '0 auto 0'}),
        html.P('selection-area ; kyusyu-s: Kyusyu-South, kyusyu-n: Kyusyu-North, tohoku-n: Tohoku-North,tohoku-s: Tohoku-South', style={'width': '60%', 'margin': '1% auto', 'fontSize': '1vw'})
    ]),
    html.Div([
        html.H2(id = 'gantt-title', style={'width': '70%', 'textAlign': 'center', 'fontSize': '1.5vw', 'margin': '0 auto'}),
        dcc.Graph(id = 'area-gantt', style={'width': '75%', 'margin': '0 auto 0'}),
        html.H2(id = 'scatter-title', style={'width': '70%', 'textAlign': 'center', 'fontSize': '1.5vw', 'margin': '0 auto'}),
        dcc.Graph(id = 'scatter-rain',  style={'width': '75%', 'margin': '0 auto 0'}),
        html.Div([
        html.P('Please choose the year!'),
        dcc.Dropdown(id = 'polar-dropdown', options = [{'label': i, 'value': i} for i in dftsuyu['year'].unique()], value = 1951, style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),
        dcc.Graph(id = 'bar-polar',  style={'width': '75%', 'margin': '0 auto 0', 'display': 'inline-block'})
        ], style={'width': '75%', 'margin': '0 auto 0'}),
    ]),
    html.Div([
        dcc.Link('Back to Menu', href = '/', style={'fontSize': 40, })
    ], style = {'textAlign': 'center'})
])

@app.callback([Output('area-chart', 'figure'),
               Output('sub-title', 'children')],
            [Input('area-select-dropdown', 'value'),
            Input('area-range-slider', 'value')])
def area_chart_figure(areaName, slider_val):
    slider_num_small = slider_val[0]
    slider_num_big = slider_val[1]
    dfftsuyu = dftsuyu[dftsuyu['area'] == areaName]
    dfftsuyu = dfftsuyu[dfftsuyu['year'] >= slider_num_small]
    dfftsuyu = dfftsuyu[dfftsuyu['year'] <= slider_num_big]

    d = timedelta(10)

    return px.scatter(dfftsuyu, 
        x = 'g-enter', y = 'g-exit', size = 'p-amount', color = 'year', 
        marginal_x = 'violin', marginal_y = 'violin',
        range_x = [dftsuyu['g-enter'].min() - d , dftsuyu['g-enter'].max() + d],
        range_y = [dftsuyu['g-exit'].min() - d, dftsuyu['g-exit'].max() + d],
        height = 600),'Rainy season in {} from {} to {}'.format(areaName, slider_num_small, slider_num_big)

@app.callback([Output('area-gantt', 'figure'),
                Output('gantt-title', 'children'),
                Output('scatter-rain', 'figure'),
                Output('bar-polar', 'figure'),
                Output('scatter-title', 'children')],
                [Input('area-select-dropdown', 'value'),
                Input('area-range-slider', 'value'),
                Input('polar-dropdown', 'value')])
def gantt(areaName, slider_val, selected_year):
    slider_num_small = slider_val[0]
    slider_num_big = slider_val[1]
    df1tsuyu = dftsuyu[dftsuyu['area'] == areaName]
    df1tsuyu = df1tsuyu[df1tsuyu['year'] >= slider_num_small]
    df1tsuyu = df1tsuyu[df1tsuyu['year'] <= slider_num_big]    
    dfftsuyu = df2tsuyu[df2tsuyu['area'] == areaName]
    dfftsuyu = dfftsuyu[dfftsuyu['year'] >= slider_num_small]
    dfftsuyu = dfftsuyu[dfftsuyu['year'] <= slider_num_big]
    dff2suyu = dfftsuyu[dfftsuyu['variable'] == 'g-enter']
    d = timedelta(10)
    df_gannt = dftsuyu[dftsuyu['year'] == selected_year]

    gannt_data = list()

    for i in range(len(df_gannt)):
        gannt_data.append(dict(Task = df_gannt.iloc[i, 2], Start = df_gannt.iloc[i, 3], Finish = df_gannt.iloc[i, 4]))

    return px.box(dfftsuyu, x = 'year', y = 'date', 
    range_y = [dftsuyu['g-enter'].min() - d, dftsuyu['g-exit'].max() + d]), 'Historical tsuyu enter-data and exit-date Chart: {} '.format(areaName),{'data':[go.Scatter(x = df1tsuyu[df1tsuyu['year'] == i]['days'],y = dff2suyu[dff2suyu['year'] == i]['p-amount'], 
    mode = 'markers', marker = {'size': 15},text = str(i), name = str(i)) for i in df1tsuyu['year'].unique()],'layout':go.Layout(xaxis = {'title': 'days'}, yaxis = {'title': 'precipatation amount'}, height = 600, hovermode = 'closest')}, ff.create_gantt(gannt_data, title='Difference of Area; Year {}'.format(selected_year)), 'Scatter plot: {} xaxis: length of rainy season, yaxis: precipitational amount(average value: 100)'.format(areaName)

## Contents US YIELD CURVE

us_yield = html.Div([
    html.Div([
        html.H1('US Yield Data', style ={'textAlign': 'center'}),
        dcc.DatePickerRange(
            id = 'date-picker',
            minimum_nights = 5,
            clearable = True,
            start_date = datetime(2000, 1, 1),
            style = {'display': 'block'},
        ),
        html.Div([
            dcc.Graph(id = 'historical-left',
                    hoverData = {'points':[{'x': '2008-09-09'}]}),
            # html.H3('見たい範囲を上の日付ピッカー、もしくはマウスのドラッグで選択できます', style={'textAlign': 'center'}),
            ], style = {'width': '49%', 'display': 'inline-block'}),
        html.Div([
            html.H1(id='test'),
            dcc.Graph(id = 'yield-curve-right'),
            # html.H3('左の米国の主要金利のグラフでマウスホバーした地点のイールドカーブが表示できます。', style={'textAlign': 'center'}),
        ], style = {'width': '49%','display': 'inline-block'}),
    ], style = {'height': '1000', 'margin': '2%'}),
    html.Div([
        html.Div([
            html.H1('Major Yeild Spreads')
        ], style={'textAlign': 'center'}),
        html.Div([
            dcc.Dropdown(
                id = 'spread-dropdown',
                options = [{'label': i, 'value': i} for i in spreads.columns[1:]],
                value = 'tedspread'
            )
        ], style = {'width': '30%', 'margin': '2% auto 2%'}),
        html.Div([
            dcc.Graph(id='spreadGraph'),
        ], style = {'width': '60%', 'margin': '0 auto 0'}),
    ]),
    html.Div([
        dcc.Link('Back to Menu', href = '/', style={'fontSize': 40})
    ], style = {'textAlign': 'center'})
])

@app.callback(dash.dependencies.Output('historical-left', 'figure'),
            [dash.dependencies.Input('date-picker', 'start_date'),
            dash.dependencies.Input('date-picker', 'end_date')])
def makeYieldHist(start_date, end_date):
    histdf = yieldOnly[start_date: end_date]
    histdf = pd.melt(histdf, id_vars='date', value_vars=['ffrate', '3mT', '2yT', '5yT', '10yT', '30yT'])
    return {
        'data': [
            go.Scatter(
                x = histdf[histdf['variable'] == i]['date'],
                y = histdf[histdf['variable'] == i]['value'],
                name = i
            ) for i in histdf['variable'].unique()
        ],
        'layout':{
            'title': 'US Yeild'
        }
    }

@app.callback(dash.dependencies.Output('yield-curve-right', 'figure'),
            [dash.dependencies.Input('historical-left', 'hoverData')])
def makeYieldCurve(hoverData):
    
    try:
        selectedDate = hoverData['points'][0]['x']
    except:
        selectedDate = datetime(2008, 9, 9)
    
    selecteddf = yieldOnly[yieldOnly['date'] == selectedDate]
    return {
        'data':[
            go.Parcoords(
                line = dict(color='blue'),
                dimensions = list([
                    dict(range = [0, 7],
                        label = 'FF Rate', values = selecteddf['ffrate']
                    ),
                    dict(range = [0, 7],
                        label = '3M Treasury', values = selecteddf['3mT']
                    ),
                    dict(range = [0, 7],
                        label = '2Y Treasury', values = selecteddf['2yT']
                    ),
                    dict(range = [0, 7],
                        label = '5Y Treasury', values = selecteddf['5yT']
                    ),
                    dict(range = [0, 7],
                        label = '10Y Treasury', values = selecteddf['10yT']
                    ),
                    dict(range = [0, 7],
                        label = '30Y Treasury', values = selecteddf['30yT']
                    ),
                ])
            )
        ],
        'layout':{
            'title': 'Yield Curve Date: {}'.format(selectedDate)
        }
    }

@app.callback(dash.dependencies.Output('spreadGraph', 'figure'),
            [dash.dependencies.Input('spread-dropdown', 'value')])
def spreadGraph(selectedvalue):
    dfspread = spreads[['date', selectedvalue]]
    return {
        'data': [go.Scatter(
            x = dfspread['date'], 
            y = dfspread[selectedvalue],
            name = selectedvalue
        )
        ]
    }

japanese_gdp = html.Div([
    html.H1('日本の実質GDP成長率（前年比%）', style={'textAlign':'center'}),
    html.Div([dcc.Graph(figure={
        'data':[go.Bar(
            x = dfgdp['暦年'],
            y = dfgdp['GDP実質前年比（％）']
        )]
    })]),
    html.Div([
        dcc.Link('Back to Menu', href = '/', style={'fontSize': 40, })
    ], style = {'textAlign': 'center'})
])

# Page-Router
@app.callback(dash.dependencies.Output('page-content', 'children'),
            [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/tsuyu-dash':
        return tsuyu_page
    elif pathname == '/us-yield':
        return us_yield
    elif pathname == '/japanese-gdp':
        return japanese_gdp
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)