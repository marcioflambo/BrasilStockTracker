import yfinance as yf
import pandas as pd
import time
from typing import List, Dict, Any

class StockDataManager:
    """Gerenciador de dados de ações brasileiras"""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 30  # segundos
    
    def get_stock_data(self, tickers: List[str]) -> pd.DataFrame:
        """
        Obtém dados completos das ações especificadas
        
        Args:
            tickers: Lista de códigos das ações (ex: ['ITUB4.SA', 'PETR4.SA'])
            
        Returns:
            DataFrame com dados das ações
        """
        data_list = []
        
        for ticker in tickers:
            try:
                stock_data = self._get_single_stock_data(ticker)
                data_list.append(stock_data)
            except Exception as e:
                print(f"Erro ao obter dados para {ticker}: {str(e)}")
                # Adicionar linha com dados N/A em caso de erro
                error_data = self._create_error_row(ticker)
                data_list.append(error_data)
        
        df = pd.DataFrame(data_list)
        return df
    
    def _get_single_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Obtém dados de uma única ação"""
        
        # Verificar cache
        current_time = time.time()
        if (ticker in self.cache and 
            ticker in self.cache_expiry and 
            current_time < self.cache_expiry[ticker]):
            return self.cache[ticker]
        
        # Obter dados do Yahoo Finance
        stock = yf.Ticker(ticker)
        
        # Informações básicas
        info = stock.info
        
        # Histórico para calcular variação
        hist = stock.history(period="2d")
        
        # Dados financeiros
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        # Calcular métricas
        data = {
            'Ticker': ticker,
            'Nome': info.get('longName', ticker.replace('.SA', '')),
            'Preço Atual': self._get_current_price(stock, hist),
            'Variação (%)': self._get_price_change(hist),
            'DY Atual (%)': self._get_dividend_yield(info),
            'DY Médio 5a (%)': self._get_avg_dividend_yield(stock),
            'P/L': self._get_pe_ratio(info),
            'P/VP': self._get_pb_ratio(info),
            'Margem Líq. (%)': self._get_profit_margin(info, financials),
            'Valor de Mercado': self._get_market_cap(info),
            'Setor': info.get('sector', 'N/A')
        }
        
        # Atualizar cache
        self.cache[ticker] = data
        self.cache_expiry[ticker] = current_time + self.cache_duration
        
        return data
    
    def _get_current_price(self, stock, hist) -> float:
        """Obtém o preço atual da ação"""
        try:
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            else:
                # Fallback para info se histórico não disponível
                info = stock.info
                price = info.get('currentPrice') or info.get('regularMarketPrice')
                return float(price) if price else 'N/A'
        except:
            return 'N/A'
    
    def _get_price_change(self, hist) -> float:
        """Calcula a variação percentual do preço"""
        try:
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                change = ((current_price - previous_price) / previous_price) * 100
                return float(change)
        except:
            pass
        return 'N/A'
    
    def _get_dividend_yield(self, info) -> float:
        """Obtém o dividend yield atual"""
        try:
            dy = info.get('dividendYield')
            if dy:
                return float(dy * 100)  # Converter para percentual
        except:
            pass
        return 'N/A'
    
    def _get_avg_dividend_yield(self, stock) -> float:
        """Calcula o dividend yield médio dos últimos 5 anos"""
        try:
            # Obter histórico de dividendos
            dividends = stock.dividends
            if not dividends.empty:
                # Filtrar últimos 5 anos
                five_years_ago = pd.Timestamp.now() - pd.DateOffset(years=5)
                recent_dividends = dividends[dividends.index >= five_years_ago]
                
                if not recent_dividends.empty:
                    # Calcular yield médio baseado nos dividendos anuais
                    annual_dividend = recent_dividends.groupby(recent_dividends.index.year).sum()
                    
                    # Obter preços históricos para calcular yield
                    hist = stock.history(period="5y")
                    if not hist.empty:
                        avg_price = hist['Close'].mean()
                        avg_dividend = annual_dividend.mean()
                        avg_yield = (avg_dividend / avg_price) * 100
                        return float(avg_yield)
        except:
            pass
        return 'N/A'
    
    def _get_pe_ratio(self, info) -> float:
        """Obtém a relação Preço/Lucro"""
        try:
            pe = info.get('trailingPE') or info.get('forwardPE')
            return float(pe) if pe else 'N/A'
        except:
            return 'N/A'
    
    def _get_pb_ratio(self, info) -> float:
        """Obtém a relação Preço/Valor Patrimonial"""
        try:
            pb = info.get('priceToBook')
            return float(pb) if pb else 'N/A'
        except:
            return 'N/A'
    
    def _get_profit_margin(self, info, financials) -> float:
        """Obtém a margem líquida"""
        try:
            margin = info.get('profitMargins')
            if margin:
                return float(margin * 100)  # Converter para percentual
        except:
            pass
        return 'N/A'
    
    def _get_market_cap(self, info) -> float:
        """Obtém o valor de mercado"""
        try:
            market_cap = info.get('marketCap')
            return float(market_cap) if market_cap else 'N/A'
        except:
            return 'N/A'
    
    def _create_error_row(self, ticker: str) -> Dict[str, Any]:
        """Cria uma linha com dados N/A para ações com erro"""
        return {
            'Ticker': ticker,
            'Nome': 'N/A',
            'Preço Atual': 'N/A',
            'Variação (%)': 'N/A',
            'DY Atual (%)': 'N/A',
            'DY Médio 5a (%)': 'N/A',
            'P/L': 'N/A',
            'P/VP': 'N/A',
            'Margem Líq. (%)': 'N/A',
            'Valor de Mercado': 'N/A',
            'Setor': 'N/A'
        }
