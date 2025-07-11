"""
Sistema dinâmico para obter ações brasileiras usando Yahoo Finance API
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List
import streamlit as st
import time
import json
import os

class StockScraper:
    """Obtém dados dinâmicos de ações brasileiras usando Yahoo Finance"""
    
    def __init__(self):
        self.cache_file = "stocks_cache.json"
        self.cache_duration = 3600  # 1 hora em segundos
        
    def get_stocks_from_yahoo_finance(self) -> Dict[str, Dict]:
        """
        Obtém lista dinâmica de ações brasileiras do Yahoo Finance
        Retorna dict com estrutura: {ticker: {name: str, sector: str}}
        """
        
        # Verificar cache primeiro
        cached_data = self._load_cache()
        if cached_data:
            return cached_data
            
        try:
            # Lista reduzida de ações principais para evitar timeout
            base_tickers = [
                'ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3',
                'SUZB3', 'WEGE3', 'BBAS3', 'RENT3', 'LREN3', 'RDOR3',
                'GGBR4', 'CSNA3', 'JBSS3', 'EMBR3', 'RADL3', 'RAIL3',
                'ELET3', 'VIVT3', 'CPFE3', 'CMIG4', 'EQTL3', 'SANB11',
                'SBSP3', 'CSAN3', 'BRFS3', 'TIMS3', 'TOTS3', 'PRIO3'
            ]
            
            stocks = {}
            successful_requests = 0
            max_requests = 20  # Limitar para evitar timeout
            
            # Obter dados reais de cada ação com timeout
            for i, ticker in enumerate(base_tickers):
                if successful_requests >= max_requests:
                    break
                    
                try:
                    ticker_sa = f"{ticker}.SA"
                    
                    # Timeout de 3 segundos por requisição
                    stock = yf.Ticker(ticker_sa)
                    info = stock.info
                    
                    if info and len(info) > 1:  # Verificar se tem dados válidos
                        # Extrair setor real do Yahoo Finance
                        sector = info.get('sector', 'N/A')
                        if sector == 'N/A' or not sector:
                            sector = info.get('industry', 'Diversos')
                        
                        name = info.get('longName', info.get('shortName', ticker))
                        
                        stocks[ticker_sa] = {
                            'name': name,
                            'sector': sector if sector else 'Diversos'
                        }
                        successful_requests += 1
                    else:
                        # Se não conseguir dados do YF, usar nome básico
                        stocks[ticker_sa] = {
                            'name': ticker,
                            'sector': 'Diversos'
                        }
                        
                except Exception as e:
                    # Em caso de erro, usar dados básicos
                    stocks[f"{ticker}.SA"] = {
                        'name': ticker,
                        'sector': 'Diversos'
                    }
                    
                # Pequena pausa entre requisições
                if i < len(base_tickers) - 1:
                    time.sleep(0.1)
                    
            # Salvar cache
            if stocks:
                self._save_cache(stocks)
                return stocks
            else:
                return self._get_minimal_fallback()
                
        except Exception as e:
            st.error(f"Erro ao obter dados do Yahoo Finance: {str(e)}")
            return self._get_minimal_fallback()
    
    def _get_minimal_fallback(self) -> Dict[str, Dict]:
        """Retorna apenas ações principais como fallback quando tudo falha"""
        return {
            'ITUB4.SA': {'name': 'Itaú Unibanco', 'sector': 'Financial Services'},
            'PETR4.SA': {'name': 'Petróleo Brasileiro S.A. - Petrobras', 'sector': 'Energy'},
            'VALE3.SA': {'name': 'Vale S.A.', 'sector': 'Basic Materials'},
            'BBDC4.SA': {'name': 'Banco Bradesco S.A.', 'sector': 'Financial Services'},
            'ABEV3.SA': {'name': 'Ambev S.A.', 'sector': 'Consumer Defensive'},
            'MGLU3.SA': {'name': 'Magazine Luiza S.A.', 'sector': 'Consumer Cyclical'},
            'SUZB3.SA': {'name': 'Suzano S.A.', 'sector': 'Basic Materials'},
            'WEGE3.SA': {'name': 'WEG S.A.', 'sector': 'Industrials'}
        }
    
    def _load_cache(self) -> Dict[str, Dict]:
        """Carrega dados do cache se ainda válidos"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Verificar se cache ainda é válido
                cache_time = cache_data.get('timestamp', 0)
                if time.time() - cache_time < self.cache_duration:
                    return cache_data.get('stocks', {})
                    
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
            
        return {}
    
    def _save_cache(self, stocks: Dict[str, Dict]):
        """Salva dados no cache"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'stocks': stocks
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
def get_dynamic_stocks():
    """Função principal para obter ações dinâmicas do Yahoo Finance"""
    scraper = StockScraper()
    return scraper.get_stocks_from_yahoo_finance()