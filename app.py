import streamlit as st
import pandas as pd
import time
from datetime import datetime
from stock_data import StockDataManager
from utils import format_currency, format_percentage, format_market_cap
from stock_database import stock_db

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

# Watchlist simples sem persistência
if 'watched_stocks' not in st.session_state:
    st.session_state.watched_stocks = []

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Funções auxiliares dinâmicas
def get_all_tickers():
    return stock_db.get_all_tickers()

def get_sectors():
    return stock_db.get_sectors()

def get_tickers_by_sector(sector):
    return stock_db.get_tickers_by_sector(sector)

def search_stocks(query):
    results = []
    tickers = stock_db.search_stocks(query)
    for ticker in tickers:
        info = stock_db.get_stock_info(ticker)
        if info:
            results.append({
                'ticker': ticker,
                'name': info.get('name', ticker.replace('.SA', '')),
                'sector': info.get('sector', 'Diversos')
            })
    return results

def get_stock_name(ticker):
    info = stock_db.get_stock_info(ticker)
    if info:
        return info.get('name', ticker.replace('.SA', ''))
    return ticker.replace('.SA', '')

def get_popular_stocks():
    # Retorna os primeiros 20 stocks da lista como populares
    return stock_db.get_all_tickers()[:20]

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
        # Criar tabs organizadas
        tab1, tab2, tab3, tab4 = st.tabs(["🔧 Controles", "📊 Base de Dados", "🎯 Filtros", "📋 Seleção"])
        
        with tab1:
            st.subheader("Controles da Aplicação")
            col1, col2 = st.columns(2)
            
            with col1:
                # Auto-refresh
                auto_refresh = st.checkbox(
                    "Atualização automática (2s)", 
                    value=st.session_state.auto_refresh,
                    help="Ativa a atualização automática dos dados"
                )
                st.session_state.auto_refresh = auto_refresh
                
                if st.button("🔄 Atualizar Dados Agora", type="secondary"):
                    st.session_state.last_update = None
                    st.rerun()
            
            with col2:
                if st.button("❌ Limpar Seleções"):
                    st.session_state.watched_stocks = []
                    st.success("Seleções limpas!")
                    st.rerun()
                
                if st.button("⭐ Adicionar Populares"):
                    popular = get_popular_stocks()[:10]
                    current = set(st.session_state.watched_stocks)
                    new_stocks = [stock for stock in popular if stock not in current]
                    if new_stocks:
                        st.session_state.watched_stocks.extend(new_stocks[:5])
                        st.success(f"✅ {len(new_stocks[:5])} ações populares adicionadas!")
                        st.rerun()
                    else:
                        st.info("Todas as ações populares já estão na lista!")
        
        with tab2:
            st.subheader("Gerenciamento da Base de Dados")
            
            # Botão para atualizar base de dados completa
            if st.button("🔄 Atualizar Base de Dados", help="Busca todas as ações da B3 e atualiza informações"):
                progress_placeholder = st.empty()
                
                def update_progress(message):
                    progress_placeholder.info(message)
                
                with st.spinner("Atualizando base de dados completa..."):
                    success = stock_db.update_database(update_progress)
                    if success:
                        st.success("✅ Base de dados atualizada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar base de dados")
                
                progress_placeholder.empty()
            
            st.markdown("---")
            
            # Estatísticas da Base de Dados
            st.subheader("📊 Estatísticas")
            stats = stock_db.get_database_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Ações", f"{stats['total_stocks']:,}")
            with col2:
                st.metric("Setores", f"{stats['total_sectors']:,}")
            with col3:
                if stats['last_updated'] != 'N/A':
                    try:
                        from datetime import datetime
                        last_update = datetime.fromisoformat(stats['last_updated'])
                        formatted_date = last_update.strftime("%d/%m/%Y %H:%M")
                        st.metric("Última Atualização", formatted_date)
                    except:
                        st.metric("Última Atualização", "Erro na data")
                else:
                    st.metric("Última Atualização", "N/A")
            with col4:
                if stats['cache_valid']:
                    st.metric("Status", "✅ Atualizada")
                else:
                    st.metric("Status", "⚠️ Desatualizada")
        
        with tab3:
            st.subheader("Filtros e Estratégias")
            
            # Filtros básicos
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
            
            st.markdown("---")
            
            # Filtro estratégia Barsi
            st.subheader("📈 Estratégia Luiz Barsi Filho")
            st.write("Filtre ações que atendem aos critérios da metodologia Barsi:")
            
            col1, col2 = st.columns(2)
            with col1:
                apply_barsi_filter = st.checkbox(
                    "Aplicar filtro Barsi",
                    help="Mostra apenas ações que atendem aos critérios da metodologia Barsi"
                )
            
            with col2:
                barsi_minimum_score = st.selectbox(
                    "Pontuação mínima:",
                    options=["Todas", "Boas (2/4)", "Excelentes (3/4)"],
                    help="Escolha a pontuação mínima dos critérios Barsi"
                )
            
            if apply_barsi_filter:
                st.info("🎯 **Critérios Barsi aplicados:**\n"
                       "• Paga dividendos consistentemente\n"
                       "• P/L entre 3 e 15\n"
                       "• ROE > 15%\n"
                       "• Valor de mercado > R$ 1 bilhão")
        
        with tab4:
            st.subheader("Seleção de Ações para Monitoramento")
            
            # Criar listas ordenadas
            all_tickers = sorted(get_all_tickers())
            current_watched = set(st.session_state.watched_stocks)
            
            # Aplicar filtros
            if search_filter:
                filtered_results = search_stocks(search_filter)
                filtered_tickers = [r['ticker'] for r in filtered_results]
            elif selected_sector != "Todos":
                filtered_tickers = get_tickers_by_sector(selected_sector)
            else:
                filtered_tickers = all_tickers[:30]  # Limitar para performance
            
            # Aplicar filtro Barsi se selecionado
            if apply_barsi_filter and filtered_tickers:
                # Buscar dados das ações para aplicar filtro Barsi
                with st.spinner("Aplicando filtro Barsi..."):
                    barsi_filtered = []
                    stock_data = st.session_state.stock_manager.get_stock_data(filtered_tickers[:20])  # Limitar para performance
                    
                    for _, row in stock_data.iterrows():
                        barsi_score = row.get('Critério Barsi', 'N/A')
                        
                        # Extrair pontuação numérica
                        if '(' in barsi_score:
                            try:
                                score_text = barsi_score.split('(')[1].split(')')[0]
                                current_score = int(score_text.split('/')[0])
                                
                                # Aplicar critério de pontuação mínima
                                if barsi_minimum_score == "Todas":
                                    barsi_filtered.append(row['Ticker'])
                                elif barsi_minimum_score == "Boas (2/4)" and current_score >= 2:
                                    barsi_filtered.append(row['Ticker'])
                                elif barsi_minimum_score == "Excelentes (3/4)" and current_score >= 3:
                                    barsi_filtered.append(row['Ticker'])
                            except:
                                pass
                    
                    filtered_tickers = barsi_filtered
                    st.success(f"✅ {len(filtered_tickers)} ações atendem aos critérios Barsi")
            
            # Botões de seleção rápida
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Selecionar Filtradas", use_container_width=True):
                    new_selections = current_watched.union(set(filtered_tickers))
                    st.session_state.watched_stocks = list(new_selections)
                    st.success(f"{len(filtered_tickers)} ações adicionadas!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Desmarcar Filtradas", use_container_width=True):
                    new_selections = current_watched - set(filtered_tickers)
                    st.session_state.watched_stocks = list(new_selections)
                    st.success(f"{len(filtered_tickers)} ações removidas!")
                    st.rerun()
            
            # Lista de seleção compacta
            if filtered_tickers:
                st.write(f"**Ações encontradas ({len(filtered_tickers)}):**")
                
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
                        st.success(f"Watchlist atualizada! {len(st.session_state.watched_stocks)} ações.")
                        st.rerun()
            else:
                st.info("Nenhuma ação encontrada com os filtros aplicados.")

