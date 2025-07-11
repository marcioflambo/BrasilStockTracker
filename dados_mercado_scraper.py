"""
Scraper para extrair lista completa de ações do site dadosdemercado.com.br
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
import streamlit as st
from datetime import datetime


class DadosMercadoScraper:
    """Extrai dados completos de ações do site dadosdemercado.com.br"""
    
    def __init__(self):
        self.base_url = "https://www.dadosdemercado.com.br"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_all_stocks_from_site(self) -> Dict[str, Dict]:
        """
        Extrai todas as ações disponíveis no site dadosdemercado.com.br
        Retorna dict com informações completas de cada ação
        """
        try:
            stocks = {}
            
            # Página principal de ações
            url = f"{self.base_url}/acoes"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procura por links de ações (padrão: /acoes/TICKER)
            stock_links = soup.find_all('a', href=re.compile(r'/acoes/[a-zA-Z0-9]+$'))
            
            for link in stock_links:
                href = link.get('href')
                if href and '/acoes/' in href:
                    ticker_code = href.split('/acoes/')[-1].upper()
                    ticker_sa = f"{ticker_code}.SA"
                    
                    # Extrai nome da empresa do link
                    company_name = link.get_text(strip=True)
                    if not company_name:
                        company_name = ticker_code
                    
                    # URL completa para a ação
                    stock_url = f"{self.base_url}{href}"
                    
                    stocks[ticker_sa] = {
                        'name': company_name,
                        'ticker_code': ticker_code,
                        'url': stock_url,
                        'sector': 'N/A',  # Será preenchido depois
                        'industry': 'N/A',
                        'isin': f'BR{ticker_code}',
                        'currency': 'BRL',
                        'exchange': 'B3',
                        'country': 'Brazil'
                    }
            
            # Se não encontrou ações pelo método acima, tenta método alternativo
            if not stocks:
                stocks = self._extract_from_stock_table(soup)
            
            # Se ainda não encontrou, usa lista conhecida
            if not stocks:
                stocks = self._get_comprehensive_stock_list()
            
            return stocks
            
        except Exception as e:
            st.error(f"Erro ao extrair dados do site: {e}")
            return self._get_comprehensive_stock_list()
    
    def _extract_from_stock_table(self, soup) -> Dict[str, Dict]:
        """Extrai ações de tabelas ou listas no site"""
        stocks = {}
        
        # Procura por tabelas com dados de ações
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Procura por padrão de ticker (4 letras + número)
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        if re.match(r'^[A-Z]{4}\d{1,2}$', text):
                            ticker_sa = f"{text}.SA"
                            # Próxima célula pode ser o nome
                            next_cell = cells[cells.index(cell) + 1] if cells.index(cell) + 1 < len(cells) else None
                            name = next_cell.get_text(strip=True) if next_cell else text
                            
                            stocks[ticker_sa] = {
                                'name': name,
                                'ticker_code': text,
                                'url': f"{self.base_url}/acoes/{text.lower()}",
                                'sector': 'N/A',
                                'industry': 'N/A',
                                'isin': f'BR{text}',
                                'currency': 'BRL',
                                'exchange': 'B3',
                                'country': 'Brazil'
                            }
        
        return stocks
    
    def _get_minimal_fallback(self) -> Dict[str, Dict]:
        """Retorna apenas algumas ações básicas como fallback absoluto"""
        return {
            'PETR4.SA': {
                'name': 'Petrobras',
                'sector': 'Energy',
                'industry': 'Oil & Gas',
                'isin': 'BRPETRACNPR6',
                'ticker_code': 'PETR4',
                'currency': 'BRL',
                'exchange': 'B3',
                'country': 'Brazil',
                'url': 'https://www.dadosdemercado.com.br/acoes/petr4'
            },
            'VALE3.SA': {
                'name': 'Vale',
                'sector': 'Materials',
                'industry': 'Mining',
                'isin': 'BRVALEACNOR0',
                'ticker_code': 'VALE3',
                'currency': 'BRL',
                'exchange': 'B3',
                'country': 'Brazil',
                'url': 'https://www.dadosdemercado.com.br/acoes/vale3'
            },
            'ITUB4.SA': {
                'name': 'Itaú Unibanco',
                'sector': 'Financial Services',
                'industry': 'Banks',
                'isin': 'BRITUBALCTB2',
                'ticker_code': 'ITUB4',
                'currency': 'BRL',
                'exchange': 'B3',
                'country': 'Brazil',
                'url': 'https://www.dadosdemercado.com.br/acoes/itub4'
            }
        }
    
    def get_stock_details(self, ticker_code: str) -> Optional[Dict]:
        """
        Busca detalhes específicos de uma ação no site
        """
        try:
            url = f"{self.base_url}/acoes/{ticker_code.lower()}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair informações específicas da página
            details = {
                'url': url,
                'ticker_code': ticker_code.upper(),
                'name': 'N/A',
                'sector': 'N/A',
                'industry': 'N/A',
                'isin': f'BR{ticker_code.upper()}'
            }
            
            # Buscar nome da empresa
            title_tags = soup.find_all(['h1', 'h2', 'title'])
            for tag in title_tags:
                text = tag.get_text(strip=True)
                if ticker_code.upper() in text or 'ações' in text.lower():
                    details['name'] = text.split(' - ')[0] if ' - ' in text else text
                    break
            
            # Buscar setor/indústria
            setor_patterns = ['setor', 'segmento', 'industria', 'industry']
            for pattern in setor_patterns:
                elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
                for element in elements:
                    parent = element.parent
                    if parent:
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            sector_text = next_sibling.get_text(strip=True)
                            if len(sector_text) > 3 and len(sector_text) < 50:
                                details['sector'] = sector_text
                                break
            
            return details
            
        except Exception as e:
            print(f"Erro ao buscar detalhes de {ticker_code}: {e}")
            return None

# Instância global do scraper
dados_mercado_scraper = DadosMercadoScraper()