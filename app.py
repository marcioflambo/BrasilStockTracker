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

def get_besst_sector_tickers():
    """Retorna apenas tickers de empresas dos setores BESST"""
    return stock_db.get_besst_sector_tickers()

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
        tab1, tab2, tab3 = st.tabs(["🔧 Controles", "📊 Base de Dados", "🎯 Filtros & Seleção"])
        
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
            st.subheader("📈 Metodologia BESST - Luiz Barsi Filho")
            st.write("Filtre ações que atendem aos critérios da metodologia BESST:")
            
            col1, col2 = st.columns(2)
            with col1:
                apply_barsi_filter = st.checkbox(
                    "Aplicar filtro BESST",
                    help="Mostra apenas ações que atendem aos critérios da metodologia BESST"
                )
            
            with col2:
                barsi_minimum_score = st.selectbox(
                    "Pontuação mínima:",
                    options=["Todas", "Boas (2/4)", "Excelentes (3/4)", "Só BESST (4/4)"],
                    help="Escolha a pontuação mínima dos critérios BESST"
                )
            
            st.markdown("---")
            
            # Seleção de ações na mesma aba
            st.subheader("📋 Seleção de Ações")
            
            # Criar listas ordenadas
            all_tickers = sorted(get_all_tickers())
            
            if apply_barsi_filter:
                st.info("🎯 **Critérios BESST aplicados:**\n"
                       "• **B**ancos, **E**nergia, **S**aneamento, **S**eguros, **T**elecomunicações\n"
                       "• Paga dividendos consistentemente\n"
                       "• Empresa consolidada (valor > R$ 1 bilhão)\n"
                       "• Solidez financeira (ROE > 10%)")
                
                # Mostrar estatísticas do banco de dados
                total_stocks = len(all_tickers)
                besst_sector_stocks = get_besst_sector_tickers()
                st.info(f"📊 **Base de dados**: {total_stocks} ações brasileiras disponíveis\n"
                       f"🎯 **Setores BESST**: {len(besst_sector_stocks)} empresas dos setores corretos\n"
                       f"⚡ **Otimização**: Analisando apenas empresas dos setores BESST")
                
                # Botão para análise completa otimizada
                if st.button("🔍 Analisar setores BESST completos", use_container_width=True):
                    if not besst_sector_stocks:
                        st.warning("Nenhuma empresa dos setores BESST encontrada na base de dados.")
                    else:
                        st.info(f"⏱️ Analisando {len(besst_sector_stocks)} empresas dos setores BESST...")
                        
                        # Análise otimizada apenas dos setores BESST
                        batch_size = 20
                        total_batches = (len(besst_sector_stocks) + batch_size - 1) // batch_size
                        all_besst_stocks = []
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(0, len(besst_sector_stocks), batch_size):
                            batch = besst_sector_stocks[i:i + batch_size]
                            batch_num = i // batch_size + 1
                            
                            status_text.text(f"Processando lote {batch_num}/{total_batches} ({len(batch)} ações)")
                            progress_bar.progress(i / len(besst_sector_stocks))
                            
                            try:
                                batch_data = st.session_state.stock_manager.get_stock_data(batch)
                                if not batch_data.empty:
                                    for _, row in batch_data.iterrows():
                                        barsi_score = row.get('Critério Barsi', 'N/A')
                                        if '(' in str(barsi_score):
                                            try:
                                                score_text = str(barsi_score).split('(')[1].split(')')[0]
                                                current_score = int(score_text.split('/')[0])
                                                if current_score >= 2:  # Pelo menos "Boas"
                                                    all_besst_stocks.append({
                                                        'ticker': row['Ticker'],
                                                        'score': current_score,
                                                        'barsi_full': barsi_score
                                                    })
                                            except:
                                                continue
                            except Exception as e:
                                st.warning(f"Erro no lote {batch_num}: {e}")
                                continue
                    
                    progress_bar.progress(1.0)
                    status_text.text("Análise completa!")
                    
                    # Resultados finais
                    if all_besst_stocks:
                        st.success(f"✅ **Análise Completa da Base de Dados:**")
                        
                        # Contar por pontuação
                        score_counts = {}
                        for stock in all_besst_stocks:
                            score = stock['score']
                            score_counts[score] = score_counts.get(score, 0) + 1
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Empresas Analisadas", f"{len(besst_sector_stocks)}")
                        with col2:
                            st.metric("Boas (2/4)", f"{score_counts.get(2, 0)}")
                        with col3:
                            st.metric("Excelentes (3/4)", f"{score_counts.get(3, 0)}")
                        with col4:
                            st.metric("BESST Perfeitas (4/4)", f"{score_counts.get(4, 0)}")
                        
                        # Mostrar as melhores
                        best_stocks = [s for s in all_besst_stocks if s['score'] >= 3]
                        if best_stocks:
                            st.write("**🏆 Melhores ações encontradas (3/4 ou 4/4):**")
                            for stock in best_stocks[:20]:  # Mostrar top 20
                                st.write(f"• {stock['ticker']} - {stock['barsi_full']}")
                    else:
                        st.warning("Nenhuma empresa dos setores BESST atendeu aos critérios completos.")
            current_watched = set(st.session_state.watched_stocks)
            
            # Aplicar filtros base
            if search_filter:
                filtered_results = search_stocks(search_filter)
                filtered_tickers = [r['ticker'] for r in filtered_results]
            elif selected_sector != "Todos":
                filtered_tickers = get_tickers_by_sector(selected_sector)
            else:
                # Se não há filtros específicos, usar uma lista maior para o filtro Barsi
                filtered_tickers = all_tickers[:100] if apply_barsi_filter else all_tickers[:30]
            
            # Aplicar filtro Barsi se selecionado
            if apply_barsi_filter:
                # Usar apenas empresas dos setores BESST para melhor performance
                if not st.session_state.watched_stocks and not search_filter and selected_sector == "Todos":
                    st.info("💡 Criando lista inicial com base nos critérios BESST...")
                    sample_tickers = besst_sector_stocks[:30]  # Usar apenas setores BESST
                else:
                    # Filtrar apenas setores BESST se não há filtros específicos
                    if not search_filter and selected_sector == "Todos":
                        sample_tickers = besst_sector_stocks[:20]
                    else:
                        sample_tickers = filtered_tickers[:20]
                
                # Mostrar progresso simples
                with st.spinner(f"Analisando {len(sample_tickers)} ações com critérios BESST..."):
                    try:
                        # Buscar dados das ações
                        stock_data = st.session_state.stock_manager.get_stock_data(sample_tickers)
                        
                        barsi_filtered = []
                        
                        if not stock_data.empty:
                            for _, row in stock_data.iterrows():
                                barsi_score = row.get('Critério Barsi', 'N/A')
                                
                                # Extrair pontuação numérica
                                if '(' in str(barsi_score):
                                    try:
                                        score_text = str(barsi_score).split('(')[1].split(')')[0]
                                        current_score = int(score_text.split('/')[0])
                                        
                                        # Aplicar critério de pontuação mínima
                                        if barsi_minimum_score == "Todas":
                                            barsi_filtered.append(row['Ticker'])
                                        elif barsi_minimum_score == "Boas (2/4)" and current_score >= 2:
                                            barsi_filtered.append(row['Ticker'])
                                        elif barsi_minimum_score == "Excelentes (3/4)" and current_score >= 3:
                                            barsi_filtered.append(row['Ticker'])
                                        elif barsi_minimum_score == "Só BESST (4/4)" and current_score >= 4:
                                            barsi_filtered.append(row['Ticker'])
                                    except:
                                        continue
                        
                        filtered_tickers = barsi_filtered
                        
                        # Mensagem específica baseada no contexto
                        if not st.session_state.watched_stocks and not search_filter and selected_sector == "Todos":
                            st.success(f"✅ {len(filtered_tickers)} ações encontradas que atendem aos critérios BESST")
                        else:
                            filter_context = []
                            if search_filter:
                                filter_context.append(f"busca '{search_filter}'")
                            if selected_sector != "Todos":
                                filter_context.append(f"setor '{selected_sector}'")
                            
                            context_text = " + ".join(filter_context) if filter_context else "filtros aplicados"
                            st.success(f"✅ {len(filtered_tickers)} ações atendem aos critérios BESST + {context_text}")
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao aplicar filtro BESST: {str(e)}")
                        # Usar lista padrão em caso de erro
                        filtered_tickers = all_tickers[:20]
                
                # Se não encontrou nenhuma ação, usar lista padrão
                if not filtered_tickers:
                    st.warning("⚠️ Nenhuma ação encontrada com os critérios BESST. Mostrando lista padrão.")
                    filtered_tickers = all_tickers[:20]
            
            # Botões de seleção rápida
            col1, col2, col3 = st.columns(3)
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
            
            with col3:
                # Botão especial para lista inicial BESST
                if not st.session_state.watched_stocks and apply_barsi_filter and filtered_tickers:
                    if st.button("🎯 Criar Lista BESST", use_container_width=True, type="primary"):
                        # Selecionar as melhores ações BESST (limitado a 20)
                        best_besst = filtered_tickers[:20]
                        st.session_state.watched_stocks = best_besst
                        st.success(f"✅ Lista inicial criada com {len(best_besst)} ações que atendem aos critérios BESST!")
                        st.rerun()
            
            # Lista de seleção compacta
            if filtered_tickers:
                # Mostrar dica para lista inicial se não há ações monitoradas
                if not st.session_state.watched_stocks and apply_barsi_filter:
                    st.info("💡 **Dica:** Use o botão 'Criar Lista BESST' para começar com uma seleção inteligente das melhores ações!")
                
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
                if not search_filter and selected_sector == "Todos" and not apply_barsi_filter:
                    st.info("🎯 **Sugestão:** Ative o filtro BESST para ver uma seleção inteligente de ações que atendem aos critérios de investimento de Luiz Barsi!")
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