# Sidebar compacta
with st.sidebar:
    st.header("Status")
    
    # Status do auto-refresh
    if st.session_state.auto_refresh:
        st.success("🔄 Auto-refresh: ON")
    else:
        st.info("⏸️ Auto-refresh: OFF")
    
    # Última atualização
    if st.session_state.last_update:
        st.write(f"**Última atualização:** {st.session_state.last_update.strftime('%H:%M:%S')}")
    else:
        st.write("**Status:** Aguardando dados...")
    
    st.markdown("---")
    
    # Adicionar ações rápida
    st.subheader("➕ Adicionar Ação")
    
    # Input direto
    new_ticker = st.text_input(
        "Código da ação:",
        placeholder="Ex: PETR4",
        help="Digite o código da ação (sem .SA)"
    )
    
    if st.button("📌 Adicionar", use_container_width=True):
        if new_ticker:
            # Formatar ticker
            formatted_ticker = new_ticker.upper().strip()
            if not formatted_ticker.endswith('.SA'):
                formatted_ticker += '.SA'
            
            # Verificar se existe
            if formatted_ticker in get_all_tickers():
                if formatted_ticker not in st.session_state.watched_stocks:
                    st.session_state.watched_stocks.append(formatted_ticker)
                    st.success(f"✅ {formatted_ticker} adicionada!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ {formatted_ticker} já está na lista!")
            else:
                st.error(f"❌ {formatted_ticker} não encontrada!")
    
    # Ações populares
    if st.button("⭐ Adicionar Populares", use_container_width=True):
        popular = get_popular_stocks()[:10]
        current = set(st.session_state.watched_stocks)
        new_stocks = [stock for stock in popular if stock not in current]
        if new_stocks:
            st.session_state.watched_stocks.extend(new_stocks[:5])
            st.success(f"✅ {len(new_stocks[:5])} ações populares adicionadas!")
            st.rerun()
        else:
            st.info("Todas as ações populares já estão na lista!")

