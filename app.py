import streamlit as st
import pandas as pd
import time
from datetime import datetime
from stock_data import StockDataManager
from utils import format_currency, format_percentage, format_market_cap
from stock_scraper import get_dynamic_stocks
from watchlist_manager import WatchlistManager
from portfolio_manager import PortfolioManager

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

if 'portfolio_manager' not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()

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

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = st.session_state.portfolio_manager.load_portfolio()

if 'show_barsi_filter' not in st.session_state:
    st.session_state.show_barsi_filter = False

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
        
        # Tabs para organizar funcionalidades
        tab1, tab2, tab3 = st.tabs(["📋 Seleção de Ações", "💼 Carteira de Investimentos", "🎯 Filtro Barsi"])
        
        with tab1:
            st.subheader("Selecionar Ações para Monitoramento")
            
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
        
        with tab2:
            st.subheader("💼 Gerenciar Carteira de Investimentos")
            
            # Adicionar posições na carteira
            col1, col2 = st.columns(2)
            with col1:
                portfolio_ticker = st.selectbox(
                    "Ação para adicionar na carteira:",
                    options=sorted(get_all_tickers()),
                    help="Selecione uma ação para adicionar à carteira"
                )
                
            with col2:
                quantity = st.number_input(
                    "Quantidade de ações:",
                    min_value=0,
                    value=0,
                    step=1,
                    help="0 para remover da carteira"
                )
            
            if st.button("💾 Salvar na Carteira", type="primary"):
                st.session_state.portfolio = st.session_state.portfolio_manager.add_position(
                    portfolio_ticker, quantity, st.session_state.portfolio
                )
                st.session_state.portfolio_manager.save_portfolio(st.session_state.portfolio)
                
                if quantity > 0:
                    st.success(f"Adicionado {quantity} ações de {portfolio_ticker} na carteira!")
                else:
                    st.success(f"{portfolio_ticker} removido da carteira!")
                st.rerun()
            
            # Mostrar carteira atual
            if st.session_state.portfolio:
                st.markdown("---")
                st.write("**Sua Carteira Atual:**")
                
                for ticker, qty in st.session_state.portfolio.items():
                    name = get_stock_name(ticker)
                    st.write(f"• **{ticker}** ({name}): {qty:,} ações")
                
                # Botão para limpar carteira
                if st.button("🗑️ Limpar Carteira", type="secondary"):
                    st.session_state.portfolio = {}
                    st.session_state.portfolio_manager.save_portfolio({})
                    st.success("Carteira limpa!")
                    st.rerun()
            else:
                st.info("Sua carteira está vazia. Adicione algumas ações acima!")
        
        with tab3:
            st.subheader("🎯 Filtro Metodologia Barsi")
            
            st.write("""
            **Critérios da Metodologia Luiz Barsi Filho:**
            - ✅ Empresa paga dividendos consistentemente
            - ✅ P/L entre 3 e 15 (preço justo)
            - ✅ ROE > 15% (rentabilidade do patrimônio)
            - ✅ Valor de mercado > R$ 1 bilhão (empresa consolidada)
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                barsi_filter = st.checkbox(
                    "Mostrar apenas ações que atendem critérios Barsi",
                    value=st.session_state.show_barsi_filter,
                    help="Filtra apenas empresas de qualidade segundo Barsi"
                )
                st.session_state.show_barsi_filter = barsi_filter
            
            with col2:
                if st.button("📊 Adicionar Ações Barsi à Watchlist"):
                    if 'stock_data' in st.session_state and not st.session_state.stock_data.empty:
                        # Encontrar ações que atendem aos critérios Barsi
                        barsi_stocks = st.session_state.portfolio_manager.filter_barsi_stocks(st.session_state.stock_data)
                        
                        if barsi_stocks:
                            # Adicionar à watchlist
                            current_watched = set(st.session_state.watched_stocks)
                            new_watched = current_watched.union(set(barsi_stocks))
                            st.session_state.watched_stocks = list(new_watched)
                            st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
                            
                            st.success(f"✅ {len(barsi_stocks)} ações que atendem critérios Barsi adicionadas à watchlist!")
                            st.rerun()
                        else:
                            st.warning("Nenhuma ação atende aos critérios Barsi no momento.")
                    else:
                        st.info("Carregue dados das ações primeiro para usar esta função!")
            
            st.markdown("---")
            st.write("**Filtros Adicionais:**")
            
            col1, col2 = st.columns(2)
            with col1:
                no_dividend_filter = st.checkbox(
                    "Mostrar apenas empresas SEM dividendos",
                    help="Identifica empresas que não pagam dividendos"
                )
            
            with col2:
                high_yield_filter = st.checkbox(
                    "Dividend Yield > 6%",
                    help="Empresas com alto rendimento de dividendos"
                )
            
            # Salvar filtros no session state
            st.session_state.no_dividend_filter = no_dividend_filter
            st.session_state.high_yield_filter = high_yield_filter

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
    elif st.session_state.auto_refresh:
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
        
        # Aplicar filtros se habilitados
        if st.session_state.show_barsi_filter:
            # Filtrar apenas ações que atendem aos critérios Barsi
            display_df = display_df[display_df['Critério Barsi'].str.contains('✅|⚠️', na=False)]
        
        if st.session_state.get('no_dividend_filter', False):
            # Mostrar apenas empresas que NÃO pagam dividendos
            display_df = display_df[display_df['Paga Dividendos'] == 'Não']
        
        if st.session_state.get('high_yield_filter', False):
            # Mostrar apenas empresas com DY > 6%
            display_df = display_df[
                (display_df['DY Atual (%)'] != 'N/A') & 
                (display_df['DY Atual (%)'] > 6)
            ]
        
        # Formatação dos dados para exibição
        format_columns = {
            'Preço Atual': lambda x: format_currency(x) if x != 'N/A' else 'N/A',
            'Variação (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'DY Atual (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'DY Médio 5a (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'Div/Ação (R$)': lambda x: format_currency(x) if x != 'N/A' else 'N/A',
            'P/L': lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A',
            'P/VP': lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A',
            'ROE (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'Dívida/PL': lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A',
            'Margem Líq. (%)': lambda x: format_percentage(x) if x != 'N/A' else 'N/A',
            'Valor de Mercado': lambda x: format_market_cap(x) if x != 'N/A' else 'N/A'
        }
        
        # Aplicar formatação
        formatted_df = display_df.copy()
        for col, formatter in format_columns.items():
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(formatter)
        
        # Informações de filtros ativos
        filter_info = []
        if st.session_state.show_barsi_filter:
            filter_info.append("🎯 Critérios Barsi")
        if st.session_state.get('no_dividend_filter', False):
            filter_info.append("🚫 Sem dividendos")
        if st.session_state.get('high_yield_filter', False):
            filter_info.append("📈 DY > 6%")
        
        if filter_info:
            st.info(f"Filtros ativos: {' | '.join(filter_info)}")
        
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
                "Div/Ação (R$)": st.column_config.TextColumn("Div/Ação", width="small"),
                "Paga Dividendos": st.column_config.TextColumn("Dividendos", width="small"),
                "P/L": st.column_config.TextColumn("P/L", width="small"),
                "P/VP": st.column_config.TextColumn("P/VP", width="small"),
                "ROE (%)": st.column_config.TextColumn("ROE", width="small"),
                "Dívida/PL": st.column_config.TextColumn("Dívi/PL", width="small"),
                "Margem Líq. (%)": st.column_config.TextColumn("Margem", width="small"),
                "Valor de Mercado": st.column_config.TextColumn("Val. Mercado", width="medium"),
                "Setor": st.column_config.TextColumn("Setor", width="medium"),
                "Critério Barsi": st.column_config.TextColumn("Barsi", width="medium")
            },
            hide_index=True
        )
        
        # Mostrar estatísticas da carteira se existir
        if st.session_state.portfolio:
            st.markdown("---")
            st.subheader("💼 Resumo da Carteira")
            
            # Calcular projeção de dividendos
            future_dividends = st.session_state.portfolio_manager.calculate_future_dividends(
                st.session_state.portfolio, 
                st.session_state.stock_data
            )
            
            # Calcular valor total da carteira
            portfolio_value = st.session_state.portfolio_manager.get_portfolio_value(
                st.session_state.portfolio,
                st.session_state.stock_data
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor da Carteira", format_currency(portfolio_value))
            
            with col2:
                total_future_dividends = sum(future_dividends.values())
                st.metric("Dividendos Anuais Projetados", format_currency(total_future_dividends))
            
            with col3:
                if portfolio_value > 0:
                    yield_projection = (total_future_dividends / portfolio_value) * 100
                    st.metric("Yield da Carteira", format_percentage(yield_projection))
                else:
                    st.metric("Yield da Carteira", "N/A")
            
            # Detalhes por ação na carteira
            if future_dividends:
                st.write("**Projeção de Dividendos por Ação:**")
                for ticker, dividend in future_dividends.items():
                    if dividend > 0:
                        quantity = st.session_state.portfolio[ticker]
                        name = get_stock_name(ticker)
                        st.write(f"• **{ticker}** ({name}): {format_currency(dividend)} ({quantity:,} ações)")
            else:
                st.info("Nenhuma ação na carteira paga dividendos no momento.")
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

# Auto-refresh logic - melhorado para evitar loops infinitos
if st.session_state.auto_refresh and st.session_state.watched_stocks:
    # Só refresh se há ações para monitorar e não houve atualização recente
    current_time = time.time()
    if not st.session_state.last_update or (current_time - st.session_state.last_update) >= 2:
        time.sleep(0.5)  # Pausa maior para estabilidade
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
