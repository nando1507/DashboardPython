import dash
import pyodbc
from sqlalchemy import create_engine

from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State
from dash_bootstrap_components._components.Container import Container
from dash.exceptions import PreventUpdate

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash_bootstrap_templates import load_figure_template

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

counties["features"][0]

colorscales = px.colors.named_colorscales()
# load_figure_template("MATERIA")

app = dash.Dash(external_stylesheets=[dbc.themes.MATERIA])
server = app.server

# mapa de calor python

# https://www.flai.com.br/jonatas/4-bibliotecas-para-mapas-no-python-altair-bokehfolium-e-plotly/

# https://dash.plotly.com/tutorial
# https://dash.plotly.com/basic-callbacks
# graficos
# https://dash.plotly.com/interactive-graphing
#
# https://stackoverflow.com/questions/55946082/dash-output-with-multiple-inputs
# df = pd.read_csv("https://media.githubusercontent.com/media/microsoft/Bing-COVID-19-Data/master/data/Bing-COVID19-Data.csv", delimiter=",", encoding="utf-8")
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

server = 'DESKTOP-UVIN3NU'
database = 'Particular'
username = 'sa'
password = '*casa123'

# Criação da string de conexão
# connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
#conn = pyodbc.connect(connection_string)
connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(connection_string)

# cnxn = pyodbc.connect('DRIVER=SQLNCLI11;Data Source=DESKTOP-UVIN3NU;Initial Catalog=Particular;User ID=sa;Password=*casa123;TrustServerCertificate=True')
query = "exec SP_ScriptCovid"

df = pd.read_sql(query, engine)

    
def remove_repetidos(lista):
    l = []
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
    return l

dfAnos = df['Updated'].unique().strftime("%Y")
dfAnos = remove_repetidos(dfAnos)
# dfAnos

dfMeses = df['Updated'].unique().strftime("%m")
dfMeses = remove_repetidos(dfMeses)
# dfMeses

df2 = df.describe()
titulo = "Dash Covid"

app.title = titulo

# =========  Layout  =========== #
app.layout = html.Div(
    children=[
        html.Hr(),
        html.H1(titulo),
        dbc.Row(
            dbc.Col(
                html.Div("Filtros Grafico")
                )
            ),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                dbc.RadioItems(options=[
                        {"label": "Confirmados", "value": "ConfirmedChange"},
                        {"label": "Mortes", "value": "DeathsChange"},
                        {"label": "Recuperados", "value": "RecoveredChange"}
                    ]
                    # 'pop', 'lifeExp', 'gdpPercap']
                    , value='ConfirmedChange', id='itens'),
            ),
            dbc.Col(
                dbc.RadioItems(options=[
                    {"label": "Soma", "value": 'sum'}, 
                    {"label": "Média", "value": 'avg'}
                ], value='sum', id='inputSoma'),
            ),         
        ]
        ),
        dbc.Row(
            [
                dash_table.DataTable(data=df.to_dict('records'), page_size=15 ),
            ]),
        html.Hr(),
        # dcc.Graph(figure=px.histogram(df, x='continent', y='pop', histfunc='sum'))
        dbc.Row(
            [
                dcc.Graph(figure={}, id='controls-and-graph')
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dcc.Graph(figure={}, id='controls-and-graph-linha')
            ]
        ),
        dbc.Row(
            [
                dash_table.DataTable(data=df2.to_dict('records')),
            ]
        ),
        dbc.Row([
            html.Hr(),
        ]
        ),
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    df["AdminRegion1"].unique(),
                    value="São Paulo",
                    id='demo-dropdown'),
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='dropdown-colors', 
                    options=colorscales,
                    value='earth'
                ),
            )
        ]
        ),
        dbc.Row(
            [
                #estado x Confirmado
                dbc.Col(
                    dcc.Graph(figure={}, id='controls-linha-data')
                ),
                #estado x Mortes
                dbc.Col(
                    dcc.Graph(figure={}, id='graph-linha-data')
                ),
                #estado x Recuperados
                dbc.Col(
                    dcc.Graph(figure={}, id='graph-linha-data-recovered')
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(figure={}, id='data-mapa')
                    ] 
                ),
            ],
            justify="center", 
            align="center"
        ),
        html.Div(
            dbc.Row(
                [                    
                    dbc.Col(
                        dcc.Slider(
                            int(min(dfAnos)),
                            int(max(dfAnos)),
                            step=1,
                            id='crossfilter-Updated--slider-Anual',
                            value=int(max(dfAnos)),
                            marks={str(up): str(up) for up in dfAnos}
                        ),
                        style={'width': '49%', 'padding': '0px 20px 20px 20px'}
                    ),
                    dbc.Col(
                        dcc.Slider(
                            int(min(dfMeses)),
                            int(max(dfMeses)),
                            step=1,
                            id='crossfilter-Updated--slider-mensal',
                            value=int(max(dfMeses)),
                            marks={str(up): str(up) for up in dfMeses}
                        ),
                        style={'width': '49%', 'padding': '0px 20px 20px 20px'}
                    ),                    
                ]
            ),            
        )
    ]
)



