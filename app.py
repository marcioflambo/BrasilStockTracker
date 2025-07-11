import streamlit as st
import pandas as pd
import time
from datetime import datetime
from stock_data import StockDataManager
from utils import format_currency, format_percentage, format_market_cap
from stock_scraper import get_dynamic_stocks
from watchlist_manager import WatchlistManager

# Configuração da página
st.set_page_config(
    page_title="Monitor de Ações Brasileiras",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar o visual
st.markdown("""
<style>
    /* Melhorar header */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Customizar métricas */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    [data-testid="metric-container"] > div {
        color: white;
    }
    
    /* Melhorar sidebar */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Botões customizados */
    .stButton > button {
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Tabela de dados */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f1f3f4;
        border-radius: 8px;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do gerenciador de dados
if 'stock_manager' not in st.session_state:
    st.session_state.stock_manager = StockDataManager()

if 'watchlist_manager' not in st.session_state:
    st.session_state.watchlist_manager = WatchlistManager()

# Carregar lista dinâmica de ações
if 'dynamic_stocks' not in st.session_state:
    with st.spinner("Carregando lista de ações brasileiras..."):
        st.session_state.dynamic_stocks = get_dynamic_stocks()

# Carregar watchlist persistente
if 'watched_stocks' not in st.session_state:
    st.session_state.watched_stocks = st.session_state.watchlist_manager.load_watchlist()

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Funções auxiliares dinâmicas
def get_all_tickers():
    return list(st.session_state.dynamic_stocks.keys())

def get_sectors():
    sectors = set()
    for stock_info in st.session_state.dynamic_stocks.values():
        sectors.add(stock_info.get('sector', 'Diversos'))
    return sorted(list(sectors))

def get_tickers_by_sector(sector):
    tickers = []
    for ticker, info in st.session_state.dynamic_stocks.items():
        if info.get('sector') == sector:
            tickers.append(ticker)
    return tickers

def search_stocks(query):
    query = query.upper()
    results = []
    for ticker, info in st.session_state.dynamic_stocks.items():
        name = info.get('name', '')
        sector = info.get('sector', 'Diversos')
        
        if query in ticker.upper() or query in name.upper():
            results.append({
                'ticker': ticker,
                'name': name,
                'sector': sector
            })
    return results

def get_stock_name(ticker):
    return st.session_state.dynamic_stocks.get(ticker, {}).get('name', ticker.replace('.SA', ''))

def get_popular_stocks():
    # Retorna os primeiros 20 stocks da lista como populares
    return list(st.session_state.dynamic_stocks.keys())[:20]

# Header principal com informações do sistema
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.title("📈 Monitor de Ações Brasileiras")
with col2:
    total_stocks = len(get_all_tickers())
    st.metric("Ações Disponíveis", total_stocks)
with col3:
    st.metric("Monitoradas", len(st.session_state.watched_stocks))
with col4:
    # Botão de configurações
    if st.button("⚙️ Configurar", use_container_width=True):
        st.session_state.show_config = not st.session_state.get('show_config', False)

# Inicializar estado de configuração
if 'show_config' not in st.session_state:
    st.session_state.show_config = False

# Painel de configuração expansível
if st.session_state.show_config:
    with st.expander("⚙️ Configurações", expanded=True):
        # Controles principais
        col1, col2 = st.columns(2)
        
        with col1:
            # Auto-refresh
            auto_refresh = st.checkbox(
                "Atualização automática (2s)", 
                value=st.session_state.auto_refresh,
                help="Ativa a atualização automática dos dados"
            )
            st.session_state.auto_refresh = auto_refresh
            
            # Botão para atualizar lista de ações
            if st.button("🔄 Atualizar Base de Dados", help="Busca nova lista de ações"):
                with st.spinner("Atualizando..."):
                    st.session_state.dynamic_stocks = get_dynamic_stocks()
                    st.success("Base atualizada!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Atualizar Dados Agora", type="secondary"):
                st.session_state.last_update = None
                st.rerun()
            
            if st.button("❌ Limpar Seleções"):
                st.session_state.watched_stocks = []
                st.session_state.watchlist_manager.save_watchlist([])
                st.success("Seleções limpas!")
                st.rerun()
        
        st.markdown("---")
        
        # Seleção de ações simplificada
        st.subheader("Selecionar Ações")
        
        # Criar listas ordenadas
        all_tickers = sorted(get_all_tickers())
        current_watched = set(st.session_state.watched_stocks)
        
        # Filtros em linha
        col1, col2 = st.columns(2)
        with col1:
            search_filter = st.text_input(
                "Buscar ações:",
                placeholder="Ex: Itaú, PETR4, Bancos...",
                key="stock_filter"
            )
        
        with col2:
            sectors = get_sectors()
            selected_sector = st.selectbox(
                "Filtrar por setor:",
                options=["Todos"] + sectors,
                key="sector_filter"
            )
        
        # Filtrar lista
        if search_filter:
            filtered_results = search_stocks(search_filter)
            filtered_tickers = [r['ticker'] for r in filtered_results]
        elif selected_sector != "Todos":
            filtered_tickers = get_tickers_by_sector(selected_sector)
        else:
            filtered_tickers = all_tickers[:30]  # Limitar para performance
        
        # Botões de seleção rápida
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Selecionar Filtradas", use_container_width=True):
                new_selections = current_watched.union(set(filtered_tickers))
                st.session_state.watched_stocks = list(new_selections)
                st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
                st.success(f"{len(filtered_tickers)} ações adicionadas!")
                st.rerun()
        
        with col2:
            if st.button("❌ Desmarcar Filtradas", use_container_width=True):
                new_selections = current_watched - set(filtered_tickers)
                st.session_state.watched_stocks = list(new_selections)
                st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
                st.success(f"{len(filtered_tickers)} ações removidas!")
                st.rerun()
        
        # Lista de seleção compacta
        if filtered_tickers:
            st.write(f"**Ações ({len(filtered_tickers)}):**")
            
            with st.form("quick_selection"):
                # Organizar em colunas para economizar espaço
                cols = st.columns(3)
                new_watched_set = current_watched.copy()
                
                for i, ticker in enumerate(filtered_tickers[:30]):  # Limitar a 30
                    col_idx = i % 3
                    name = get_stock_name(ticker)
                    
                    with cols[col_idx]:
                        is_selected = st.checkbox(
                            f"{ticker}",
                            value=ticker in current_watched,
                            key=f"cb_{ticker}",
                            help=f"{name}"
                        )
                        
                        if is_selected:
                            new_watched_set.add(ticker)
                        else:
                            new_watched_set.discard(ticker)
                
                if st.form_submit_button("💾 Salvar Seleções", type="primary"):
                    st.session_state.watched_stocks = list(new_watched_set)
                    st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
                    st.success(f"Watchlist atualizada! {len(st.session_state.watched_stocks)} ações.")
                    st.rerun()

# Sidebar compacta
with st.sidebar:
    st.header("Status")
    
    # Status do auto-refresh
    if st.session_state.auto_refresh:
        st.success("🟢 Auto-refresh ativo")
    else:
        st.info("⏸️ Auto-refresh pausado")
    
    # Última atualização
    if st.session_state.last_update:
        update_time = datetime.fromtimestamp(st.session_state.last_update).strftime("%H:%M:%S")
        st.caption(f"Última atualização: {update_time}")
    
    st.markdown("---")
    
    # Lista compacta de ações selecionadas
    if st.session_state.watched_stocks:
        st.subheader(f"Monitoradas ({len(st.session_state.watched_stocks)})")
        
        # Mostrar apenas algumas com scroll
        for stock in st.session_state.watched_stocks[:8]:
            name = get_stock_name(stock)
            st.caption(f"• {stock}")
        
        if len(st.session_state.watched_stocks) > 8:
            st.caption(f"... e mais {len(st.session_state.watched_stocks) - 8} ações")
    else:
        st.warning("Nenhuma ação selecionada")
        st.caption("Use ⚙️ Configurar para selecionar ações")

# Área principal
if st.session_state.watched_stocks:
    # Placeholder para mostrar status de carregamento
    status_placeholder = st.empty()
    
    # Container para a tabela
    table_container = st.container()
    
    # Lógica de atualização
    should_update = False
    
    if st.session_state.last_update is None:
        should_update = True
    elif auto_refresh:
        time_since_update = time.time() - st.session_state.last_update
        if time_since_update >= 2:  # 2 segundos
            should_update = True
    
    if should_update:
        with status_placeholder:
            with st.spinner("📊 Carregando dados das ações..."):
                # Obter dados atualizados
                df = st.session_state.stock_manager.get_stock_data(st.session_state.watched_stocks)
                st.session_state.stock_data = df
                st.session_state.last_update = time.time()
    
    # Exibir dados se disponíveis
    if 'stock_data' in st.session_state and not st.session_state.stock_data.empty:
        status_placeholder.empty()
        
        # Tabela de dados com título clean
        st.subheader("💹 Dashboard de Ações")
        
        # Preparar dados para exibição
        display_df = st.session_state.stock_data.copy()
        
        # Formatação dos dados para exibição
        format_columns = {
            'Preço Atual': lambda x: format_currency(x) if x != 'N/A' else 'N/A',
            'Variação (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'DY Atual (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'DY Médio 5a (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'P/L': lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A',
            'P/VP': lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A',
            'Margem Líq. (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'Valor de Mercado': lambda x: format_market_cap(x) if x != 'N/A' else 'N/A'
        }
        
        # Aplicar formatação
        formatted_df = display_df.copy()
        for col, formatter in format_columns.items():
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(formatter)
        
        # Exibir tabela com configuração otimizada
        st.dataframe(
            formatted_df,
            use_container_width=True,
            height=500,
            column_config={
                "Ticker": st.column_config.TextColumn("Código", width="small"),
                "Nome": st.column_config.TextColumn("Empresa", width="medium"),
                "Preço Atual": st.column_config.TextColumn("Preço", width="small"),
                "Variação (%)": st.column_config.TextColumn("Var. %", width="small"),
                "DY Atual (%)": st.column_config.TextColumn("DY Atual", width="small"),
                "DY Médio 5a (%)": st.column_config.TextColumn("DY 5a", width="small"),
                "P/L": st.column_config.TextColumn("P/L", width="small"),
                "P/VP": st.column_config.TextColumn("P/VP", width="small"),
                "Margem Líq. (%)": st.column_config.TextColumn("Margem", width="small"),
                "Valor de Mercado": st.column_config.TextColumn("Valor Mercado", width="medium"),
                "Setor": st.column_config.TextColumn("Setor", width="medium")
            },
            hide_index=True
        )
    else:
        status_placeholder.error("❌ Erro ao carregar dados das ações")

else:
    # Tela inicial quando não há ações selecionadas
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🚀 **Bem-vindo ao Monitor de Ações!**")
        st.markdown("""
        **Para começar:**
        1. Clique em **⚙️ Configurar** acima
        2. Selecione as ações que deseja monitorar
        3. Volte aqui para ver os dados em tempo real!
        """)
        
        if st.button("⚙️ Configurar Ações", type="primary", use_container_width=True):
            st.session_state.show_config = True
            st.rerun()

# Auto-refresh logic
if st.session_state.auto_refresh:
    time.sleep(0.1)  # Pequena pausa para evitar refresh muito agressivo
    st.rerun()

# Rodapé simplificado
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 11px; padding: 20px;'>
        📊 Dados: Yahoo Finance | 🔄 Atualização: Tempo real | 🚀 Powered by Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )
