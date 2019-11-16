import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.graph_objects as go

from dash.dependencies import Input, Output
from flask import Flask
from plotly.subplots import make_subplots

df = pd.read_excel('./data/SIP Project.xlsx')

# convert to readable date format
df['Delivery Date'] = df['Delivery Date'].dt.strftime('%d/%m/%Y')
df['Due Date'] = df['Due Date'].dt.strftime('%d/%m/%Y')

# create another column to for amount for calculation
# but do not show it out in dashboard
df['Float Amount (MYR)'] = df['Amount (MYR)']

# convert Amount (MYR) to 0.2 floating point and string format
df['Amount (MYR)'] = df['Amount (MYR)'].map('{:,.2f}'.format)

# print the dataframe for analysis first
# print(df.head(5))
# print(df['Loading Port'].unique()) # ['GLNG' 'BLNG' 'MLNG']
# print(df['Delivery Port'].unique()) # ['RGTP' 'RGTSU']

# Create global chart template
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
)

server = Flask(__name__, static_folder='./assets')
app = dash.Dash(__name__, server=server)

colors = {
    'petronas_color': '#00a19c',
    'chart_background': '#D3D3D3',
    'text': '#ffffff'
}


def generate_table(dataframe, max_rows=5):
    return html.Div(
        [
            dt.DataTable(
                id='datatable-paging',
                columns=[{"name": i, "id": i} for i in dataframe.columns],
                data=dataframe.to_dict("records"),
                style_table={
                    'overflowX': 'scroll',
                    'maxHeight': '300',
                    'overflowY': 'scroll'
                },
                editable=False,
                style_cell={
                    'width': 'auto',
                    'height': 'auto',
                    'padding': '12px 15px',
                    'margin': '5%',
                    'textAlign': 'left',
                    'whiteSpace': 'no-wrap',
                    'fontFamily': '"Open Sans", "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif',
                    'fontSize': '16px'
                },
                style_header={
                    'fontWeight': 'bold',
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontFamily': '"Open Sans", "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif',
                    'fontSize': '16px',
                    'color': 'black'
                },
                page_current=0,
                page_size=max_rows,
            )
        ],
    )


def generate_graph_chart(df_filtered):
    return html.Div(
        dcc.Graph(
            id='graph chart',
            figure=go.Figure(data=[
                go.Scatter(x=df_filtered['Delivery Date'],
                       y=df_filtered['Float Amount (MYR)'],
                       marker=dict(color=colors['petronas_color']))],
                layout=go.Layout(
                    title='Graph Chart - Highest Amount Paid',
                    xaxis={"title": "Delivery Date"},
                    yaxis={"title": "Amount (MYR)"},
                )
            )
        )
    )


def generate_bar_chart(df_filtered):
    return html.Div(
        dcc.Graph(
            id='bar chart',
            figure=go.Figure(data=[
                go.Bar(x=df_filtered['Delivery Date'],
                       y=df_filtered['Float Amount (MYR)'],
                       marker=dict(color=colors['petronas_color']))],
                layout=go.Layout(
                    title='Bar Chart - Highest Amount Paid',
                    xaxis={"title": "Delivery Date"},
                    yaxis={"title": "Amount (MYR)"},
                )
            )
        )
    )


def generate_pie_chart(df_filtered):

    # find all the occurences for each unique value in delivery port
    delivery_port_occurences = []
    for value in df_filtered['Delivery Port'].unique():
        delivery_port_occurences.append(df_filtered[df_filtered['Delivery Port'] == value].shape[0])

    # find all the occurences for each unique value in loading port
    loading_port_occurences = []
    for value in df_filtered['Loading Port'].unique():
        loading_port_occurences.append(df_filtered[df_filtered['Loading Port'] == value].shape[0])

    delivery_labels = df['Delivery Port'].unique()
    loading_labels = df['Loading Port'].unique()

    figure = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
    figure.add_trace(go.Pie(
        labels=delivery_labels,
        values=delivery_port_occurences,
        name="Delivery Port",
        textinfo='label+percent'), 1, 1)
    figure.add_trace(go.Pie(
        labels=loading_labels,
        values=loading_port_occurences,
        name="Loading Port",
        textinfo='label+percent'), 1, 2)

    # Use `hole` to create a donut-like pie chart
    figure.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure.update_layout(title_text="Pie Chart - Comparison between Delivery Port and Loading Port")

    return html.Div(
        dcc.Graph(
            id='pie chart',
            figure=figure
        )
    )