# Área principal: Monitor de ações
st.markdown("---")

# Verificar se há ações para monitorar
if not st.session_state.watched_stocks:
    st.info("📋 Nenhuma ação selecionada para monitoramento. Use o painel de configurações acima para adicionar ações.")
else:
    # Buscar dados das ações
    with st.spinner("Carregando dados das ações..."):
        try:
            stock_data = st.session_state.stock_manager.get_stock_data(st.session_state.watched_stocks)
            st.session_state.stock_data = stock_data
            st.session_state.last_update = datetime.now()
            
            if not stock_data.empty:
                # Formatação para exibição
                display_data = stock_data.copy()
                
                # Formatar colunas numéricas
                numeric_columns = ['Preço Atual', 'Variação (%)', 'DY Atual (%)', 'DY Médio 5a (%)', 
                                   'Div/Ação (R$)', 'P/L', 'P/VP', 'ROE (%)', 'Dívida/PL', 'Margem Líq. (%)']
                
                for col in numeric_columns:
                    if col in display_data.columns:
                        display_data[col] = pd.to_numeric(display_data[col], errors='coerce')
                
                # Criar dataframe formatado para exibição
                formatted_df = display_data.copy()
                
                # Aplicar formatações específicas
                if 'Preço Atual' in formatted_df.columns:
                    formatted_df['Preço Atual'] = formatted_df['Preço Atual'].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
                
                if 'Variação (%)' in formatted_df.columns:
                    formatted_df['Variação (%)'] = formatted_df['Variação (%)'].apply(lambda x: format_percentage(x) if pd.notna(x) else 'N/A')
                
                if 'Valor de Mercado' in formatted_df.columns:
                    formatted_df['Valor de Mercado'] = formatted_df['Valor de Mercado'].apply(lambda x: format_market_cap(x) if pd.notna(x) else 'N/A')
                
                percentage_cols = ['DY Atual (%)', 'DY Médio 5a (%)', 'ROE (%)', 'Margem Líq. (%)']
                for col in percentage_cols:
                    if col in formatted_df.columns:
                        formatted_df[col] = formatted_df[col].apply(lambda x: format_percentage(x) if pd.notna(x) else 'N/A')
                
                currency_cols = ['Div/Ação (R$)']
                for col in currency_cols:
                    if col in formatted_df.columns:
                        formatted_df[col] = formatted_df[col].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
                
                ratio_cols = ['P/L', 'P/VP', 'Dívida/PL']
                for col in ratio_cols:
                    if col in formatted_df.columns:
                        formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
                
                # Substituir NaN por N/A
                formatted_df = formatted_df.fillna('N/A')
                
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
                
            else:
                st.warning("⚠️ Não foi possível carregar dados para as ações selecionadas.")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {str(e)}")

# Auto-refresh
if st.session_state.auto_refresh and st.session_state.watched_stocks:
    time.sleep(2)
    st.rerun()