import streamlit as st
import pandas as pd
import time
from datetime import datetime
from stock_data import StockDataManager
from utils import format_currency, format_percentage, format_market_cap

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

if 'watched_stocks' not in st.session_state:
    st.session_state.watched_stocks = ['ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'BBDC4.SA', 'ABEV3.SA']

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Título principal
st.title("📈 Monitor de Ações Brasileiras")
st.markdown("---")

# Sidebar para controles
with st.sidebar:
    st.header("⚙️ Controles")
    
    # Controle de auto-refresh
    auto_refresh = st.checkbox(
        "🔄 Atualização automática (2s)", 
        value=st.session_state.auto_refresh,
        help="Ativa a atualização automática dos dados a cada 2 segundos"
    )
    st.session_state.auto_refresh = auto_refresh
    
    st.markdown("---")
    
    # Adicionar nova ação
    st.subheader("➕ Adicionar Ação")
    new_stock = st.text_input(
        "Código da ação (ex: ITUB4.SA):",
        placeholder="Digite o ticker..."
    ).upper()
    
    if st.button("Adicionar", type="primary"):
        if new_stock and new_stock not in st.session_state.watched_stocks:
            # Validar se a ação existe
            test_data = st.session_state.stock_manager.get_stock_data([new_stock])
            if not test_data.empty and test_data.iloc[0]['Preço Atual'] != 'N/A':
                st.session_state.watched_stocks.append(new_stock)
                st.success(f"✅ {new_stock} adicionada com sucesso!")
                st.rerun()
            else:
                st.error(f"❌ Ação {new_stock} não encontrada ou inválida")
        elif new_stock in st.session_state.watched_stocks:
            st.warning(f"⚠️ {new_stock} já está na lista")
        elif not new_stock:
            st.warning("⚠️ Digite um código de ação válido")
    
    st.markdown("---")
    
    # Lista de ações monitoradas
    st.subheader("📋 Ações Monitoradas")
    for i, stock in enumerate(st.session_state.watched_stocks):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(stock)
        with col2:
            if st.button("🗑️", key=f"remove_{i}", help=f"Remover {stock}"):
                st.session_state.watched_stocks.remove(stock)
                st.rerun()
    
    # Botão de atualização manual
    st.markdown("---")
    if st.button("🔄 Atualizar Agora", type="secondary"):
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