app.layout = html.Div(children=[

    html.Link(rel='shortcut icon', href='./assets/favicon.ico'),

    # header
    html.Div([
        html.Img(
            src="https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Petronas_2013_logo.svg/1200px-Petronas_2013_logo.svg.png",
            className='one columns'
        ),
        html.Div(
            style={'textAlign': 'center', }, children=[
                html.H2('Energy and Gas Trading')
            ], className='twelve columns'
        ),
    ], id="header", className='row', style={'marginBottom': '15px'}),

    # main body
    html.Div(
        [
            # selection on left side
            html.Div(
                [
                    html.Div([
                        html.P('Delivery Port', className="control_label"),
                        dcc.Dropdown(
                            id='dropdown_delivery',
                            options=[
                                {'label': 'All', 'value': 'ALL'},
                                {'label': 'RGTP', 'value': 'RGTP'},
                                {'label': 'RGTSU', 'value': 'RGTSU'},
                            ],
                            value='ALL'
                        )
                    ]),

                    html.Div([
                        html.P('Loading Port', className="control_label"),
                        dcc.Dropdown(
                            id='dropdown_loading',
                            options=[
                                {'label': 'All', 'value': 'ALL'},
                                {'label': 'GLNG', 'value': 'GLNG'},
                                {'label': 'BLNG', 'value': 'BLNG'},
                                {'label': 'MLNG', 'value': 'MLNG'},
                            ],
                            value='ALL'
                        ),
                    ]),

                    html.P(
                        'Filter by paid status:',
                        className="control_label"
                    ),
                    dcc.RadioItems(
                        id='paid_status_selector',
                        options=[
                            {'label': 'All ', 'value': 'ALL'},
                            {'label': 'Paid', 'value': 'PAID'},
                            {'label': 'Unpaid ', 'value': 'UNPAID'}
                        ],
                        value='PAID',
                        labelStyle={'display': 'inline-block'},
                        className="dcc_control"
                    ),

                    html.P(
                        'Filter by unit:',
                        className="control_label"
                    ),
                    dcc.RadioItems(
                        id='unit_selector',
                        options=[
                            {'label': 'All ', 'value': 'ALL'},
                            {'label': 'MMBtu', 'value': 'MMBTU'},
                        ],
                        value='ALL',
                        labelStyle={'display': 'inline-block'},
                        className="dcc_control"
                    ),
                ],
                className="pretty_container four columns"
            ),
            # info card on right side
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        id="highest_amount_text",
                                        className="info_text"
                                    ),
                                    html.P("Highest Amount (MYR)")
                                ],
                                id="highest_amount",
                                className="pretty_container"
                            ),

                            html.Div(
                                [
                                    html.H6(
                                        id="delivery_port_text",
                                        className="info_text"
                                    ),
                                    html.P("Delivery Port"),
                                ],
                                id="delivery_port",
                                className="pretty_container"
                            ),

                            html.Div(
                                [
                                    html.H6(
                                        id="loading_port_text",
                                        className="info_text"
                                    ),
                                    html.P("Loading Port")
                                ],
                                id="loading_port",
                                className="pretty_container"
                            ),

                            html.Div(
                                [
                                    html.H6(
                                        id="delivery_date_text",
                                        className="info_text"
                                    ),
                                    html.P("Delivery Date")
                                ],
                                id="delivery_date",
                                className="pretty_container"
                            ),
                        ],
                        id="infoContainer",
                        className="row"
                    ),

                    html.Div(id='table', className="pretty_container"),
                 ],
                id="rightCol",
                className="eight columns"
            )
        ],
        className="row"
    ),
    # charts on bottom
    html.Div(
        [
            html.Div(id='graph_chart', className="pretty_container twelve columns"),
        ],
        className='row'
    ),

    html.Div(
        [
            html.Div(id='bar_chart', className="pretty_container twelve columns"),
        ],
        className='row'
    ),

    html.Div(
        [
            html.Div(id='pie_chart', className="pretty_container twelve columns"),
        ],
        className='row'
    ),

], # end html body
    id="mainContainer",
    style={
        "display": "flex",
        "flexDirection": "column"
    }
)


