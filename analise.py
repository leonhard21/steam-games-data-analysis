import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ==========================================
# 1. PREPARAÇÃO DOS DADOS
# ==========================================
try:
    df = pd.read_csv('steamcharts.csv')
except FileNotFoundError:
    print("ERRO: steamcharts.csv não encontrado.")
    exit()

df['month_dt'] = pd.to_datetime(df['month'], format='%b-%y', errors='coerce')
recent_date = df['month_dt'].max()

# Mapeamento de modelo de negócio (Free/Paid)
game_model = {
    'Counter-Strike 2': 'Free', 'PUBG: BATTLEGROUNDS': 'Free',
    'Rust': 'Paid', 'HELLDIVERS™ 2': 'Paid', 'Stardew Valley': 'Paid',
    'Grand Theft Auto V Legacy': 'Paid', "Tom Clancy's Rainbow Six® Siege X": 'Paid',
    'Hollow Knight': 'Paid', 'Team Fortress 2': 'Free', 'Dota 2': 'Free',
    'War Thunder': 'Free', 'Apex Legends': 'Free', 'Counter-Strike': 'Free'
}

# Aplicar modelo a todos os jogos
df['Model'] = df['name'].apply(lambda x: game_model.get(x, 'Paid'))

# ==========================================
# 2. INICIALIZAÇÃO DO DASH APP
# ==========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Steam Market Intelligence"

# Obter listas únicas para os filtros
unique_games = sorted(df['name'].unique())
unique_models = sorted(df['Model'].unique())
date_range = [df['month_dt'].min(), df['month_dt'].max()]

# ==========================================
# 3. LAYOUT DA INTERFACE
# ==========================================
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("STEAM MARKET INTELLIGENCE", 
                   style={'color': '#E0E0E0', 'marginBottom': '20px', 'fontSize': '28px'}),
        ], width=12)
    ]),
    
    # Filtros
    dbc.Row([
        dbc.Col([
            html.Label("Filtrar por Data:", style={'color': '#B0B0B0', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.DatePickerRange(
                id='date-filter',
                start_date=df['month_dt'].min(),
                end_date=df['month_dt'].max(),
                display_format='MMM YYYY',
                style={'backgroundColor': '#1E1E1E', 'color': '#E0E0E0'}
            ),
        ], width=4, style={'marginBottom': '20px'}),
        
        dbc.Col([
            html.Label("Filtrar por Modelo:", style={'color': '#B0B0B0', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='model-filter',
                options=[{'label': 'Todos', 'value': 'All'}] + [{'label': m, 'value': m} for m in unique_models],
                value='All',
                clearable=False,
                style={'backgroundColor': '#1E1E1E', 'color': '#E0E0E0'}
            ),
        ], width=4, style={'marginBottom': '20px'}),
        
        dbc.Col([
            html.Label("Filtrar por Jogo:", style={'color': '#B0B0B0', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='game-filter',
                options=[{'label': 'Todos', 'value': 'All'}] + [{'label': g, 'value': g} for g in unique_games],
                value='All',
                clearable=False,
                searchable=True,
                style={'backgroundColor': '#1E1E1E', 'color': '#E0E0E0'}
            ),
        ], width=4, style={'marginBottom': '20px'}),
    ]),
    
    # Gráficos
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line-chart')
        ], width=12, style={'marginBottom': '30px'}),
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart')
        ], width=8, style={'marginBottom': '30px'}),
        dbc.Col([
            dcc.Graph(id='pie-chart')
        ], width=4, style={'marginBottom': '30px'}),
    ]),
    
], fluid=True, style={'backgroundColor': '#121212', 'padding': '20px', 'minHeight': '100vh'})

# ==========================================
# 4. CALLBACKS PARA FILTROS E GRÁFICOS
# ==========================================

