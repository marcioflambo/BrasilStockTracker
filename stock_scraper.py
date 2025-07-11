"""
Web scraper para obter lista dinâmica de ações brasileiras
"""

import trafilatura
import re
import requests
from typing import Dict, List, Tuple
import streamlit as st
import time
import json
import os

class StockScraper:
    """Scraper para obter dados dinâmicos de ações brasileiras"""
    
    def __init__(self):
        self.cache_file = "stocks_cache.json"
        self.cache_duration = 3600  # 1 hora em segundos
        
    def get_stocks_from_dadosdemercado(self) -> Dict[str, Dict]:
        """
        Obtém lista de ações do dadosdemercado.com.br
        Retorna dict com estrutura: {ticker: {name: str, sector: str}}
        """
        
        # Verificar cache primeiro
        cached_data = self._load_cache()
        if cached_data:
            return cached_data
            
        try:
            # URL da página de ações
            url = "https://www.dadosdemercado.com.br/acoes"
            
            # Fazer requisição
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                st.warning("Não foi possível acessar o site. Usando dados em cache.")
                return self._get_fallback_stocks()
                
            # Extrair texto
            text = trafilatura.extract(downloaded)
            if not text:
                return self._get_fallback_stocks()
                
            # Processar o texto para extrair informações das ações
            stocks = self._parse_stocks_from_text(text)
            
            if stocks:
                # Salvar cache
                self._save_cache(stocks)
                return stocks
            else:
                return self._get_fallback_stocks()
                
        except Exception as e:
            st.error(f"Erro ao obter dados: {str(e)}")
            return self._get_fallback_stocks()
    
    def _parse_stocks_from_text(self, text: str) -> Dict[str, Dict]:
        """Parse do texto extraído para obter informações das ações"""
        stocks = {}
        
        # Padrões para encontrar códigos de ações (formato: ABCD3, ABCD4, ABCD11, etc.)
        ticker_pattern = r'\b([A-Z]{4}[0-9]{1,2})\b'
        
        # Encontrar todos os tickers
        tickers = re.findall(ticker_pattern, text)
        
        # Lista conhecida de ações brasileiras para validação
        known_stocks = {
            'ABEV3': {'name': 'Ambev', 'sector': 'Bebidas'},
            'AZUL4': {'name': 'Azul', 'sector': 'Aviação'},
            'B3SA3': {'name': 'B3', 'sector': 'Serviços Financeiros'},
            'BBAS3': {'name': 'Banco do Brasil', 'sector': 'Bancos'},
            'BBDC3': {'name': 'Bradesco ON', 'sector': 'Bancos'},
            'BBDC4': {'name': 'Bradesco', 'sector': 'Bancos'},
            'BBSE3': {'name': 'BB Seguridade', 'sector': 'Seguros'},
            'BEEF3': {'name': 'Minerva', 'sector': 'Alimentos'},
            'BPAC11': {'name': 'BTG Pactual', 'sector': 'Bancos'},
            'BRAP4': {'name': 'Bradespar', 'sector': 'Holdings'},
            'BRFS3': {'name': 'BRF', 'sector': 'Alimentos'},
            'BRKM5': {'name': 'Braskem', 'sector': 'Petroquímicos'},
            'CASH3': {'name': 'Méliuz', 'sector': 'Tecnologia'},
            'CCRO3': {'name': 'CCR', 'sector': 'Concessões'},
            'CIEL3': {'name': 'Cielo', 'sector': 'Serviços Financeiros'},
            'CMIG4': {'name': 'Cemig', 'sector': 'Energia Elétrica'},
            'COGN3': {'name': 'Cogna', 'sector': 'Educação'},
            'CPFE3': {'name': 'CPFL Energia', 'sector': 'Energia Elétrica'},
            'CPLE6': {'name': 'Copel', 'sector': 'Energia Elétrica'},
            'CRFB3': {'name': 'Carrefour Brasil', 'sector': 'Varejo'},
            'CSAN3': {'name': 'Cosan', 'sector': 'Energia'},
            'CSNA3': {'name': 'CSN', 'sector': 'Siderurgia'},
            'CYRE3': {'name': 'Cyrela', 'sector': 'Construção'},
            'DXCO3': {'name': 'Dexco', 'sector': 'Materiais de Construção'},
            'ECOR3': {'name': 'EcoRodovias', 'sector': 'Concessões'},
            'EGIE3': {'name': 'Engie Brasil', 'sector': 'Energia Elétrica'},
            'ELET3': {'name': 'Eletrobras', 'sector': 'Energia Elétrica'},
            'ELET6': {'name': 'Eletrobras PNB', 'sector': 'Energia Elétrica'},
            'EMBR3': {'name': 'Embraer', 'sector': 'Aeroespacial'},
            'ENBR3': {'name': 'EDP Brasil', 'sector': 'Energia Elétrica'},
            'ENEV3': {'name': 'Eneva', 'sector': 'Energia'},
            'EQTL3': {'name': 'Equatorial', 'sector': 'Energia Elétrica'},
            'EZTC3': {'name': 'EZTec', 'sector': 'Construção'},
            'FLRY3': {'name': 'Fleury', 'sector': 'Saúde'},
            'GGBR4': {'name': 'Gerdau', 'sector': 'Siderurgia'},
            'GNDI3': {'name': 'Notre Dame', 'sector': 'Saúde'},
            'GOAU4': {'name': 'Gerdau Met', 'sector': 'Siderurgia'},
            'GOLL4': {'name': 'Gol', 'sector': 'Aviação'},
            'HAPV3': {'name': 'Hapvida', 'sector': 'Saúde'},
            'HYPE3': {'name': 'Hypera', 'sector': 'Farmacêutico'},
            'IGTI11': {'name': 'Iguatemi', 'sector': 'Shopping Centers'},
            'IRBR3': {'name': 'IRB Brasil', 'sector': 'Seguros'},
            'ITSA4': {'name': 'Itaúsa', 'sector': 'Holdings'},
            'ITUB4': {'name': 'Itaú Unibanco', 'sector': 'Bancos'},
            'JBSS3': {'name': 'JBS', 'sector': 'Alimentos'},
            'JHSF3': {'name': 'JHSF', 'sector': 'Construção'},
            'KLBN11': {'name': 'Klabin', 'sector': 'Papel e Celulose'},
            'LAME4': {'name': 'Lojas Americanas', 'sector': 'Varejo'},
            'LCAM3': {'name': 'Locamerica', 'sector': 'Aluguel de Carros'},
            'LREN3': {'name': 'Lojas Renner', 'sector': 'Varejo'},
            'LWSA3': {'name': 'Locaweb', 'sector': 'Tecnologia'},
            'MGLU3': {'name': 'Magazine Luiza', 'sector': 'Varejo'},
            'MRFG3': {'name': 'Marfrig', 'sector': 'Alimentos'},
            'MRVE3': {'name': 'MRV', 'sector': 'Construção'},
            'MULT3': {'name': 'Multiplan', 'sector': 'Shopping Centers'},
            'NTCO3': {'name': 'Natura', 'sector': 'Cosméticos'},
            'PCAR3': {'name': 'P.Açúcar-CBD', 'sector': 'Varejo'},
            'PETR3': {'name': 'Petrobras ON', 'sector': 'Petróleo e Gás'},
            'PETR4': {'name': 'Petrobras', 'sector': 'Petróleo e Gás'},
            'PETZ3': {'name': 'Petz', 'sector': 'Pet Shop'},
            'POSI3': {'name': 'Positivo', 'sector': 'Tecnologia'},
            'PRIO3': {'name': 'PetroRio', 'sector': 'Petróleo e Gás'},
            'QUAL3': {'name': 'Qualicorp', 'sector': 'Saúde'},
            'RADL3': {'name': 'Raia Drogasil', 'sector': 'Farmácias'},
            'RAIL3': {'name': 'Rumo', 'sector': 'Logística'},
            'RDOR3': {'name': 'Rede D\'Or', 'sector': 'Saúde'},
            'RECV3': {'name': 'Petro Rec', 'sector': 'Petróleo e Gás'},
            'RENT3': {'name': 'Localiza', 'sector': 'Aluguel de Carros'},
            'RRRP3': {'name': '3R Petroleum', 'sector': 'Petróleo e Gás'},
            'SANB11': {'name': 'Santander Brasil', 'sector': 'Bancos'},
            'SBSP3': {'name': 'Sabesp', 'sector': 'Saneamento'},
            'SLCE3': {'name': 'SLC Agrícola', 'sector': 'Agronegócio'},
            'SMTO3': {'name': 'São Martinho', 'sector': 'Açúcar e Álcool'},
            'SOMA3': {'name': 'Grupo Soma', 'sector': 'Varejo'},
            'SUZB3': {'name': 'Suzano', 'sector': 'Papel e Celulose'},
            'TAEE11': {'name': 'Taesa', 'sector': 'Transmissão de Energia'},
            'TIMS3': {'name': 'TIM', 'sector': 'Telecomunicações'},
            'TOTS3': {'name': 'Totvs', 'sector': 'Tecnologia'},
            'UGPA3': {'name': 'Ultrapar', 'sector': 'Combustíveis'},
            'USIM5': {'name': 'Usiminas', 'sector': 'Siderurgia'},
            'VALE3': {'name': 'Vale', 'sector': 'Mineração'},
            'VBBR3': {'name': 'Vibra', 'sector': 'Combustíveis'},
            'VIIA3': {'name': 'Via', 'sector': 'Varejo'},
            'VIVT3': {'name': 'Telefônica Brasil', 'sector': 'Telecomunicações'},
            'WEGE3': {'name': 'WEG', 'sector': 'Máquinas e Equipamentos'},
            'YDUQ3': {'name': 'Yduqs', 'sector': 'Educação'}
        }
        
        # Processar tickers encontrados
        for ticker in set(tickers):
            ticker_sa = f"{ticker}.SA"
            
            if ticker in known_stocks:
                stocks[ticker_sa] = known_stocks[ticker]
            else:
                # Para tickers não conhecidos, tentar inferir informações básicas
                stocks[ticker_sa] = {
                    'name': ticker,
                    'sector': 'Diversos'
                }
        
        return stocks
    
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
    
    def _get_fallback_stocks(self) -> Dict[str, Dict]:
        """Retorna lista básica de ações como fallback"""
        return {
            'ITUB4.SA': {'name': 'Itaú Unibanco', 'sector': 'Bancos'},
            'PETR4.SA': {'name': 'Petrobras', 'sector': 'Petróleo e Gás'},
            'VALE3.SA': {'name': 'Vale', 'sector': 'Mineração'},
            'BBDC4.SA': {'name': 'Bradesco', 'sector': 'Bancos'},
            'ABEV3.SA': {'name': 'Ambev', 'sector': 'Bebidas'},
            'MGLU3.SA': {'name': 'Magazine Luiza', 'sector': 'Varejo'},
            'ELET3.SA': {'name': 'Eletrobras', 'sector': 'Energia Elétrica'},
            'JBSS3.SA': {'name': 'JBS', 'sector': 'Alimentos'},
            'SUZB3.SA': {'name': 'Suzano', 'sector': 'Papel e Celulose'},
            'VIVT3.SA': {'name': 'Telefônica Brasil', 'sector': 'Telecomunicações'},
            'BRFS3.SA': {'name': 'BRF', 'sector': 'Alimentos'},
            'CSNA3.SA': {'name': 'CSN', 'sector': 'Siderurgia'},
            'LREN3.SA': {'name': 'Lojas Renner', 'sector': 'Varejo'},
            'RAIL3.SA': {'name': 'Rumo', 'sector': 'Logística'},
            'USIM5.SA': {'name': 'Usiminas', 'sector': 'Siderurgia'},
            'GGBR4.SA': {'name': 'Gerdau', 'sector': 'Siderurgia'},
            'CPFE3.SA': {'name': 'CPFL Energia', 'sector': 'Energia Elétrica'},
            'MRVE3.SA': {'name': 'MRV', 'sector': 'Construção'},
            'TOTS3.SA': {'name': 'Totvs', 'sector': 'Tecnologia'},
            'RDOR3.SA': {'name': 'Rede D\'Or', 'sector': 'Saúde'}
        }

def get_dynamic_stocks():
    """Função principal para obter ações dinâmicas"""
    scraper = StockScraper()
    return scraper.get_stocks_from_dadosdemercado()