@app.callback(
    Output('pie_chart', 'children'),
    [Input('dropdown_delivery', 'value'), Input('dropdown_loading', 'value')]
)
def update_pie_chart(delivery_value, loading_value):
    # always copy the original data so in case you mess up you still can revert
    df_filtered = df.copy()
    if delivery_value == 'ALL' and loading_value == 'ALL':
        return generate_pie_chart(df_filtered)
    else:
        if delivery_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Delivery Port"] == delivery_value]
        if loading_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Loading Port"] == loading_value]
        return generate_pie_chart(df_filtered)


@app.callback(
    Output('table', 'children'),
    [Input('dropdown_delivery', 'value'), Input('dropdown_loading', 'value')]
)
def update_table(delivery_value, loading_value):
    df_filtered = df.drop('Float Amount (MYR)', axis=1)
    if delivery_value == 'ALL' and loading_value == 'ALL':
        return generate_table(df_filtered)
    else:
        if delivery_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Delivery Port"] == delivery_value]
        if loading_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Loading Port"] == loading_value]
        return generate_table(df_filtered)


@app.callback(
    Output('bar_chart', 'children'),
    [Input('dropdown_delivery', 'value'),  Input('dropdown_loading', 'value')]
)
def update_bar_chart(delivery_value, loading_value):
    df_filtered = df.copy()
    if delivery_value == 'ALL' and loading_value == 'ALL':
        return generate_bar_chart(df_filtered)
    else:
        if delivery_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Delivery Port"] == delivery_value]
        if loading_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Loading Port"] == loading_value]
        return generate_bar_chart(df_filtered)


@app.callback(
    Output('graph_chart', 'children'),
    [Input('dropdown_delivery', 'value'),  Input('dropdown_loading', 'value')]
)
def update_graph_chart(delivery_value, loading_value):
    df_filtered = df.copy()
    if delivery_value == 'ALL' and loading_value == 'ALL':
        return generate_graph_chart(df_filtered)
    else:
        if delivery_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Delivery Port"] == delivery_value]
        if loading_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Loading Port"] == loading_value]
        return generate_graph_chart(df_filtered)


@app.callback([Output('highest_amount_text', 'children'), Output('delivery_port_text', 'children'),
               Output('loading_port_text', 'children'), Output('delivery_date_text', 'children')],
              [Input('dropdown_delivery', 'value'),  Input('dropdown_loading', 'value')])
def update_info_card(delivery_value, loading_value,):
    # if select all, return original data highest value by using Float Amount (MYR) column
    if delivery_value == 'ALL' and loading_value == 'ALL':
        df_filtered = df.loc[df['Float Amount (MYR)'].idxmax()]

        # extract the values from the highest row
        highest_amount = df_filtered['Amount (MYR)']
        delivery_port = df_filtered['Delivery Port']
        loading_port = df_filtered['Loading Port']
        delivery_date = df_filtered['Delivery Date']
        return highest_amount, loading_port, delivery_port , delivery_date
    else:
        # create blank value in case it could not find match delivery and loading port
        highest_amount = ''
        delivery_port = ''
        loading_port = ''
        delivery_date = ''

        df_filtered = df.copy()

        if delivery_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Delivery Port"] == delivery_value]
        if loading_value != 'ALL':
            df_filtered = df_filtered.loc[df_filtered["Loading Port"] == loading_value]

        # if dataframe is not empty, we proceed to extract the values from the highest row
        if not df_filtered.empty:
            df_filtered = df_filtered.loc[df_filtered['Float Amount (MYR)'].idxmax()]
            highest_amount = df_filtered['Amount (MYR)']
            delivery_port = df_filtered['Delivery Port']
            loading_port = df_filtered['Loading Port']
            delivery_date = df_filtered['Delivery Date']
        return highest_amount, loading_port, delivery_port, delivery_date


if __name__ == '__main__':
    # Debug/Development
    # app.run_server(debug=True)
    # Production
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('', 5000), server)
    http_server.serve_forever()