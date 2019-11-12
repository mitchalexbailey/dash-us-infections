import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask

from us_infectious_toy import infections, show_year_map, get_diseases
from constants import columns_by_table_clean


fserver = Flask(__name__)
app = dash.Dash(__name__, server=fserver)
server = app.server
app.title = 'US Infectious Disease'
# app = dash.Dash(__name__)


app.layout = html.Div(
    className='container-fluid',
    children=[
    html.Div(
        className='row',
        children=[
        html.Div(
            className='col-md-12',
            children=[
            html.H1(
                className='title',
                children='US Infectious Disease'),
            html.Hr()])]),
    html.Div(
        className='row',
        children=[
        html.Div(
            className='col-md-4 col-md-4-pretty_container pretty_container',
            children=[
            html.H1(children='Select Tables'),
            html.P(children=[html.I(children='Disease tables selected impact the list of infectious diseases available below.')]),
            dcc.Dropdown(
                id='table_select',
                className="dash-input",
                multi=True,
                options=[{'label': x, 'value': x} for x in list(columns_by_table_clean.keys())],
                value=['Measles', 'Mumps']
            ),
            html.H1(children='Select Year'),
            dcc.Dropdown(
                id='year',
                className="dash-input",
                options=[{'label': x, 'value': x} for x in ['2016', '2017', '2018']],
                value='2018'
            ),
            html.H1(children='Select Disease'),
            html.P(children=[html.I(children='This list includes only infections available in the disease tables selected above.')]),
            dcc.Dropdown(
                id='infection',
                className="dash-input",
                options=[{'label': x, 'value': x} for x in infections],
                value='Measles, Total'
            ),
            html.H1(children='Select Count Type'),
            html.P(children=[html.I(children='Absolute number of cases or incidence (i.e. relative to population of state).')]),
            dcc.Dropdown(
                id='count_type',
                className="dash-input",
                options=[{'label': x, 'value': x} for x in ['Absolute', 'Relative to State Population']],
                value='Relative to State Population'
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            ]),
        html.Div(
            className='col-md-8 col-md-8-pretty_container pretty_container',
            children=[dcc.Graph(id='us-infectious-graph'),
                      html.Hr(),
                      html.H5(children=["You can zoom, pan and hover over map above to explore values. Produced using ",
                                        html.A(children="Plotly.", href='https://plot.ly/', target='_blank')]),
                      html.P(children=["Infection data from ",
                                        html.A(children="CDC.", href="https://wonder.cdc.gov/nndss/static", target="_blank"),
                                        html.Br(),
                                        "Population data from ",
                                        html.A(children="US Census Bureau.", href="https://data.census.gov", target="_blank")
                                        ]
                        )
                      ])
        ]),
    ])

@app.callback(
    Output('us-infectious-graph', 'figure'),
    [Input('year', 'value'),
     Input('infection', 'value'),
     Input('count_type', 'value'),
     Input('table_select', 'value')])
def update_figure(year, infection, count_type, table_select):
    fig = show_year_map(year=year,
        infection=infection,
        count_type=count_type,
        tables=table_select)
    return fig

@app.callback(
    Output('infection', 'options'),
    [Input('table_select', 'value')])
def update_disease_list(tables):
    cols = get_diseases(tables)
    return [{'label': x, 'value': x} for x in cols]


if __name__ == '__main__':
    app.run_server(debug=True)