@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('model-filter', 'value'),
     Input('game-filter', 'value')]
)
def update_charts(start_date, end_date, model_filter, game_filter):
    # Filtrar dados
    filtered_df = df[
        (df['month_dt'] >= pd.to_datetime(start_date)) & 
        (df['month_dt'] <= pd.to_datetime(end_date))
    ].copy()
    
    if model_filter != 'All':
        filtered_df = filtered_df[filtered_df['Model'] == model_filter]
    
    if game_filter != 'All':
        filtered_df = filtered_df[filtered_df['name'] == game_filter]
    
    # ==========================================
    # GRÁFICO 1: LINHAS (Dinâmica de Retenção)
    # ==========================================
    fig_line = go.Figure()
    
    # Obter jogos únicos no período filtrado
    games_in_period = filtered_df['name'].unique()
    
    # Cores para os jogos
    colors = {
        0: 'rgba(0, 229, 255, 1)',   # Cyan
        1: 'rgba(255, 64, 129, 1)',   # Pink
        2: 'rgba(0, 230, 118, 1)'     # Green
    }
    fill_colors = {
        0: 'rgba(0, 229, 255, 0.1)',
        1: 'rgba(255, 64, 129, 0.1)',
        2: 'rgba(0, 230, 118, 0.1)'
    }
    
    for i, game in enumerate(games_in_period[:20]):  # Limitar a 20 jogos para performance
        data = filtered_df[filtered_df['name'] == game].sort_values('month_dt')
        if len(data) > 0:
            if i < 3:
                fig_line.add_trace(go.Scatter(
                    x=data['month_dt'],
                    y=data['avg_players'],
                    name=game,
                    mode='lines',
                    line=dict(color=colors[i], width=3, shape='spline'),
                    fill='tozeroy',
                    fillcolor=fill_colors[i],
                    hovertemplate=f'<b>{game}</b><br>Data: %{{x|%b %Y}}<br>Jogadores: %{{y:,.0f}}<extra></extra>',
                    showlegend=True
                ))
            else:
                fig_line.add_trace(go.Scatter(
                    x=data['month_dt'],
                    y=data['avg_players'],
                    name=game,
                    mode='lines',
                    line=dict(color='rgba(207, 216, 220, 0.7)', width=2, shape='spline'),
                    hovertemplate=f'<b>{game}</b><br>Data: %{{x|%b %Y}}<br>Jogadores: %{{y:,.0f}}<extra></extra>',
                    showlegend=True
                ))
    
    fig_line.update_layout(
        template='plotly_dark',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        title=dict(
            text="DINÂMICA DE RETENÇÃO<br><span style='font-size:14px; color:#9E9E9E'>Média de jogadores simultâneos</span>",
            x=0.02,
            xanchor='left',
            font=dict(size=18, color="#E0E0E0")
        ),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(t=80, b=100, l=80, r=80),
        height=500,
        font=dict(family="Arial, sans-serif", size=12, color="#B0B0B0"),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)')
    )
    
    # ==========================================
    # GRÁFICO 2: BARRAS (Liderança de Mercado) - TODOS OS DADOS
    # ==========================================
    # Usar a data mais recente no período filtrado
    latest_date_in_filter = filtered_df['month_dt'].max()
    current_stats = filtered_df[filtered_df['month_dt'] == latest_date_in_filter].copy()
    
    # Agrupar por jogo e pegar o maior valor de peak_players
    current_stats = current_stats.groupby('name').agg({
        'peak_players': 'max',
        'avg_players': 'max',
        'Model': 'first'
    }).reset_index()
    
    # Ordenar por peak_players
    current_stats = current_stats.sort_values(by='peak_players', ascending=True)
    
    # Limitar a 50 jogos para melhor visualização (mas mostrar todos se menos que 50)
    if len(current_stats) > 50:
        current_stats = current_stats.tail(50)
    
    bar_colors = ['#00B8D4' if m == 'Free' else '#7C4DFF' for m in current_stats['Model']]
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=current_stats['name'],
        x=current_stats['peak_players'],
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=current_stats['peak_players'],
        textposition='outside',
        texttemplate='%{text:,.0f}',
        hovertemplate='<b>%{y}</b><br>Pico: %{x:,.0f}<br>Média: %{customdata:,.0f}<extra></extra>',
        customdata=current_stats['avg_players']
    ))
    
    fig_bar.update_layout(
        template='plotly_dark',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        title=dict(
            text="LIDERANÇA DE MERCADO<br><span style='font-size:14px; color:#9E9E9E'>Ranking por pico de jogadores</span>",
            x=0.02,
            xanchor='left',
            font=dict(size=18, color="#E0E0E0")
        ),
        margin=dict(t=80, b=20, l=200, r=100),  # Aumentar margem esquerda para nomes
        height=800,  # Aumentar altura do gráfico
        font=dict(family="Arial, sans-serif", size=11, color="#B0B0B0"),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=10, color="#E0E0E0")
        ),
        showlegend=False
    )
    
    # Adicionar legenda do modelo
    fig_bar.add_trace(go.Scatter(
        x=[None], y=[None], 
        mode='markers', 
        marker=dict(size=10, color='#00B8D4'), 
        name='Free-to-Play', 
        showlegend=True
    ))
    fig_bar.add_trace(go.Scatter(
        x=[None], y=[None], 
        mode='markers', 
        marker=dict(size=10, color='#7C4DFF'), 
        name='Pago', 
        showlegend=True
    ))
    
    # ==========================================
    # GRÁFICO 3: PIZZA (Distribuição)
    # ==========================================
    # Verificar se há dados
    if len(current_stats) == 0:
        # Gráfico vazio
        fig_pie = go.Figure()
        fig_pie.add_annotation(
            text="Nenhum dado disponível para o período selecionado",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#9E9E9E")
        )
        title_pie = "Distribuição<br><span style='font-size:12px; color:#9E9E9E'>Sem dados</span>"
    else:
        # Agrupar por modelo ou por jogo dependendo do filtro
        if game_filter == 'All' and len(current_stats) > 1:
            # Distribuição por modelo
            pie_data = current_stats.groupby('Model').agg({
                'peak_players': 'sum'
            }).reset_index()
            if len(pie_data) > 0:
                labels = pie_data['Model']
                values = pie_data['peak_players']
                title_pie = "Distribuição por Modelo<br><span style='font-size:12px; color:#9E9E9E'>Pico de jogadores</span>"
            else:
                labels = []
                values = []
                title_pie = "Distribuição<br><span style='font-size:12px; color:#9E9E9E'>Sem dados</span>"
        else:
            # Se filtrado por jogo ou poucos jogos, mostrar top jogos
            top_games_pie = current_stats.nlargest(min(10, len(current_stats)), 'peak_players')
            labels = top_games_pie['name']
            values = top_games_pie['peak_players']
            title_pie = f"Top {len(labels)} Jogos<br><span style='font-size:12px; color:#9E9E9E'>Pico de jogadores</span>"
        
        if len(labels) > 0 and len(values) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                textinfo='label+percent',
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>Pico: %{value:,.0f}<br>Percentual: %{percent}<extra></extra>',
                marker=dict(
                    colors=['#00B8D4', '#7C4DFF', '#00E676', '#FF4081', '#FFC107', '#9C27B0', '#FF5722', '#2196F3', '#4CAF50', '#FF9800'],
                    line=dict(color='#121212', width=2)
                )
            )])
        else:
            fig_pie = go.Figure()
            fig_pie.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="#9E9E9E")
            )
    
    fig_pie.update_layout(
        template='plotly_dark',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        title=dict(
            text=title_pie,
            x=0.5,
            xanchor='center',
            font=dict(size=16, color="#E0E0E0")
        ),
        margin=dict(t=80, b=20, l=20, r=20),
        height=500,
        font=dict(family="Arial, sans-serif", size=11, color="#B0B0B0"),
        showlegend=False
    )
    
    return fig_line, fig_bar, fig_pie

# ==========================================
# 5. EXECUTAR APLICAÇÃO
# ==========================================
if __name__ == '__main__':
    print("Iniciando aplicação Dash...")
    print("Acesse http://127.0.0.1:8050 no seu navegador")
    app.run(debug=True, port=8050)
