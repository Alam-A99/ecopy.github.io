import dash
from dash import dcc, html
import yfinance as yf
import datetime
import plotly.graph_objects as go
import numpy as np

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__)

# Emiten Pilihan
symbols_list = ['TLKM.JK', 'BBRI.JK', 'SIDO.JK', 'UNVR.JK', 'TOWR.JK']

# Trendline
def get_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date, interval='1mo')
    data.reset_index(inplace=True)
    dates = data['Date']
    closing_prices = data['Close']
    volume = data['Volume']  

    # Konversi tanggal ke angka (untuk regresi linear)
    date_numbers = np.arange(len(dates))

    # Trend Line
    coefficients = np.polyfit(date_numbers, closing_prices, 1)  # Derajat 1 untuk garis lurus
    trendline = np.polyval(coefficients, date_numbers)

    # Persamaan Trend Line
    slope, intercept = coefficients
    equation = f"y = {slope:.2f}x + {intercept:.2f}"

    return dates, closing_prices, trendline, equation, volume

# Layout Dash
app.layout = html.Div([
    html.H1("Stock Prices with Trendline and Volume (Monthly Data)"),
    
    # Dropdown untuk memilih simbol emiten
    html.Div([
        html.Label("Select Stock Symbol:"),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': symbol, 'value': symbol} for symbol in symbols_list],
            value='TLKM.JK',  # Default value
            style={'width': '50%'}
        ),
    ], style={'margin-bottom': '20px'}),
    
    # Slider untuk memilih timeframe
    dcc.Slider(
        id='timeframe-slider',
        min=1,
        max=10,  # Rentang waktu hingga 10 tahun
        step=1,
        value=1,  # Default untuk 1 tahun
        marks={i: f'{i} Year' for i in range(1, 11)},
        updatemode='drag',
    ),
    
    # Grafik harga saham dan trendline
    dcc.Graph(id='stock-graph'),
])

# Callback untuk memperbarui grafik berdasarkan slider dan input simbol
@app.callback(
    dash.dependencies.Output('stock-graph', 'figure'),
    [dash.dependencies.Input('timeframe-slider', 'value'),
     dash.dependencies.Input('symbol-dropdown', 'value')]
)
def update_graph(timeframe, symbol):
    # Tentukan tanggal start dan end berdasarkan slider
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.today() - datetime.timedelta(days=timeframe * 365)).strftime('%Y-%m-%d')
    
    # Ambil data berdasarkan timeframe yang dipilih
    dates, closing_prices, trendline, equation, volume = get_data(symbol, start_date, end_date)

    # Plot dengan Plotly
    fig = go.Figure()

    # Tambahkan harga saham
    fig.add_trace(go.Scatter(x=dates, y=closing_prices, mode='lines', name='Close Price'))

    # Tambahkan garis tren
    fig.add_trace(go.Scatter(x=dates, y=trendline, mode='lines', name='Trendline', line=dict(dash='dot')))

    # Tambahkan volume sebagai bar chart dengan warna grey
    fig.add_trace(go.Bar(x=dates, y=volume, name='Volume', marker_color='rgba(169, 169, 169, 0.6)', yaxis='y2'))

    # Tambahkan persamaan garis tren sebagai teks dengan posisi di atas
    fig.add_annotation(
        x=dates[len(dates)//2], y=trendline[len(trendline)//2] + 10,  # Posisi di atas garis tren
        text=equation,
        showarrow=False,
        font=dict(size=14, color="black"),  
        bgcolor="white"  
    )

    # Format grafik
    fig.update_layout(
        title=f"{symbol} Stock Prices with Trendline and Volume ({timeframe} Year)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        showlegend=True
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
