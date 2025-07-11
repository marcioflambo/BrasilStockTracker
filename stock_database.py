"""
Sistema completo de banco de dados de ações brasileiras
Gerencia arquivo JSON com dados fixos e atualizações sob demanda
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import streamlit as st
from dados_mercado_scraper import dados_mercado_scraper

class StockDatabase:
    """Gerencia banco de dados completo de ações brasileiras"""
    
    def __init__(self, db_file: str = "stock_database.json"):
        self.db_file = db_file
        self.cache_duration = timedelta(hours=24)  # Cache por 24 horas
        
    def load_database(self) -> Dict[str, Dict]:
        """Carrega banco de dados de ações do arquivo JSON"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verifica se precisa atualizar
                    if self._is_cache_valid(data.get('last_updated')):
                        return data.get('stocks', {})
                    else:
                        st.info("Base de dados desatualizada. Considere atualizar nas configurações.")
                        return data.get('stocks', {})
            else:
                # Cria arquivo inicial com dados básicos
                return self._create_initial_database()
        except Exception as e:
            st.error(f"Erro ao carregar base de dados: {e}")
            return self._get_fallback_stocks()
    
    def _create_initial_database(self) -> Dict[str, Dict]:
        """Cria arquivo inicial vazio - dados serão carregados do DadosMercado"""
        database = {
            'last_updated': None,
            'stocks': {},
            'total_stocks': 0,
            'source': 'Aguardando primeira atualização'
        }
        
        self._save_database(database)
        return {}
    
    def update_database(self, progress_callback=None) -> bool:
        """Atualiza completamente o banco de dados de ações"""
        try:
            if progress_callback:
                progress_callback("🔍 Buscando lista completa de ações do DadosMercado...")
            
            # Busca todas as ações do site DadosMercado
            all_stocks = dados_mercado_scraper.get_all_stocks_from_site()
            
            if progress_callback:
                progress_callback(f"📊 Encontradas {len(all_stocks)} ações. Enriquecendo dados com Yahoo Finance...")
            
            # Enriquece dados com Yahoo Finance
            enriched_stocks = self._enrich_with_yahoo_finance(all_stocks, progress_callback)
            
            # Salva no arquivo
            database = {
                'last_updated': datetime.now().isoformat(),
                'stocks': enriched_stocks,
                'total_stocks': len(enriched_stocks),
                'source': 'DadosMercado + Yahoo Finance'
            }
            
            self._save_database(database)
            
            if progress_callback:
                progress_callback(f"✅ Base de dados atualizada com {len(enriched_stocks)} ações!")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Erro na atualização: {str(e)}")
            return False
    
    def _fetch_all_brazilian_stocks(self) -> List[str]:
        """Busca lista completa de ações brasileiras do DadosMercado"""
        try:
            # Delega para o scraper do DadosMercado
            stocks_data = dados_mercado_scraper.get_all_stocks_from_site()
            return list(stocks_data.keys())
        except Exception as e:
            print(f"Erro ao buscar ações: {e}")
            return []
    
    def _enrich_with_yahoo_finance(self, stocks: Dict[str, Dict], progress_callback=None) -> Dict[str, Dict]:
        """Enriquece dados do DadosMercado com informações do Yahoo Finance"""
        enriched_stocks = {}
        total = len(stocks)
        completed = 0
        
        def enrich_stock(ticker, base_data):
            try:
                # Usa dados do DadosMercado como base
                enriched_data = base_data.copy()
                
                # Tenta enriquecer com Yahoo Finance
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if info and len(info) > 1:
                    # Atualiza com dados mais precisos do Yahoo Finance
                    enriched_data.update({
                        'yf_name': info.get('shortName', info.get('longName', '')),
                        'yf_sector': info.get('sector', ''),
                        'yf_industry': info.get('industry', ''),
                        'market_cap': info.get('marketCap', 0),
                        'currency': info.get('currency', 'BRL'),
                        'exchange': info.get('exchange', 'SAO'),
                        'country': info.get('country', 'Brazil'),
                        'employees': info.get('employees', 0),
                        'website': info.get('website', ''),
                        'business_summary': info.get('businessSummary', '')[:200] if info.get('businessSummary') else ''
                    })
                    
                    # Usa nome do Yahoo Finance se disponível e mais completo
                    if enriched_data.get('yf_name') and len(enriched_data['yf_name']) > len(enriched_data['name']):
                        enriched_data['name'] = enriched_data['yf_name']
                    
                    # Usa setor do Yahoo Finance se disponível
                    if enriched_data.get('yf_sector') and enriched_data['yf_sector'] != 'N/A':
                        enriched_data['sector'] = enriched_data['yf_sector']
                    
                    # Usa indústria do Yahoo Finance se disponível
                    if enriched_data.get('yf_industry') and enriched_data['yf_industry'] != 'N/A':
                        enriched_data['industry'] = enriched_data['yf_industry']
                
                return ticker, enriched_data
                
            except Exception as e:
                print(f"Erro ao enriquecer {ticker}: {e}")
                return ticker, base_data
        
        # Processa em lotes para evitar timeout
        batch_size = 8
        stock_items = list(stocks.items())
        
        for i in range(0, len(stock_items), batch_size):
            batch = stock_items[i:i+batch_size]
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(enrich_stock, ticker, data) for ticker, data in batch]
                
                for future in as_completed(futures):
                    ticker, data = future.result()
                    completed += 1
                    
                    enriched_stocks[ticker] = data
                    
                    if progress_callback and completed % 20 == 0:
                        progress_callback(f"⚡ Enriquecendo dados... {completed}/{total} ações")
            
            # Pausa entre lotes para evitar rate limiting
            time.sleep(2)
        
        return enriched_stocks
    
    def _save_database(self, database: Dict):
        """Salva banco de dados no arquivo JSON"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Erro ao salvar banco de dados: {e}")
    
    def _is_cache_valid(self, last_updated: str) -> bool:
        """Verifica se o cache ainda está válido"""
        if not last_updated:
            return False
        
        try:
            last_update = datetime.fromisoformat(last_updated)
            return datetime.now() - last_update < self.cache_duration
        except:
            return False
    
    def _get_fallback_stocks(self) -> Dict[str, Dict]:
        """Retorna fallback mínimo - força atualização"""
        return {}
    
    def get_all_tickers(self) -> List[str]:
        """Retorna lista de todos os tickers disponíveis"""
        stocks = self.load_database()
        return list(stocks.keys())
    
    def get_sectors(self) -> List[str]:
        """Retorna lista de setores únicos"""
        stocks = self.load_database()
        sectors = set()
        for stock_data in stocks.values():
            sector = stock_data.get('sector', 'N/A')
            if sector and sector != 'N/A':
                sectors.add(sector)
        return sorted(list(sectors))
    
    def get_tickers_by_sector(self, sector: str) -> List[str]:
        """Retorna tickers de um setor específico"""
        stocks = self.load_database()
        return [ticker for ticker, data in stocks.items() 
                if data.get('sector') == sector]
    
    def search_stocks(self, query: str) -> List[str]:
        """Busca ações por nome ou ticker"""
        stocks = self.load_database()
        query = query.lower()
        results = []
        
        for ticker, data in stocks.items():
            if (query in ticker.lower() or 
                query in data.get('name', '').lower() or
                query in data.get('industry', '').lower()):
                results.append(ticker)
        
        return results[:20]  # Limita a 20 resultados
    
    def get_stock_info(self, ticker: str) -> Optional[Dict]:
        """Retorna informações de uma ação específica"""
        stocks = self.load_database()
        return stocks.get(ticker)
    
    def get_besst_sector_tickers(self) -> List[str]:
        """Retorna apenas tickers de empresas dos setores BESST"""
        stocks = self.load_database()
        besst_tickers = []
        
        # Critérios de setores BESST
        besst_keywords = [
            'financeiro', 'bancos', 'financial', 'banco', 'bank',
            'energia', 'elétrica', 'utilities', 'electric', 'energy',
            'saneamento', 'water', 'sanitation', 'básico',
            'seguro', 'insurance', 'seguradora', 'previdência',
            'telecomunicações', 'communication', 'telecom', 'telefonia'
        ]
        
        for ticker, data in stocks.items():
            if ticker.startswith('_'):  # Pular metadados
                continue
                
            if isinstance(data, dict):
                sector = data.get('sector', '').lower()
                industry = data.get('industry', '').lower()
                
                # Verificar se pertence aos setores BESST
                is_besst_sector = any(keyword in sector or keyword in industry 
                                    for keyword in besst_keywords)
                
                if is_besst_sector:
                    besst_tickers.append(ticker)
        
        return sorted(besst_tickers)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stocks = self.load_database()
                    total_stocks = len([k for k in stocks.keys() if not k.startswith('_')])
                    besst_count = len(self.get_besst_sector_tickers())
                    
                    return {
                        'total_stocks': total_stocks,
                        'besst_sector_stocks': besst_count,
                        'total_sectors': len(self.get_sectors()),
                        'last_updated': data.get('last_updated', 'N/A'),
                        'cache_valid': self._is_cache_valid(data.get('last_updated'))
                    }
        except:
            pass
        
        return {
            'total_stocks': 0,
            'besst_sector_stocks': 0,
            'total_sectors': 0,
            'last_updated': 'N/A',
            'cache_valid': False
        }

# Instância global
stock_db = StockDatabase()