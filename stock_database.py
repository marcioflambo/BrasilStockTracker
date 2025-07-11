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
        """Cria arquivo inicial com algumas ações principais"""
        initial_stocks = {
            'PETR4.SA': {
                'name': 'Petrobras',
                'sector': 'Petróleo, Gás e Biocombustíveis',
                'isin': 'BRPETRACNPR6',
                'link': 'https://www.dadosdemercado.com.br/acoes/petr4'
            },
            'VALE3.SA': {
                'name': 'Vale',
                'sector': 'Mineração',
                'isin': 'BRVALEACNOR0',
                'link': 'https://www.dadosdemercado.com.br/acoes/vale3'
            },
            'ITUB4.SA': {
                'name': 'Itaú Unibanco',
                'sector': 'Bancos',
                'isin': 'BRITUBALCTB2',
                'link': 'https://www.dadosdemercado.com.br/acoes/itub4'
            },
            'BBDC4.SA': {
                'name': 'Bradesco',
                'sector': 'Bancos',
                'isin': 'BRBBDCACNPR8',
                'link': 'https://www.dadosdemercado.com.br/acoes/bbdc4'
            },
            'ABEV3.SA': {
                'name': 'Ambev',
                'sector': 'Bebidas',
                'isin': 'BRABEVACNOR6',
                'link': 'https://www.dadosdemercado.com.br/acoes/abev3'
            }
        }
        
        database = {
            'last_updated': datetime.now().isoformat(),
            'stocks': initial_stocks,
            'total_stocks': len(initial_stocks)
        }
        
        self._save_database(database)
        return initial_stocks
    
    def update_database(self, progress_callback=None) -> bool:
        """Atualiza completamente o banco de dados de ações"""
        try:
            if progress_callback:
                progress_callback("Buscando lista de ações da B3...")
            
            # Busca todas as ações brasileiras
            all_stocks = self._fetch_all_brazilian_stocks()
            
            if progress_callback:
                progress_callback(f"Encontradas {len(all_stocks)} ações. Coletando dados detalhados...")
            
            # Coleta dados detalhados de cada ação
            detailed_stocks = self._collect_detailed_data(all_stocks, progress_callback)
            
            # Salva no arquivo
            database = {
                'last_updated': datetime.now().isoformat(),
                'stocks': detailed_stocks,
                'total_stocks': len(detailed_stocks)
            }
            
            self._save_database(database)
            
            if progress_callback:
                progress_callback(f"✅ Base de dados atualizada com {len(detailed_stocks)} ações!")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Erro na atualização: {str(e)}")
            return False
    
    def _fetch_all_brazilian_stocks(self) -> List[str]:
        """Busca lista completa de ações brasileiras"""
        try:
            # Tenta várias fontes para obter lista completa
            stocks = set()
            
            # Método 1: Lista conhecida de ações principais
            major_stocks = [
                'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
                'WEGE3.SA', 'RENT3.SA', 'LREN3.SA', 'MGLU3.SA', 'VBBR3.SA',
                'BTOW3.SA', 'RADL3.SA', 'HAPV3.SA', 'FLRY3.SA', 'KLBN11.SA',
                'SUZB3.SA', 'CMIG4.SA', 'EGIE3.SA', 'TAEE11.SA', 'BRFS3.SA',
                'JBSS3.SA', 'BEEF3.SA', 'MRFG3.SA', 'PCAR3.SA', 'CCRO3.SA',
                'EQTL3.SA', 'MULT3.SA', 'CIEL3.SA', 'AZUL4.SA', 'GOLL4.SA',
                'EMBR3.SA', 'GOAU4.SA', 'USIM5.SA', 'CSNA3.SA', 'GGBR4.SA',
                'SBSP3.SA', 'CPLE6.SA', 'CPFE3.SA', 'ENBR3.SA', 'VIVT3.SA',
                'UGPA3.SA', 'PSSA3.SA', 'LWSA3.SA', 'NTCO3.SA', 'CSAN3.SA',
                'RAIL3.SA', 'RUMO3.SA', 'LOGN3.SA', 'TIMS3.SA', 'TOTS3.SA',
                'B3SA3.SA', 'IRBR3.SA', 'BBSE3.SA', 'SANB11.SA', 'BPAC11.SA',
                'BRML3.SA', 'IGTI11.SA', 'YDUQ3.SA', 'COGN3.SA', 'ANIM3.SA',
                'QUAL3.SA', 'JHSF3.SA', 'CYRELA.SA', 'CYRE3.SA', 'MRVE3.SA',
                'EVEN3.SA', 'GFSA3.SA', 'TCSA3.SA', 'HYPE3.SA', 'PDGR3.SA',
                'ALPA4.SA', 'RECV3.SA', 'DIRR3.SA', 'MDIA3.SA', 'OIBR3.SA',
                'OIBR4.SA', 'TELB4.SA', 'VIVR3.SA', 'CARD3.SA', 'PAGS3.SA',
                'PAYX3.SA', 'STBP3.SA', 'STONE3.SA', 'RDOR3.SA', 'DASA3.SA',
                'ODPV3.SA', 'PARD3.SA', 'GNDI3.SA', 'HAPV3.SA', 'SMTO3.SA',
                'PLPL3.SA', 'HBOR3.SA', 'SLCE3.SA', 'CGAS5.SA', 'LIGT3.SA',
                'NEOE3.SA', 'AESB3.SA', 'COCE5.SA', 'TRPL4.SA', 'ENEV3.SA',
                'PEAB4.SA', 'DXCO3.SA', 'MOVI3.SA', 'CASH3.SA', 'GRND3.SA',
                'SIMH3.SA', 'RRRP3.SA', 'FRAS3.SA', 'SOMA3.SA', 'ALUP11.SA',
                'TAEE3.SA', 'SAPR11.SA', 'TRPL3.SA', 'ENGI11.SA', 'CESP6.SA',
                'ELPL4.SA', 'GEPA4.SA', 'LIPR3.SA', 'RAPT4.SA', 'SAPR4.SA',
                'MEAL3.SA', 'CAML3.SA', 'SMLS3.SA', 'MLAS3.SA', 'POMO4.SA',
                'TIET11.SA', 'TIET3.SA', 'TIET4.SA', 'CPFE3.SA', 'CPLE3.SA',
                'CPLE5.SA', 'EEEL3.SA', 'EEEL4.SA', 'EKTR4.SA', 'ELET3.SA',
                'ELET6.SA', 'EMAE4.SA', 'ENMA3B.SA', 'GPAR3.SA', 'RAPT3.SA'
            ]
            
            stocks.update(major_stocks)
            
            # Método 2: Busca por padrões conhecidos
            patterns = [
                '3.SA', '4.SA', '5.SA', '6.SA', '11.SA'
            ]
            
            # Adiciona algumas ações conhecidas de cada setor
            known_tickers = [
                'AGRO3.SA', 'ALPA4.SA', 'ALSO3.SA', 'AMAR3.SA', 'ANIM3.SA',
                'ARML3.SA', 'ATOM3.SA', 'BAHI3.SA', 'BAUH4.SA', 'BBRK3.SA',
                'BBDC3.SA', 'BBSE3.SA', 'BEES3.SA', 'BEES4.SA', 'BMGB4.SA',
                'BNBR3.SA', 'BPAC11.SA', 'BRAP4.SA', 'BRDT3.SA', 'BRFS3.SA',
                'BRIN3.SA', 'BRIT3.SA', 'BRML3.SA', 'BRPR3.SA', 'BRSR6.SA',
                'BSLI3.SA', 'BTLG11.SA', 'BTOW3.SA', 'CAML3.SA', 'CARD3.SA',
                'CBAV3.SA', 'CCRO3.SA', 'CEAB3.SA', 'CESP6.SA', 'CGAS5.SA',
                'CGRA3.SA', 'CGRA4.SA', 'CIEL3.SA', 'CLSC4.SA', 'CMIG3.SA',
                'COCE5.SA', 'COGN3.SA', 'CPLE3.SA', 'CPLE5.SA', 'CPLE6.SA',
                'CPFE3.SA', 'CSAN3.SA', 'CSNA3.SA', 'CTIP3.SA', 'CVCB3.SA',
                'CYRE3.SA', 'DASA3.SA', 'DESK3.SA', 'DIRR3.SA', 'DMMO3.SA',
                'DXCO3.SA', 'ECOR3.SA', 'EGIE3.SA', 'ELEK3.SA', 'ELET3.SA',
                'ELET6.SA', 'EMBR3.SA', 'ENBR3.SA', 'ENEV3.SA', 'ENGI11.SA',
                'ENGI3.SA', 'ENGI4.SA', 'EQTL3.SA', 'EUCA4.SA', 'EVEN3.SA',
                'EZTC3.SA', 'FESA4.SA', 'FHER3.SA', 'FLRY3.SA', 'FRAS3.SA',
                'GFSA3.SA', 'GGBR3.SA', 'GGBR4.SA', 'GNDI3.SA', 'GOAU3.SA',
                'GOAU4.SA', 'GOLL4.SA', 'GPAR3.SA', 'GRND3.SA', 'HAPV3.SA',
                'HBOR3.SA', 'HYPE3.SA', 'IFCM3.SA', 'IGTI11.SA', 'IGTI3.SA',
                'IRBR3.SA', 'ITSA3.SA', 'ITSA4.SA', 'ITUB3.SA', 'JBSS3.SA',
                'JHSF3.SA', 'KEPL3.SA', 'KLBN11.SA', 'KLBN3.SA', 'KLBN4.SA',
                'LCAM3.SA', 'LIGT3.SA', 'LINX3.SA', 'LJQQ3.SA', 'LLIS3.SA',
                'LOGN3.SA', 'LPSB3.SA', 'LREN3.SA', 'LWSA3.SA', 'MDIA3.SA',
                'MEAL3.SA', 'MILS3.SA', 'MMXM3.SA', 'MOVI3.SA', 'MRFG3.SA',
                'MRVE3.SA', 'MULT3.SA', 'MYPK3.SA', 'NEOE3.SA', 'NTCO3.SA',
                'ODPV3.SA', 'OIBR3.SA', 'OIBR4.SA', 'PARD3.SA', 'PDGR3.SA',
                'PEAB3.SA', 'PEAB4.SA', 'PFRM3.SA', 'PINE4.SA', 'PLAS3.SA',
                'PLPL3.SA', 'POMO3.SA', 'POMO4.SA', 'PSSA3.SA', 'QUAL3.SA',
                'RADL3.SA', 'RAIL3.SA', 'RAPT3.SA', 'RAPT4.SA', 'RDOR3.SA',
                'RECV3.SA', 'RLOG3.SA', 'RNEW11.SA', 'RNEW3.SA', 'RNEW4.SA',
                'ROMI3.SA', 'RRRP3.SA', 'RUMO3.SA', 'SANB11.SA', 'SANB3.SA',
                'SANB4.SA', 'SAPR11.SA', 'SAPR3.SA', 'SAPR4.SA', 'SBSP3.SA',
                'SHOW3.SA', 'SIMH3.SA', 'SLCE3.SA', 'SMLS3.SA', 'SMTO3.SA',
                'SOMA3.SA', 'SQIA3.SA', 'STBP3.SA', 'SULA11.SA', 'SULA3.SA',
                'SULA4.SA', 'SUZB3.SA', 'TAEE11.SA', 'TAEE3.SA', 'TAEE4.SA',
                'TCSA3.SA', 'TGMA3.SA', 'TIET11.SA', 'TIET3.SA', 'TIET4.SA',
                'TIMS3.SA', 'TOTS3.SA', 'TRPL3.SA', 'TRPL4.SA', 'TUPY3.SA',
                'UGPA3.SA', 'UNIP6.SA', 'USIM3.SA', 'USIM5.SA', 'VBBR3.SA',
                'VIVR3.SA', 'VIVT3.SA', 'VIVT4.SA', 'VLID3.SA', 'VULC3.SA',
                'WEGE3.SA', 'YDUQ3.SA', 'ZAMP3.SA'
            ]
            
            stocks.update(known_tickers)
            
            return list(stocks)
            
        except Exception as e:
            print(f"Erro ao buscar ações: {e}")
            return []
    
    def _collect_detailed_data(self, tickers: List[str], progress_callback=None) -> Dict[str, Dict]:
        """Coleta dados detalhados de cada ação"""
        detailed_stocks = {}
        total = len(tickers)
        completed = 0
        
        def process_ticker(ticker):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Extrai informações básicas
                name = info.get('shortName', info.get('longName', ticker.replace('.SA', '').upper()))
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                
                # Gera link para dados de mercado
                ticker_code = ticker.replace('.SA', '').lower()
                link = f"https://www.dadosdemercado.com.br/acoes/{ticker_code}"
                
                # Tenta obter ISIN (pode não estar disponível)
                isin = info.get('isin', f'BR{ticker.replace(".SA", "").upper()}')
                
                return ticker, {
                    'name': name,
                    'sector': sector,
                    'industry': industry,
                    'isin': isin,
                    'link': link,
                    'currency': info.get('currency', 'BRL'),
                    'exchange': info.get('exchange', 'SAO'),
                    'market_cap': info.get('marketCap', 0),
                    'country': info.get('country', 'Brazil')
                }
            except Exception as e:
                print(f"Erro ao processar {ticker}: {e}")
                return ticker, None
        
        # Processa em lotes para evitar timeout
        batch_size = 10
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(process_ticker, ticker) for ticker in batch]
                
                for future in as_completed(futures):
                    ticker, data = future.result()
                    completed += 1
                    
                    if data:
                        detailed_stocks[ticker] = data
                    
                    if progress_callback and completed % 10 == 0:
                        progress_callback(f"Processando... {completed}/{total} ações")
            
            # Pausa entre lotes para evitar rate limiting
            time.sleep(1)
        
        return detailed_stocks
    
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
        """Retorna ações básicas em caso de erro"""
        return {
            'PETR4.SA': {
                'name': 'Petrobras',
                'sector': 'Energy',
                'industry': 'Oil & Gas',
                'isin': 'BRPETRACNPR6',
                'link': 'https://www.dadosdemercado.com.br/acoes/petr4'
            },
            'VALE3.SA': {
                'name': 'Vale',
                'sector': 'Materials',
                'industry': 'Mining',
                'isin': 'BRVALEACNOR0',
                'link': 'https://www.dadosdemercado.com.br/acoes/vale3'
            },
            'ITUB4.SA': {
                'name': 'Itaú Unibanco',
                'sector': 'Financial Services',
                'industry': 'Banks',
                'isin': 'BRITUBALCTB2',
                'link': 'https://www.dadosdemercado.com.br/acoes/itub4'
            }
        }
    
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
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        'total_stocks': len(data.get('stocks', {})),
                        'total_sectors': len(self.get_sectors()),
                        'last_updated': data.get('last_updated', 'N/A'),
                        'cache_valid': self._is_cache_valid(data.get('last_updated'))
                    }
        except:
            pass
        
        return {
            'total_stocks': 0,
            'total_sectors': 0,
            'last_updated': 'N/A',
            'cache_valid': False
        }

# Instância global
stock_db = StockDatabase()