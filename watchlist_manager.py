"""
Gerenciador de watchlist com persistência em JSON
"""

import json
import os
import pandas as pd
from typing import List, Set

class WatchlistManager:
    """Gerencia a lista de ações monitoradas com persistência"""
    
    def __init__(self, filename: str = "watchlist.json"):
        self.filename = filename
        self.default_stocks = ['ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'BBDC4.SA', 'ABEV3.SA']
    
    def load_watchlist(self) -> List[str]:
        """Carrega lista de ações monitoradas do arquivo JSON"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('watched_stocks', self.default_stocks)
            else:
                return self.default_stocks
        except Exception as e:
            print(f"Erro ao carregar watchlist: {e}")
            return self.default_stocks
    
    def save_watchlist(self, watched_stocks: List[str]):
        """Salva lista de ações monitoradas no arquivo JSON"""
        try:
            data = {
                'watched_stocks': watched_stocks,
                'last_updated': json.dumps(str(pd.Timestamp.now()))
            }
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erro ao salvar watchlist: {e}")
    
    def add_stock(self, ticker: str, current_list: List[str]) -> List[str]:
        """Adiciona uma ação à lista"""
        if ticker not in current_list:
            new_list = current_list + [ticker]
            self.save_watchlist(new_list)
            return new_list
        return current_list
    
    def remove_stock(self, ticker: str, current_list: List[str]) -> List[str]:
        """Remove uma ação da lista"""
        if ticker in current_list:
            new_list = [stock for stock in current_list if stock != ticker]
            self.save_watchlist(new_list)
            return new_list
        return current_list
    
    def update_watchlist(self, selected_tickers: List[str]):
        """Atualiza completamente a watchlist"""
        self.save_watchlist(selected_tickers)
        return selected_tickers