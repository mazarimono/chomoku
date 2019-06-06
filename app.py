import dash  
import dash_core_components as dcc  
import dash_html_components as html  
from dash.dependencies import Input, Output 
import plotly_express as px 
import plotly.graph_objs as go  
import plotly.figure_factory as ff 
import pandas as pd 
from datetime import timedelta

df = pd.read_csv('./src/all.csv', index_col = 0, parse_dates = ['enter', 'exit', 'g-enter', 'g-exit'])
df2 = pd.read_csv('./src/all2.csv', index_col = 0, parse_dates = ['enter', 'exit', 'date'])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('HOW ABOUT JAPANESE RAINY SEASON？', style={'textAlign': 'center', 'fontSize': '1.5vw'}),
    html.Div([
        html.H2(id = 'sub-title', style={'textAlign': 'center', 'fontSize': '1.5vw'}),
        html.H2('x-axis: begine date ; y-axis: end date, bubble-size: precipitation', style={'textAlign': 'center'}),


        dcc.RadioItems(id = 'area-select-dropdown',
        options = [{'label': i, 'value': i} for i in df['area'].unique()],
        value = 'okinawa',
        style={'width': '50%', 'margin': '1% auto 1%', 'fontSize': '1.2vw'}),

        html.Div([
        dcc.RangeSlider(id = 'area-range-slider',
        min = df['year'].min(), max = df['year'].max(), value = [df['year'].min(), df['year'].max()],
        marks = {i: '{}'.format(i) for i in range(df['year'].min(), df['year'].max()) if i % 10 == 0},
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
        dcc.Dropdown(id = 'polar-dropdown', options = [{'label': i, 'value': i} for i in df['year'].unique()], value = 1951, style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),
        dcc.Graph(id = 'bar-polar',  style={'width': '75%', 'margin': '0 auto 0', 'display': 'inline-block'})
        ], style={'width': '75%', 'margin': '0 auto 0'}),
    ]),

])

@app.callback([Output('area-chart', 'figure'),
               Output('sub-title', 'children')],
            [Input('area-select-dropdown', 'value'),
            Input('area-range-slider', 'value')])
def area_chart_figure(areaName, slider_val):
    slider_num_small = slider_val[0]
    slider_num_big = slider_val[1]
    dff = df[df['area'] == areaName]
    dff = dff[dff['year'] >= slider_num_small]
    dff = dff[dff['year'] <= slider_num_big]

    d = timedelta(10)

    return px.scatter(dff, 
        x = 'g-enter', y = 'g-exit', size = 'p-amount', color = 'year', 
        marginal_x = 'violin', marginal_y = 'violin',
        range_x = [df['g-enter'].min() - d , df['g-enter'].max() + d],
        range_y = [df['g-exit'].min() - d, df['g-exit'].max() + d],
        height = 800),'Rainy season in {} from {} to {}'.format(areaName, slider_num_small, slider_num_big)

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
    df1 = df[df['area'] == areaName]
    df1 = df1[df1['year'] >= slider_num_small]
    df1 = df1[df1['year'] <= slider_num_big]    
    dff = df2[df2['area'] == areaName]
    dff = dff[dff['year'] >= slider_num_small]
    dff = dff[dff['year'] <= slider_num_big]
    dff2 = dff[dff['variable'] == 'g-enter']
    d = timedelta(10)
    df_gannt = df[df['year'] == selected_year]

    gannt_data = list()

    for i in range(len(df_gannt)):
        gannt_data.append(dict(Task = df_gannt.iloc[i, 2], Start = df_gannt.iloc[i, 3], Finish = df_gannt.iloc[i, 4]))

    return px.box(dff, x = 'year', y = 'date', 
    range_y = [df['g-enter'].min() - d, df['g-exit'].max() + d]), 'Historical Chart: {} '.format(areaName),{'data':[go.Scatter(x = df1[df1['year'] == i]['days'],y = dff2[dff2['year'] == i]['p-amount'], 
    mode = 'markers', marker = {'size': 15},text = str(i), name = str(i)) for i in df1['year'].unique()],'layout':go.Layout(xaxis = {'title': 'days'}, yaxis = {'title': 'precipatation amount'}, height = 600, hovermode = 'closest')}, ff.create_gantt(gannt_data, title='Difference of Area; Year {}'.format(selected_year)), 'Scatter plot: {} xaxis: length of rainy season, yaxis: precipitational amount(average value: 100)'.format(areaName)


if __name__ == '__main__':
    app.run_server(debug=True)