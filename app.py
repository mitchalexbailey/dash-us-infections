import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from us_infectious_toy import infections, show_year_map


external_stylesheets = ['us_infectious.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(children=[
    html.H1(children='US Infectious Disease'),

    dcc.Dropdown(
        id='year',
        options=[{'label': x, 'value': x} for x in ['2016', '2017', '2018']],
        value='2018'
    ),
    dcc.Dropdown(
        id='infection',
        options=[{'label': x, 'value': x} for x in infections],
        value='Measles, Total'
    ),
    dcc.Dropdown(
        id='count_type',
        options=[{'label': x, 'value': x} for x in ['Absolute', 'Relative to State Population']],
        value='Relative to State Population'
    ),

    dcc.Graph(
        id='us-infectious-graph',
    )
])

@app.callback(
    Output('us-infectious-graph', 'figure'),
    [Input('year', 'value'),
     Input('infection', 'value'),
     Input('count_type', 'value')])
def update_figure(year, infection, count_type):
    return show_year_map(year, infection, count_type)


if __name__ == '__main__':
    app.run_server(debug=True)
