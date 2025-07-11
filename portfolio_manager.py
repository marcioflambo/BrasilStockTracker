"""
Gerenciador de carteira de investimentos com quantidade de ações
"""

import json
import os
from typing import Dict, List
import streamlit as st

class PortfolioManager:
    """Gerencia carteira de investimentos com quantidades"""
    
    def __init__(self, filename: str = "portfolio.json"):
        self.filename = filename
        
    def load_portfolio(self) -> Dict[str, int]:
        """Carrega carteira com quantidades do arquivo JSON"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar carteira: {e}")
        return {}
    
    def save_portfolio(self, portfolio: Dict[str, int]):
        """Salva carteira no arquivo JSON"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(portfolio, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Erro ao salvar carteira: {e}")
    
    def add_position(self, ticker: str, quantity: int, current_portfolio: Dict[str, int]) -> Dict[str, int]:
        """Adiciona ou atualiza posição na carteira"""
        new_portfolio = current_portfolio.copy()
        if quantity > 0:
            new_portfolio[ticker] = quantity
        elif ticker in new_portfolio:
            del new_portfolio[ticker]
        return new_portfolio
    
    def calculate_future_dividends(self, portfolio: Dict[str, int], stock_data) -> Dict[str, float]:
        """Calcula dividendos futuros esperados baseado na carteira"""
        future_dividends = {}
        
        for ticker, quantity in portfolio.items():
            if quantity > 0:
                # Encontrar dados da ação
                stock_row = stock_data[stock_data['Ticker'] == ticker]
                if not stock_row.empty:
                    div_per_share = stock_row['Div/Ação (R$)'].iloc[0]
                    if div_per_share != 'N/A' and div_per_share > 0:
                        future_dividends[ticker] = div_per_share * quantity
                    else:
                        future_dividends[ticker] = 0
                else:
                    future_dividends[ticker] = 0
                    
        return future_dividends
    
    def get_portfolio_value(self, portfolio: Dict[str, int], stock_data) -> float:
        """Calcula valor total da carteira"""
        total_value = 0
        
        for ticker, quantity in portfolio.items():
            if quantity > 0:
                # Encontrar dados da ação
                stock_row = stock_data[stock_data['Ticker'] == ticker]
                if not stock_row.empty:
                    price = stock_row['Preço Atual'].iloc[0]
                    if price != 'N/A':
                        total_value += price * quantity
                        
        return total_value
    
    def filter_barsi_stocks(self, stock_data) -> List[str]:
        """Filtra ações que atendem aos critérios Barsi"""
        barsi_stocks = []
        
        for _, row in stock_data.iterrows():
            criteria = row.get('Critério Barsi', '')
            if '✅ Excelente' in criteria or '⚠️ Boa' in criteria:
                barsi_stocks.append(row['Ticker'])
                
        return barsi_stocks