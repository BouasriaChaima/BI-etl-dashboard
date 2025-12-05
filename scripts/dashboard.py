import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

OUTPUT_FOLDER = "data/star schema"
# loading data
print("Loading data from Excel files...")

dim_customer = pd.read_excel(f'{OUTPUT_FOLDER}/dim_customer.xlsx')
dim_employee = pd.read_excel(f'{OUTPUT_FOLDER}/dim_employee.xlsx')
dim_date = pd.read_excel(f'{OUTPUT_FOLDER}/dim_date.xlsx')
fact_orders = pd.read_excel(f'{OUTPUT_FOLDER}/fact_orders.xlsx')
# merging the data on left jointures
df = (fact_orders
      .merge(dim_customer, left_on='Customer_FK', right_on='Customer_SK', how='left', suffixes=('', '_c'))
      .merge(dim_employee, left_on='Employee_FK', right_on='Employee_SK', how='left', suffixes=('', '_e'))
      .merge(dim_date, left_on='Date_FK', right_on='Date_SK', how='left'))

print(f"Loaded {len(df)} orders\n")

total_orders = len(df)
delivered = df['Delivered'].sum()
not_delivered = df['NotDelivered'].sum()
delivery_rate = (delivered / total_orders * 100) if total_orders > 0 else 0
# dashboard
# initialization of a dash app with bootstrap styling
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    # main row, header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Business Inteligence",
                    className="text-center text-primary mb-4"),
            html.Hr()
        ])
    ]),

    # KPI Cards Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{total_orders:,}",
                            className="card-title text-info"),
                    html.P("Total Orders", className="card-text text-muted")
                ])
            ], className="shadow-sm mb-4")
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{delivered:,}",
                            className="card-title text-success"),
                    html.P("Delivered Orders", className="card-text text-muted")
                ])
            ], className="shadow-sm mb-4")
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{not_delivered:,}",
                            className="card-title text-danger"),
                    html.P("Not Delivered Orders",
                           className="card-text text-muted")
                ])
            ], className="shadow-sm mb-4")
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{delivery_rate:.1f}%",
                            className="card-title text-warning"),
                    html.P("Delivery Rate", className="card-text text-muted")
                ])
            ], className="shadow-sm mb-4")
        ], width=3),
    ], className="mb-4"),

    # Main Charts Row
    dbc.Row([
        dbc.Col([dcc.Graph(id='delivery-pie')], width=6),
        dbc.Col([dcc.Graph(id='source-bar')], width=6),
    ], className="mb-4"),

    # Detailed Analysis - Two Curves
    dbc.Row([
        dbc.Col([
            html.H4("📈 Detailed Orders Analysis by Date",
                    className="text-center mb-3"),
            dcc.Graph(id='detailed-curves')
        ], width=12),
    ], className="mb-4"),

], fluid=True, style={'backgroundColor': "#79a7d6", 'padding': '20px'})
# callbacks


@app.callback(
    [Output('delivery-pie', 'figure'),
     Output('source-bar', 'figure'),
     Output('detailed-curves', 'figure')],
    [Input('delivery-pie', 'id')]  # Dummy input to trigger callback
)
def update_charts(dummy):
    # Chart 1: Delivery Status Distribution (Circle)
    delivery_counts = pd.DataFrame({
        'Status': ['Delivered', 'Not Delivered'],
        'Count': [delivered, not_delivered]
    })
    fig1 = px.pie(delivery_counts, values='Count', names='Status',
                  title='<b>Delivery Status Distribution</b>',
                  color='Status',
                  color_discrete_map={
                      'Delivered': '#28a745', 'Not Delivered': '#dc3545'},
                  hole=0.4)
    fig1.update_traces(textposition='inside',
                       textinfo='percent+label', textfont_size=14)
    fig1.update_layout(showlegend=True, height=400, font=dict(size=12))

    # Chart 2: Orders by Source System
    source_data = df.groupby('Source').agg({
        'Delivered': 'sum',
        'NotDelivered': 'sum'
    }).reset_index()

    fig2 = go.Figure(data=[
        go.Bar(name='Delivered', x=source_data['Source'], y=source_data['Delivered'],
               marker_color='#28a745'),
        go.Bar(name='Not Delivered', x=source_data['Source'], y=source_data['NotDelivered'],
               marker_color='#dc3545')
    ])
    fig2.update_layout(
        title='<b>Orders by Source System</b>',
        barmode='stack',
        xaxis_title='Source',
        yaxis_title='Orders',
        height=400,
        showlegend=True,
        font=dict(size=12)
    )

    # Chart 3: Detailed Orders - Two Curves (Delivered vs Not Delivered)
    df_copy = df.copy()
    df_copy['Date'] = pd.to_datetime(df_copy['Date'])
    df_copy = df_copy.sort_values('Date')

    # Separate delivered and not delivered
    delivered_orders = df_copy[df_copy['Delivered'] == 1].copy()
    not_delivered_orders = df_copy[df_copy['NotDelivered'] == 1].copy()

    # Add cumulative count for Y-axis
    delivered_orders['CumulativeCount'] = range(1, len(delivered_orders) + 1)
    not_delivered_orders['CumulativeCount'] = range(
        1, len(not_delivered_orders) + 1)

    # Create figure
    fig3 = go.Figure()

    # Delivered curve (Green) - each point is one order
    fig3.add_trace(go.Scatter(
        x=delivered_orders['Date'],
        y=delivered_orders['CumulativeCount'],
        mode='lines+markers',
        name='Delivered Orders',
        line=dict(color='#28a745', width=2),
        marker=dict(size=8, color='#28a745'),
        customdata=delivered_orders[[
            'OrderID', 'CompanyName', 'EmployeeName']],
        hovertemplate=(
            '<b>Order ID:</b> %{customdata[0]}<br>' +
            '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
            '<b>Customer:</b> %{customdata[1]}<br>' +
            '<b>Employee:</b> %{customdata[2]}<br>' +
            '<extra></extra>'
        )
    ))

    # Not Delivered curve (Red) - each point is one order
    fig3.add_trace(go.Scatter(
        x=not_delivered_orders['Date'],
        y=not_delivered_orders['CumulativeCount'],
        mode='lines+markers',
        name='Not Delivered Orders',
        line=dict(color='#dc3545', width=2),
        marker=dict(size=8, color='#dc3545'),
        customdata=not_delivered_orders[[
            'OrderID', 'CompanyName', 'EmployeeName']],
        hovertemplate=(
            '<b>Order ID:</b> %{customdata[0]}<br>' +
            '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
            '<b>Customer:</b> %{customdata[1]}<br>' +
            '<b>Employee:</b> %{customdata[2]}<br>' +
            '<extra></extra>'
        )
    ))

    fig3.update_layout(
        title='<b>Orders Over Time - Each Point is One Order</b>',
        xaxis_title='Date',
        yaxis_title='Cumulative Orders',
        height=500,
        hovermode='closest',
        showlegend=True,
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            tickformat='%Y-%m-%d',
            tickangle=-45
        )
    )

    return fig1, fig2, fig3


if __name__ == '__main__':
    app.run(debug=True, port=8050)
