import yfinance as yf
import pandas as pd
import time
from typing import List, Dict, Any
# Função será importada dinamicamente pelo app principal

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
        
        # Calcular métricas (incluindo metodologia Barsi)
        dividend_per_share = self._get_dividend_per_share(stock)
        data = {
            'Ticker': ticker,
            'Nome': info.get('longName', ticker.replace('.SA', '')),
            'Preço Atual': self._get_current_price(stock, hist),
            'Variação (%)': self._get_price_change(hist),
            'DY Atual (%)': self._get_dividend_yield(info),
            'DY Médio 5a (%)': self._get_avg_dividend_yield(stock),
            'Div/Ação (R$)': dividend_per_share,
            'Paga Dividendos': 'Sim' if dividend_per_share != 'N/A' and dividend_per_share > 0 else 'Não',
            'P/L': self._get_pe_ratio(info),
            'P/VP': self._get_pb_ratio(info),
            'ROE (%)': self._get_roe(info),
            'Dívida/PL': self._get_debt_to_equity(info, balance_sheet),
            'Margem Líq. (%)': self._get_profit_margin(info, financials),
            'Valor de Mercado': self._get_market_cap(info),
            'Setor': info.get('sector', 'N/A'),
            'Critério Barsi': self._evaluate_barsi_criteria(info, dividend_per_share, self._get_pe_ratio(info), self._get_roe(info))
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
    
    def _get_dividend_per_share(self, stock) -> float:
        """Obtém dividendo por ação dos últimos 12 meses"""
        try:
            dividends = stock.dividends
            if not dividends.empty:
                # Últimos 12 meses
                one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)
                recent_dividends = dividends[dividends.index > one_year_ago]
                if not recent_dividends.empty:
                    return float(recent_dividends.sum())
        except:
            pass
        return 'N/A'
    
    def _get_roe(self, info) -> float:
        """Obtém Return on Equity (ROE)"""
        try:
            roe = info.get('returnOnEquity')
            if roe:
                return float(roe * 100)  # Converter para percentual
        except:
            pass
        return 'N/A'
    
    def _get_debt_to_equity(self, info, balance_sheet) -> float:
        """Obtém a relação Dívida/Patrimônio Líquido"""
        try:
            debt_to_equity = info.get('debtToEquity')
            if debt_to_equity:
                return float(debt_to_equity)
        except:
            pass
        return 'N/A'
    
    def _evaluate_barsi_criteria(self, info, dividend_per_share, pe_ratio, roe) -> str:
        """Avalia se a ação atende aos critérios da metodologia Barsi"""
        criteria_met = 0
        total_criteria = 0
        
        # Critério 1: Paga dividendos consistentemente
        if dividend_per_share != 'N/A' and dividend_per_share > 0:
            criteria_met += 1
        total_criteria += 1
        
        # Critério 2: P/L entre 3 e 15
        if pe_ratio != 'N/A' and 3 <= pe_ratio <= 15:
            criteria_met += 1
        total_criteria += 1
        
        # Critério 3: ROE > 15%
        if roe != 'N/A' and roe > 15:
            criteria_met += 1
        total_criteria += 1
        
        # Critério 4: Empresa consolidada (valor de mercado > 1 bilhão)
        market_cap = info.get('marketCap', 0)
        if market_cap and market_cap > 1_000_000_000:
            criteria_met += 1
        total_criteria += 1
        
        percentage = (criteria_met / total_criteria) * 100
        
        if percentage >= 75:
            return f"✅ Excelente ({criteria_met}/{total_criteria})"
        elif percentage >= 50:
            return f"⚠️ Boa ({criteria_met}/{total_criteria})"
        else:
            return f"❌ Não atende ({criteria_met}/{total_criteria})"
    
    def _create_error_row(self, ticker: str) -> Dict[str, Any]:
        """Cria uma linha com dados N/A para ações com erro"""
        return {
            'Ticker': ticker,
            'Nome': 'N/A',
            'Preço Atual': 'N/A',
            'Variação (%)': 'N/A',
            'DY Atual (%)': 'N/A',
            'DY Médio 5a (%)': 'N/A',
            'Div/Ação (R$)': 'N/A',
            'Paga Dividendos': 'N/A',
            'P/L': 'N/A',
            'P/VP': 'N/A',
            'ROE (%)': 'N/A',
            'Dívida/PL': 'N/A',
            'Margem Líq. (%)': 'N/A',
            'Valor de Mercado': 'N/A',
            'Setor': 'N/A',
            'Critério Barsi': 'N/A'
        }
