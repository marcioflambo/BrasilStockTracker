import locale
from typing import Union

def format_currency(value: Union[float, str]) -> str:
    """
    Formata valores monetários em reais brasileiros
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        String formatada em R$
    """
    if value == 'N/A' or value is None:
        return 'N/A'
    
    try:
        # Configurar locale para Brasil (fallback se não disponível)
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'pt_BR')
            except:
                pass  # Usar formato padrão se locale não disponível
        
        if isinstance(value, str):
            value = float(value)
        
        # Formatação manual para garantir compatibilidade
        if value >= 1_000_000_000:
            return f"R$ {value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"R$ {value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"R$ {value/1_000:.2f}K"
        else:
            return f"R$ {value:.2f}"
            
    except (ValueError, TypeError):
        return 'N/A'

def format_percentage(value: Union[float, str]) -> str:
    """
    Formata valores percentuais
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        String formatada com %
    """
    if value == 'N/A' or value is None:
        return 'N/A'
    
    try:
        if isinstance(value, str):
            value = float(value)
        
        # Adicionar emoji para indicar tendência
        if value > 0:
            return f"📈 +{value:.2f}%"
        elif value < 0:
            return f"📉 {value:.2f}%"
        else:
            return f"➡️ {value:.2f}%"
            
    except (ValueError, TypeError):
        return 'N/A'

def format_market_cap(value: Union[float, str]) -> str:
    """
    Formata valor de mercado em formato legível
    
    Args:
        value: Valor de mercado
        
    Returns:
        String formatada (ex: R$ 150.2B)
    """
    if value == 'N/A' or value is None:
        return 'N/A'
    
    try:
        if isinstance(value, str):
            value = float(value)
        
        if value >= 1_000_000_000_000:  # Trilhões
            return f"R$ {value/1_000_000_000_000:.1f}T"
        elif value >= 1_000_000_000:  # Bilhões
            return f"R$ {value/1_000_000_000:.1f}B"
        elif value >= 1_000_000:  # Milhões
            return f"R$ {value/1_000_000:.1f}M"
        elif value >= 1_000:  # Milhares
            return f"R$ {value/1_000:.1f}K"
        else:
            return f"R$ {value:.2f}"
            
    except (ValueError, TypeError):
        return 'N/A'

def validate_ticker(ticker: str) -> bool:
    """
    Valida se um ticker está no formato correto para ações brasileiras
    
    Args:
        ticker: Código da ação
        
    Returns:
        True se válido, False caso contrário
    """
    if not ticker:
        return False
    
    ticker = ticker.upper().strip()
    
    # Verificar se termina com .SA (ações brasileiras no Yahoo Finance)
    if not ticker.endswith('.SA'):
        return False
    
    # Remover .SA para validar o código
    code = ticker[:-3]
    
    # Código deve ter 4-6 caracteres
    if len(code) < 4 or len(code) > 6:
        return False
    
    # Deve começar com letras e pode terminar com números
    if not code[:4].isalpha():
        return False
    
    return True

def get_sector_emoji(sector: str) -> str:
    """
    Retorna emoji correspondente ao setor
    
    Args:
        sector: Nome do setor
        
    Returns:
        Emoji do setor
    """
    sector_emojis = {
        'Technology': '💻',
        'Financial Services': '🏦',
        'Healthcare': '🏥',
        'Consumer Defensive': '🛒',
        'Communication Services': '📱',
        'Energy': '⚡',
        'Basic Materials': '🏭',
        'Consumer Cyclical': '🚗',
        'Real Estate': '🏠',
        'Utilities': '🔌',
        'Industrials': '🏗️'
    }
    
    return sector_emojis.get(sector, '📊')