@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='itens', component_property='value'),
    Input(component_id='inputSoma', component_property='value')
    #,Input(component_id='demo-dropdown', component_property='value')
)
def update_graph(col_chosen, calc_Chosen):
    fig = px.histogram(df, x='Updated', y=col_chosen, histfunc=calc_Chosen, title= calc_Chosen + " X " + col_chosen)    
                    #.filter(like=dropdownMenu, axis="Updated")*/
    return fig


@app.callback(
    Output(component_id='controls-and-graph-linha', component_property='figure'),
    Input(component_id='itens', component_property='value'),
    Input(component_id='inputSoma', component_property='value')
    #,Input(component_id='demo-dropdown', component_property='value')
)
def update_graph_linha(col_chosen, calc_Chosen):
    # fig = px.histogram(df, x='Updated', y=col_chosen, histfunc=calc_Chosen, title= calc_Chosen + " X " + col_chosen)
    fig = px.line(df, x='Updated', y=col_chosen, title= calc_Chosen + " X " + col_chosen)
    #.filter(like=dropdownMenu, axis="Updated")
    return fig

#estado x Confirmado
@app.callback(
    Output(component_id='controls-linha-data', component_property='figure'),
    Input(component_id='demo-dropdown', component_property='value'),
    Input(component_id='dropdown-colors', component_property='value')
)
def update_graph_linha(demo_dropdown, cores):
    # fig = px.histogram(df, x='Updated', y=col_chosen, histfunc=calc_Chosen, title= calc_Chosen + " X " + col_chosen)
    fig = px.scatter(df[df['AdminRegion1']==demo_dropdown],  
                    x='Updated', 
                    y="ConfirmedChange", 
                    color="ConfirmedChange",
                    color_continuous_scale=cores,
                    title= demo_dropdown + " X ConfirmedChange")
    #.filter(like=dropdownMenu, axis="Updated")
    return fig

#estado x Mortes
@app.callback(
    Output(component_id='graph-linha-data', component_property='figure'),    
    Input(component_id='demo-dropdown', component_property='value'),
    Input(component_id='dropdown-colors', component_property='value')
)
def update_graph_linha(demo_dropdown, cores):    
    fig = px.scatter(df[df['AdminRegion1']==demo_dropdown], 
                    x='Updated', 
                    y="DeathsChange", 
                    color="DeathsChange",
                    color_continuous_scale=cores,
                    title= demo_dropdown + " X DeathsChange")
    #.filter(like=dropdownMenu, axis="Updated")
    return fig

#estado x Recuperados
@app.callback(
    Output(component_id='graph-linha-data-recovered', component_property='figure'),
    Input(component_id='demo-dropdown', component_property='value'),
    Input(component_id='dropdown-colors', component_property='value')
)
def update_graph_linha(demo_dropdown, cores):    
    fig = px.scatter(df[df['AdminRegion1']==demo_dropdown], 
                    x='Updated', 
                    y="RecoveredChange", 
                    color="RecoveredChange",
                    color_continuous_scale=cores,
                    title= demo_dropdown + " X RecoveredChange")
    #.filter(like=dropdownMenu, axis="Updated")
    return fig


@app.callback(
    Output(component_id='data-mapa', component_property='figure'),
    Input(component_id='itens', component_property='value'),
    # Input(component_id='inputSoma', component_property='value'),
    Input(component_id='dropdown-colors', component_property='value')
)
def plotMap(col_chosen, cores ):
    fig = px.scatter_mapbox(
            df,             
            lat="Latitude", 
            lon="Longitude", 
            hover_name="AdminRegion1", 
            size = col_chosen,
            # hover_data=["Country_Region", "AdminRegion1","ConfirmedChange","DeathsChange","RecoveredChange" ],
            center = dict(lat=-15.7809896469116, lon=-47.7969589233398),
            color_continuous_scale= px.colors.cyclical.IceFire,
            zoom=3, 
            height=720)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(autosize=True, width=1500, height=500)
    return fig
    


# =========  Run server  =========== #
if __name__ == "__main__":
    app.run_server(debug=True)