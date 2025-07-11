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

# Título principal
st.title("📈 Monitor de Ações Brasileiras")
st.markdown("---")

# Sidebar para controles
with st.sidebar:
    st.header("⚙️ Controles")
    
    # Mostrar estatísticas das ações disponíveis
    total_stocks = len(get_all_tickers())
    total_sectors = len(get_sectors())
    
    st.info(f"""
    📊 **Base de Dados**
    - {total_stocks} ações disponíveis
    - {total_sectors} setores diferentes
    - Dados em tempo real via Yahoo Finance
    """)
    
    # Botão para atualizar lista de ações
    if st.button("🔄 Atualizar Lista de Ações", help="Busca nova lista atualizada de ações brasileiras"):
        with st.spinner("Atualizando lista de ações..."):
            st.session_state.dynamic_stocks = get_dynamic_stocks()
            st.success("Lista atualizada com sucesso!")
            st.rerun()
    
    # Controle de auto-refresh
    auto_refresh = st.checkbox(
        "🔄 Atualização automática (2s)", 
        value=st.session_state.auto_refresh,
        help="Ativa a atualização automática dos dados a cada 2 segundos"
    )
    st.session_state.auto_refresh = auto_refresh
    
    st.markdown("---")
    
    # Seletor de ações
    st.subheader("📋 Selecionar Ações para Monitoramento")
    
    # Criar listas ordenadas
    all_tickers = sorted(get_all_tickers())
    current_watched = set(st.session_state.watched_stocks)
    
    # Filtro de busca
    search_filter = st.text_input(
        "🔍 Filtrar ações (digite para buscar):",
        placeholder="Ex: Itaú, PETR4, Petrobras, Bancos...",
        key="stock_filter"
    )
    
    # Filtrar lista baseado na busca
    if search_filter:
        filtered_results = search_stocks(search_filter)
        filtered_tickers = [r['ticker'] for r in filtered_results]
    else:
        filtered_tickers = all_tickers
    
    # Controles de seleção rápida
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Selecionar Visíveis", use_container_width=True):
            new_selections = current_watched.union(set(filtered_tickers))
            st.session_state.watched_stocks = list(new_selections)
            st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
            st.success(f"✅ {len(filtered_tickers)} ações adicionadas!")
            st.rerun()
    
    with col2:
        if st.button("❌ Desmarcar Visíveis", use_container_width=True):
            new_selections = current_watched - set(filtered_tickers)
            st.session_state.watched_stocks = list(new_selections)
            st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
            st.success(f"✅ {len(filtered_tickers)} ações removidas!")
            st.rerun()
    
    with col3:
        if st.button("🔄 Limpar Tudo", use_container_width=True):
            st.session_state.watched_stocks = []
            st.session_state.watchlist_manager.save_watchlist([])
            st.success("✅ Lista limpa!")
            st.rerun()
    
    st.markdown("---")
    
    # Container scrollável com checkboxes
    st.write(f"**📊 Ações Disponíveis ({len(filtered_tickers)} de {len(all_tickers)}):**")
    
    # Agrupar por setor se não estiver filtrando
    if not search_filter:
        # Mostrar por setor
        sectors = get_sectors()
        selected_sector_filter = st.selectbox(
            "Filtrar por setor:",
            options=["Todos os setores"] + sectors,
            key="sector_filter"
        )
        
        if selected_sector_filter != "Todos os setores":
            filtered_tickers = get_tickers_by_sector(selected_sector_filter)
    
    # Mostrar checkboxes em container scrollável
    with st.container():
        # Limitar a 50 ações por vez para performance
        display_tickers = filtered_tickers[:50]
        if len(filtered_tickers) > 50:
            st.info(f"Mostrando primeiras 50 de {len(filtered_tickers)} ações. Use o filtro para refinar a busca.")
        
        # Checkbox para cada ação
        changes_made = False
        new_watched_set = current_watched.copy()
        
        # Usar formulário para processar mudanças em lote
        with st.form("stock_selection_form"):
            for ticker in display_tickers:
                name = get_stock_name(ticker)
                sector = st.session_state.dynamic_stocks.get(ticker, {}).get('sector', 'N/A')
                
                # Checkbox para cada ação
                is_selected = st.checkbox(
                    f"**{ticker}** - {name}",
                    value=ticker in current_watched,
                    key=f"checkbox_{ticker}",
                    help=f"Setor: {sector}"
                )
                
                # Atualizar conjunto baseado na seleção
                if is_selected and ticker not in current_watched:
                    new_watched_set.add(ticker)
                    changes_made = True
                elif not is_selected and ticker in current_watched:
                    new_watched_set.discard(ticker)
                    changes_made = True
            
            # Botão para aplicar mudanças
            if st.form_submit_button("💾 Salvar Seleções", type="primary"):
                st.session_state.watched_stocks = list(new_watched_set)
                st.session_state.watchlist_manager.save_watchlist(st.session_state.watched_stocks)
                st.success(f"✅ Watchlist atualizada! {len(st.session_state.watched_stocks)} ações selecionadas.")
                st.rerun()
    
    st.markdown("---")
    
    # Resumo da seleção atual
    st.subheader("📊 Ações Selecionadas")
    if st.session_state.watched_stocks:
        st.info(f"📈 **{len(st.session_state.watched_stocks)} ações** sendo monitoradas")
        
        # Mostrar ações em chips/tags
        if len(st.session_state.watched_stocks) <= 10:
            for stock in st.session_state.watched_stocks:
                st.caption(f"• {stock} - {get_stock_name(stock)}")
        else:
            st.caption(f"• {', '.join(st.session_state.watched_stocks[:5])} e mais {len(st.session_state.watched_stocks)-5} ações...")
    else:
        st.warning("⚠️ Nenhuma ação selecionada para monitoramento")
    
    # Botão de atualização manual
    st.markdown("---")
    if st.button("🔄 Atualizar Dados", type="secondary", use_container_width=True):
        st.session_state.last_update = None
        st.rerun()

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
        
        # Informações de status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Ações Monitoradas", len(st.session_state.watched_stocks))
        with col2:
            if st.session_state.last_update:
                update_time = datetime.fromtimestamp(st.session_state.last_update).strftime("%H:%M:%S")
                st.metric("🕐 Última Atualização", update_time)
        with col3:
            status_text = "🔄 Ativo" if auto_refresh else "⏸️ Pausado"
            st.metric("🔄 Auto-refresh", status_text)
        
        st.markdown("---")
        
        # Tabela de dados
        with table_container:
            st.subheader("💹 Dados das Ações")
            
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
            
            # Exibir tabela
            st.dataframe(
                formatted_df,
                use_container_width=True,
                height=400,
                column_config={
                    "Ticker": st.column_config.TextColumn("Código", width="small"),
                    "Nome": st.column_config.TextColumn("Nome da Empresa", width="medium"),
                    "Preço Atual": st.column_config.TextColumn("Preço Atual", width="small"),
                    "Variação (%)": st.column_config.TextColumn("Variação (%)", width="small"),
                    "DY Atual (%)": st.column_config.TextColumn("DY Atual", width="small"),
                    "DY Médio 5a (%)": st.column_config.TextColumn("DY Médio 5a", width="small"),
                    "P/L": st.column_config.TextColumn("P/L", width="small"),
                    "P/VP": st.column_config.TextColumn("P/VP", width="small"),
                    "Margem Líq. (%)": st.column_config.TextColumn("Margem Líq.", width="small"),
                    "Valor de Mercado": st.column_config.TextColumn("Valor de Mercado", width="medium"),
                    "Setor": st.column_config.TextColumn("Setor", width="medium")
                }
            )
    else:
        status_placeholder.error("❌ Erro ao carregar dados das ações")

else:
    st.info("📝 Adicione algumas ações na barra lateral para começar o monitoramento")

# Auto-refresh logic
if auto_refresh:
    time.sleep(0.1)  # Pequena pausa para evitar refresh muito agressivo
    st.rerun()

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
    💡 Dados fornecidos pelo Yahoo Finance | Atualização em tempo real a cada 2 segundos
    </div>
    """,
    unsafe_allow_html=True
)
