import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Load exchange rate dataset
exchange_rates = pd.read_csv("C:/NT/Exchange_Rate_Report_2012.csv", parse_dates=['Date'], dayfirst=True)
# parse_dates will convert 'Date' column to datetime format, dayfirst=True considers dd-mm-yy format

# Set 'Date' as the index
exchange_rates.set_index('Date', inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(style={'backgroundColor': '#f0f0f0'}, children=[
    html.H1(style={'textAlign': 'center', 'margin': '20px 0px'}, children='Currency Exchange Rate Analysis Dashboard'),

    dcc.Dropdown(
        id='currency-dropdown',
        options=[
            {'label': currency, 'value': currency} for currency in exchange_rates.columns
        ],
        value=exchange_rates.columns[0],  # Set default currency pair
        style={'width': '50%', 'margin': '0 auto', 'textAlign': 'center'}
    ),

    dcc.Graph(id='exchange-rate-chart'),

    html.Div(id='peak-low-date-output', style={'textAlign': 'center', 'margin': '20px'})
])

# Define callback to update the chart based on user input
@app.callback(
    Output('exchange-rate-chart', 'figure'),
    Output('peak-low-date-output', 'children'),
    Input('currency-dropdown', 'value')
)
def update_chart(selected_currency):
    selected_currency_data = exchange_rates[selected_currency]

    # Normalize currency values against USD for comparison
    compared_values = exchange_rates['USD'] / selected_currency_data

    # Filter out NaN or unexpected values
    valid_values = compared_values.dropna()

    # Create figure with animation
    fig = go.Figure()
    frames = []

    for k in range(1, len(valid_values) + 1):
        subset = valid_values[:k]
        frames.append(go.Frame(data=[go.Scatter(x=subset.index, y=subset,
                                                mode='lines+markers',
                                                name=f'{selected_currency} against USD',
                                                line=dict(color='blue'),
                                                showlegend=False)],
                               name=f'frame{k}',
                               layout=dict(title=f'Exchange Rate between 1 USD and {selected_currency}',
                                           xaxis_title='Date',
                                           yaxis_title=f'Value of 1 {selected_currency} in USD')))

    # Create play button
    fig.update_layout(updatemenus=[dict(type='buttons', showactive=False,
                                        buttons=[dict(label='Play',
                                                      method='animate',
                                                      args=[None, {'frame': {'duration': 500, 'redraw': True},
                                                                   'fromcurrent': True}])])])

    fig.frames = frames

    # Find peak and low rates after handling unexpected values
    if not valid_values.empty and isinstance(valid_values.index[0], pd.Timestamp):
        peak_date = valid_values.idxmax().strftime('%Y-%m-%d')
        low_date = valid_values.idxmin().strftime('%Y-%m-%d')
    else:
        peak_date = 'No valid data'
        low_date = 'No valid data'

    return fig, html.Div([
        html.Label(f'Date of Peak Rate: {peak_date}'),
        html.Label(f'Date of Lowest Rate: {low_date}')
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
